#!/usr/bin/env python3
"""
MedAI Academic Writing — Literature API Client
Multi-source literature search: arXiv, Semantic Scholar, CrossRef, OpenAlex.
Returns deduplicated, ranked, and optionally filtered paper metadata.
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import difflib
from pathlib import Path
from typing import Any, Dict, List, Optional


ARXIV_API = "http://export.arxiv.org/api/query"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"
CROSSREF_API = "https://api.crossref.org/works"
OPENALEX_API = "https://api.openalex.org/works"

ARXIV_NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

MAX_PER_SOURCE = 2000
PAGE_DELAY = 1.0

DOMAIN_PROFILES: Dict[str, Dict[str, float]] = {
    'general': {
        'citation_weight': 1.0,
        'recency_weight': 1.0,
        'recency_max': 5.0,
        'recency_decay_per_year': 0.5,
        'open_access_bonus': 0.25,
    },
    'fast-moving-ml': {
        'citation_weight': 0.6,
        'recency_weight': 2.0,
        'recency_max': 8.0,
        'recency_decay_per_year': 0.35,
        'open_access_bonus': 0.5,
    },
    'theory': {
        'citation_weight': 1.35,
        'recency_weight': 0.65,
        'recency_max': 3.0,
        'recency_decay_per_year': 0.25,
        'open_access_bonus': 0.0,
    },
    'biomedical': {
        'citation_weight': 1.1,
        'recency_weight': 1.15,
        'recency_max': 5.5,
        'recency_decay_per_year': 0.4,
        'open_access_bonus': 0.4,
    },
}


@dataclass(frozen=True)
class APIConfig:
    semantic_scholar_api_key: str
    crossref_email: str


def _load_env_file() -> None:
    """Load a local .env file if present (non-destructive)."""
    env_path = Path('.env')
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_api_config() -> APIConfig:
    """Load API-related settings from environment variables."""
    _load_env_file()
    return APIConfig(
        semantic_scholar_api_key=os.getenv('SEMANTIC_SCHOLAR_API_KEY', '').strip(),
        crossref_email=os.getenv('CROSSREF_EMAIL', '').strip(),
    )


def _request_json(url: str, headers: Dict[str, str], timeout: int = 30) -> Dict[str, Any]:
    """Perform GET request and decode JSON with basic retry/backoff."""
    delays = [0.0, 1.5, 3.0]
    last_error: Optional[Exception] = None
    for delay in delays:
        if delay > 0:
            time.sleep(delay)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as err:  # pragma: no cover - network failure path
            last_error = err
    raise RuntimeError(f"request failed for {url}: {last_error}")


def _request_text(url: str, headers: Dict[str, str], timeout: int = 30) -> str:
    """Perform GET request and decode UTF-8 text with retry/backoff."""
    delays = [0.0, 1.5, 3.0]
    last_error: Optional[Exception] = None
    for delay in delays:
        if delay > 0:
            time.sleep(delay)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8')
        except Exception as err:  # pragma: no cover - network failure path
            last_error = err
    raise RuntimeError(f"request failed for {url}: {last_error}")


def _parse_arxiv_entry(entry) -> Dict[str, Any]:
    """Parse a single arXiv Atom entry element into a paper dict."""
    paper: Dict[str, Any] = {
        'title': ' '.join((entry.find('atom:title', ARXIV_NS).text or '').split()),
        'summary': (entry.find('atom:summary', ARXIV_NS).text or '').strip(),
        'published': entry.find('atom:published', ARXIV_NS).text or '',
        'arxiv_id': entry.find('atom:id', ARXIV_NS).text or '',
        'authors': [],
        'categories': [],
        'source': 'arxiv',
    }
    paper['year'] = _extract_year(paper['published'])
    for author in entry.findall('atom:author', ARXIV_NS):
        name = author.find('atom:name', ARXIV_NS)
        if name is not None and name.text:
            paper['authors'].append(name.text)
    for cat in entry.findall('atom:category', ARXIV_NS):
        term = cat.get('term', '')
        if term:
            paper['categories'].append(term)
    for link in entry.findall('atom:link', ARXIV_NS):
        if link.get('title') == 'doi':
            paper['doi'] = link.get('href', '').replace('http://dx.doi.org/', '')
    return paper


def _build_ss_paper(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': item.get('title', ''),
        'year': item.get('year', ''),
        'abstract': item.get('abstract', ''),
        'citation_count': item.get('citationCount', 0),
        'authors': [a.get('name', '') for a in item.get('authors', [])],
        'external_ids': item.get('externalIds', {}),
        'venue': item.get('publicationVenue', {}).get('name', ''),
        'source': 'semantic_scholar',
    }


def _build_cr_paper(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': ' '.join(item.get('title', [''])),
        'doi': item.get('DOI', ''),
        'authors': [a.get('family', '') for a in item.get('author', []) if a.get('family')],
        'abstract': item.get('abstract', ''),
        'journal': item.get('container-title', [''])[0] if item.get('container-title') else '',
        'volume': item.get('volume', ''),
        'pages': item.get('page', ''),
        'year': _crossref_year(item),
        'source': 'crossref',
    }


def _build_oa_paper(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': item.get('title', ''),
        'doi': item.get('doi', ''),
        'cited_by_count': item.get('cited_by_count', 0),
        'authors': [a.get('author', {}).get('display_name', '') for a in item.get('authorships', [])],
        'open_access': item.get('open_access', {}).get('is_oa', False),
        'concepts': [c.get('display_name', '') for c in item.get('concepts', [])[:5]],
        'year': item.get('publication_year', ''),
        'source': 'openalex',
    }


def _normalize_title(text: str) -> str:
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', (text or '').lower())
    return ' '.join(normalized.split())


def _extract_year(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r'\b(19|20)\d{2}\b', value)
        if match:
            return int(match.group(0))
    return None


def _citation_metric(paper: Dict[str, Any]) -> int:
    for key in ('citation_count', 'cited_by_count'):
        value = paper.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return 0


def _crossref_year(item: Dict[str, Any]) -> Optional[int]:
    """Resolve CrossRef year with fallback order across common date fields."""
    for field in ('published-print', 'published-online', 'issued'):
        date_parts = item.get(field, {}).get('date-parts', [])
        if date_parts and isinstance(date_parts[0], list) and date_parts[0]:
            year = date_parts[0][0]
            if isinstance(year, int):
                return year
            if isinstance(year, str) and year.isdigit():
                return int(year)
    return None


def infer_domain_from_query(query: str) -> str:
    """Infer a ranking profile from the query when domain=auto."""
    normalized = (query or '').lower()
    tokens = set(re.findall(r'[a-z0-9]+', normalized))
    if {'protein', 'clinical', 'genome', 'biomedical'} & tokens:
        return 'biomedical'
    if {'medicine', 'medical'} & tokens:
        return 'biomedical'
    if {'proof', 'theorem', 'theoretical', 'complexity', 'bound', 'bounds'} & tokens:
        return 'theory'
    if {'transformer', 'llm', 'diffusion', 'benchmark'} & tokens:
        return 'fast-moving-ml'
    if 'language' in tokens and 'model' in tokens:
        return 'fast-moving-ml'
    if 'multi' in tokens and 'agent' in tokens:
        return 'fast-moving-ml'
    return 'general'


def _score_paper(
    paper: Dict[str, Any],
    current_year: int,
    profile: Dict[str, float],
) -> float:
    citations = _citation_metric(paper)
    year = _extract_year(paper.get('year') or paper.get('published'))
    recency_bonus = 0.0
    if year:
        recency_bonus = max(
            0.0,
            profile['recency_max'] - (current_year - year) * profile['recency_decay_per_year'],
        )
    citation_score = (citations ** 0.5) * profile['citation_weight']
    recency_score = recency_bonus * profile['recency_weight']
    oa_bonus = profile['open_access_bonus'] if bool(paper.get('open_access')) else 0.0
    return citation_score + recency_score + oa_bonus


def search_arxiv(query: str, max_results: int = 500) -> List[Dict[str, Any]]:
    """Search arXiv with pagination (200 entries per page via 'start' offset)."""
    effective_max = min(max_results, MAX_PER_SOURCE)
    all_papers: List[Dict[str, Any]] = []
    start = 0

    while len(all_papers) < effective_max:
        remaining = effective_max - len(all_papers)
        fetch = min(200, remaining)
        params = urllib.parse.urlencode({
            'search_query': f'all:{query}',
            'start': start,
            'max_results': fetch,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        })
        url = f"{ARXIV_API}?{params}"
        try:
            xml_data = _request_text(url, headers={'User-Agent': 'MedAI/1.1'})
            root = ET.fromstring(xml_data)
        except Exception as e:
            print(f"  arXiv search error: {e}")
            break
        entries = root.findall('atom:entry', ARXIV_NS)
        if not entries:
            break
        for entry in entries:
            all_papers.append(_parse_arxiv_entry(entry))
        if len(entries) < fetch:
            break
        start += len(entries)
        time.sleep(3)  # arXiv rate limit: ~1 req/3s

    return all_papers


def search_semantic_scholar(
    query: str,
    api_config: APIConfig,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """Search Semantic Scholar with pagination (100 per page via 'offset')."""
    effective_max = min(limit, MAX_PER_SOURCE)
    all_papers: List[Dict[str, Any]] = []
    offset = 0
    headers = {'User-Agent': 'MedAI/1.1'}
    if api_config.semantic_scholar_api_key:
        headers['x-api-key'] = api_config.semantic_scholar_api_key

    while len(all_papers) < effective_max:
        remaining = effective_max - len(all_papers)
        fetch = min(100, remaining)
        params = urllib.parse.urlencode({
            'query': query,
            'limit': fetch,
            'offset': offset,
            'fields': 'title,authors,year,abstract,citationCount,externalIds,publicationVenue'
        })
        url = f"{SEMANTIC_SCHOLAR_API}/search?{params}"
        try:
            data = _request_json(url, headers=headers)
        except Exception as e:
            print(f"  Semantic Scholar search error: {e}")
            break
        items = data.get('data', [])
        if not items:
            break
        for item in items:
            all_papers.append(_build_ss_paper(item))
        if len(items) < fetch:
            break
        offset += len(items)
        time.sleep(PAGE_DELAY)

    return all_papers


def search_crossref(
    query: str,
    api_config: APIConfig,
    rows: int = 200,
) -> List[Dict[str, Any]]:
    """Search CrossRef with pagination (50 per page via 'offset')."""
    effective_max = min(rows, MAX_PER_SOURCE)
    all_papers: List[Dict[str, Any]] = []
    offset = 0
    user_agent = 'MedAI/1.1'
    if api_config.crossref_email:
        user_agent = f"{user_agent} (mailto:{api_config.crossref_email})"
    cr_headers = {'User-Agent': user_agent, 'Accept': 'application/json'}

    while len(all_papers) < effective_max:
        remaining = effective_max - len(all_papers)
        fetch = min(50, remaining)
        params = urllib.parse.urlencode({
            'query': query,
            'rows': fetch,
            'offset': offset,
            'select': 'DOI,title,author,abstract,container-title,volume,page,ISSN,URL,published-print,published-online,issued'
        })
        url = f"{CROSSREF_API}?{params}"
        try:
            data = _request_json(url, headers=cr_headers)
        except Exception as e:
            print(f"  CrossRef search error: {e}")
            break
        items = data.get('message', {}).get('items', [])
        if not items:
            break
        for item in items:
            all_papers.append(_build_cr_paper(item))
        if len(items) < fetch:
            break
        offset += len(items)
        time.sleep(PAGE_DELAY)

    return all_papers


def search_openalex(query: str, per_page: int = 200) -> List[Dict[str, Any]]:
    """Search OpenAlex with pagination (50 per page via 'page' param)."""
    effective_max = min(per_page, MAX_PER_SOURCE)
    all_papers: List[Dict[str, Any]] = []
    page = 1

    while len(all_papers) < effective_max:
        remaining = effective_max - len(all_papers)
        fetch = min(50, remaining)
        params = urllib.parse.urlencode({
            'filter': f'title.search:{query}',
            'per_page': fetch,
            'page': page,
            'sort': 'cited_by_count:desc'
        })
        url = f"{OPENALEX_API}?{params}"
        try:
            data = _request_json(url, headers={'User-Agent': 'MedAI/1.1'})
        except Exception as e:
            print(f"  OpenAlex search error: {e}")
            break
        items = data.get('results', [])
        if not items:
            break
        for item in items:
            all_papers.append(_build_oa_paper(item))
        if len(items) < fetch:
            break
        page += 1
        time.sleep(PAGE_DELAY)

    return all_papers


def deduplicate_papers(
    all_papers: List[Dict[str, Any]],
    fuzzy_threshold: float = 0.85,
) -> List[Dict[str, Any]]:
    """Remove duplicate papers across sources using DOI/arXiv/title keys.

    Falls back to fuzzy title matching to catch near-duplicates without DOI/arXiv IDs.
    """
    seen: Dict[str, int] = {}
    unique: List[Dict[str, Any]] = []
    seen_title_prefixes: List[str] = []

    for paper in all_papers:
        doi = (paper.get('doi') or '').lower().strip()
        arxiv_id = (paper.get('arxiv_id') or '').lower().strip()
        normalized_title = _normalize_title(paper.get('title', ''))

        if doi:
            key = f'doi:{doi}'
        elif arxiv_id:
            key = f'arxiv:{arxiv_id}'
        else:
            key = f'title:{normalized_title[:80]}'

        if not normalized_title:
            continue

        if not doi and not arxiv_id:
            title_prefix = normalized_title[:80]
            duplicate_by_title = False
            for previous in seen_title_prefixes:
                if title_prefix == previous:
                    duplicate_by_title = True
                    break
                if fuzzy_threshold > 0.0:
                    ratio = difflib.SequenceMatcher(None, title_prefix, previous).ratio()
                    if ratio >= fuzzy_threshold:
                        duplicate_by_title = True
                        break
            if duplicate_by_title:
                continue

        if key in seen:
            existing = unique[seen[key]]
            merged_sources = set(existing.get('sources', [existing.get('source', '')]))
            merged_sources.add(paper.get('source', ''))
            existing['sources'] = sorted(s for s in merged_sources if s)
            if not existing.get('doi') and paper.get('doi'):
                existing['doi'] = paper.get('doi')
            if _citation_metric(paper) > _citation_metric(existing):
                existing['citation_count'] = _citation_metric(paper)
            continue

        paper_copy = dict(paper)
        paper_copy['sources'] = [paper.get('source', '')]
        seen[key] = len(unique)
        unique.append(paper_copy)
        if not doi and not arxiv_id:
            seen_title_prefixes.append(normalized_title[:80])

    return unique


def filter_papers(
    papers: List[Dict[str, Any]],
    since_year: Optional[int],
    open_access_only: bool,
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for paper in papers:
        year = _extract_year(paper.get('year') or paper.get('published'))
        if since_year and (not year or year < since_year):
            continue
        if open_access_only and not bool(paper.get('open_access', False)):
            continue
        filtered.append(paper)
    return filtered


def rank_papers(
    papers: List[Dict[str, Any]],
    query: str,
    domain: str,
    top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    current_year = time.gmtime().tm_year
    effective_domain = infer_domain_from_query(query) if domain == 'auto' else domain
    profile = DOMAIN_PROFILES.get(effective_domain, DOMAIN_PROFILES['general'])

    scored: List[Dict[str, Any]] = []
    for paper in papers:
        paper_copy = dict(paper)
        paper_copy['rank_score'] = round(_score_paper(paper_copy, current_year, profile), 4)
        scored.append(paper_copy)

    ranked = sorted(
        scored,
        key=lambda p: p['rank_score'],
        reverse=True,
    )
    if top_n and top_n > 0:
        return ranked[:top_n]
    return ranked


def build_markdown_report(result: Dict[str, Any]) -> str:
    """Create a compact markdown snapshot for quick human review."""
    lines = [
        f"# Literature Search Report: {result['query']}",
        "",
        "## Summary",
        f"- Raw papers: {result['total_raw']}",
        f"- Deduplicated papers: {result['total_unique']}",
        f"- After filters/ranking: {result['total_final']}",
        "",
        "## Source Counts",
    ]
    for source, count in result['by_source'].items():
        lines.append(f"- {source}: {count}")

    lines.extend(["", "## Top Papers"])
    if not result['papers']:
        lines.append("- No papers matched the filters.")
        return '\n'.join(lines)

    for idx, paper in enumerate(result['papers'], start=1):
        title = (paper.get('title') or 'Untitled').strip()
        year = _extract_year(paper.get('year') or paper.get('published')) or 'n/a'
        citation_count = _citation_metric(paper)
        source_list = ', '.join(paper.get('sources', []))
        lines.append(
            f"{idx}. **{title}** ({year}) | citations={citation_count} | sources={source_list}"
        )
    return '\n'.join(lines)


def search_all(
    query: str,
    max_per_source: int,
    since_year: Optional[int],
    open_access_only: bool,
    domain: str,
    top_n: Optional[int],
) -> Dict[str, Any]:
    """Search all sources in parallel and apply post-processing."""
    results: Dict[str, List[Dict[str, Any]]] = {}

    api_config = load_api_config()

    print(f"  Searching all sources for: {query}")

    search_jobs = {
        'arxiv': lambda: search_arxiv(query, max_results=max_per_source),
        'semantic_scholar': lambda: search_semantic_scholar(
            query,
            api_config=api_config,
            limit=max_per_source,
        ),
        'crossref': lambda: search_crossref(query, api_config=api_config, rows=max_per_source),
        'openalex': lambda: search_openalex(query, per_page=max_per_source),
    }

    with ThreadPoolExecutor(max_workers=len(search_jobs)) as pool:
        future_to_source = {
            pool.submit(job): source for source, job in search_jobs.items()
        }
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                results[source] = future.result()
            except Exception as err:  # pragma: no cover - network failure path
                print(f"    {source}: failed ({err})")
                results[source] = []
            print(f"    {source}: {len(results[source])} papers")

    # Merge and deduplicate
    all_papers: List[Dict[str, Any]] = []
    for source_papers in results.values():
        all_papers.extend(source_papers)

    unique = deduplicate_papers(all_papers, fuzzy_threshold=0.85)
    filtered = filter_papers(unique, since_year=since_year, open_access_only=open_access_only)
    ranked = rank_papers(filtered, query=query, domain=domain, top_n=top_n)
    effective_domain = infer_domain_from_query(query) if domain == 'auto' else domain

    return {
        'query': query,
        'total_raw': len(all_papers),
        'total_unique': len(unique),
        'total_final': len(ranked),
        'by_source': {k: len(v) for k, v in results.items()},
        'filters': {
            'since_year': since_year,
            'open_access_only': open_access_only,
            'domain': domain,
            'effective_domain': effective_domain,
            'top_n': top_n,
        },
        'papers': ranked
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='MedAI Academic Writing Literature Client')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument(
        '--max-per-source',
        type=int,
        default=100,
        help='Max records requested from each source (default: 100)',
    )
    parser.add_argument(
        '--since-year',
        type=int,
        help='Keep papers published from this year onwards',
    )
    parser.add_argument(
        '--open-access-only',
        action='store_true',
        help='Keep only papers marked open access (best-effort based on source metadata)',
    )
    parser.add_argument(
        '--domain',
        choices=['auto', 'general', 'fast-moving-ml', 'theory', 'biomedical'],
        default='auto',
        help='Ranking profile: auto-detect from query or choose a fixed domain',
    )
    parser.add_argument(
        '--top',
        type=int,
        help='Return only top-N ranked papers after deduplication/filtering',
    )
    parser.add_argument(
        '--report-md',
        help='Optional markdown report output path',
    )
    args = parser.parse_args()

    results = search_all(
        args.query,
        max_per_source=max(1, min(args.max_per_source, MAX_PER_SOURCE)),
        since_year=args.since_year,
        open_access_only=args.open_access_only,
        domain=args.domain,
        top_n=args.top,
    )

    output = json.dumps(results, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    if args.report_md:
        markdown = build_markdown_report(results)
        with open(args.report_md, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Markdown report written to {args.report_md}")


if __name__ == '__main__':
    main()
