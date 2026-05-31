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
from dataclasses import dataclass
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


def _score_paper(paper: Dict[str, Any], current_year: int) -> float:
    citations = _citation_metric(paper)
    year = _extract_year(paper.get('year'))
    recency_bonus = 0.0
    if year:
        recency_bonus = max(0.0, 5.0 - (current_year - year) * 0.5)
    return (citations ** 0.5) + recency_bonus


def search_arxiv(query: str, max_results: int = 200) -> List[Dict[str, Any]]:
    """Search arXiv via REST API. Returns list of paper dicts."""
    params = urllib.parse.urlencode({
        'search_query': f'all:{query}',
        'start': 0,
        'max_results': min(max_results, 200),
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    })
    url = f"{ARXIV_API}?{params}"

    try:
        xml_data = _request_text(url, headers={'User-Agent': 'MedAI/1.1'})
        root = ET.fromstring(xml_data)
        papers = []

        for entry in root.findall('atom:entry', ARXIV_NS):
            paper = {
                'title': ' '.join((entry.find('atom:title', ARXIV_NS).text or '').split()),
                'summary': (entry.find('atom:summary', ARXIV_NS).text or '').strip(),
                'published': entry.find('atom:published', ARXIV_NS).text or '',
                'arxiv_id': entry.find('atom:id', ARXIV_NS).text or '',
                'authors': [],
                'categories': [],
                'year': _extract_year(entry.find('atom:published', ARXIV_NS).text or ''),
                'source': 'arxiv'
            }

            for author in entry.findall('atom:author', ARXIV_NS):
                name = author.find('atom:name', ARXIV_NS)
                if name is not None:
                    paper['authors'].append(name.text)

            for cat in entry.findall('atom:category', ARXIV_NS):
                term = cat.get('term', '')
                if term:
                    paper['categories'].append(term)

            # Check for DOI
            for link in entry.findall('atom:link', ARXIV_NS):
                if link.get('title') == 'doi':
                    paper['doi'] = link.get('href', '').replace('http://dx.doi.org/', '')

            papers.append(paper)

        return papers

    except Exception as e:
        print(f"  arXiv search error: {e}")
        return []


def search_semantic_scholar(
    query: str,
    api_config: APIConfig,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Search Semantic Scholar. Returns papers with citation counts."""
    params = urllib.parse.urlencode({
        'query': query,
        'limit': min(limit, 100),
        'fields': 'title,authors,year,abstract,citationCount,externalIds,publicationVenue'
    })
    url = f"{SEMANTIC_SCHOLAR_API}/search?{params}"

    try:
        headers = {'User-Agent': 'MedAI/1.1'}
        if api_config.semantic_scholar_api_key:
            headers['x-api-key'] = api_config.semantic_scholar_api_key
        data = _request_json(url, headers=headers)

        papers = []
        for item in data.get('data', []):
            paper = {
                'title': item.get('title', ''),
                'year': item.get('year', ''),
                'abstract': item.get('abstract', ''),
                'citation_count': item.get('citationCount', 0),
                'authors': [a.get('name', '') for a in item.get('authors', [])],
                'external_ids': item.get('externalIds', {}),
                'venue': item.get('publicationVenue', {}).get('name', ''),
                'source': 'semantic_scholar'
            }
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"  Semantic Scholar search error: {e}")
        return []


def search_crossref(
    query: str,
    api_config: APIConfig,
    rows: int = 50,
) -> List[Dict[str, Any]]:
    """Search CrossRef. Returns papers with DOIs and BibTeX-ready metadata."""
    params = urllib.parse.urlencode({
        'query': query,
        'rows': min(rows, 50),
        'select': 'DOI,title,author,abstract,container-title,volume,page,ISSN,URL,published-print'
    })
    url = f"{CROSSREF_API}?{params}"

    try:
        user_agent = 'MedAI/1.1'
        if api_config.crossref_email:
            user_agent = f"{user_agent} (mailto:{api_config.crossref_email})"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': user_agent,
                'Accept': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        papers = []
        for item in data.get('message', {}).get('items', []):
            paper = {
                'title': ' '.join(item.get('title', [''])),
                'doi': item.get('DOI', ''),
                'authors': [a.get('family', '') for a in item.get('author', []) if a.get('family')],
                'abstract': item.get('abstract', ''),
                'journal': item.get('container-title', [''])[0] if item.get('container-title') else '',
                'volume': item.get('volume', ''),
                'pages': item.get('page', ''),
                'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0],
                'source': 'crossref'
            }
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"  CrossRef search error: {e}")
        return []


def search_openalex(query: str, per_page: int = 50) -> List[Dict[str, Any]]:
    """Search OpenAlex. Broad coverage including non-English works."""
    params = urllib.parse.urlencode({
        'filter': f'title.search:{query}',
        'per_page': min(per_page, 50),
        'sort': 'cited_by_count:desc'
    })
    url = f"{OPENALEX_API}?{params}"

    try:
        data = _request_json(url, headers={'User-Agent': 'MedAI/1.1'})

        papers = []
        for item in data.get('results', []):
            paper = {
                'title': item.get('title', ''),
                'doi': item.get('doi', ''),
                'cited_by_count': item.get('cited_by_count', 0),
                'authors': [a.get('author', {}).get('display_name', '') for a in item.get('authorships', [])],
                'open_access': item.get('open_access', {}).get('is_oa', False),
                'concepts': [c.get('display_name', '') for c in item.get('concepts', [])[:5]],
                'year': item.get('publication_year', ''),
                'source': 'openalex'
            }
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"  OpenAlex search error: {e}")
        return []


def deduplicate_papers(all_papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate papers across sources using DOI/arXiv/title keys."""
    seen: Dict[str, int] = {}
    unique: List[Dict[str, Any]] = []

    for paper in all_papers:
        doi = (paper.get('doi') or '').lower().strip()
        arxiv_id = (paper.get('arxiv_id') or '').lower().strip()
        normalized_title = _normalize_title(paper.get('title', ''))

        if doi:
            key = f'doi:{doi}'
        elif arxiv_id:
            key = f'arxiv:{arxiv_id}'
        else:
            key = f'title:{normalized_title[:120]}'

        if not normalized_title:
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
    top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    current_year = time.gmtime().tm_year
    ranked = sorted(
        papers,
        key=lambda p: _score_paper(p, current_year),
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
    top_n: Optional[int],
) -> Dict[str, Any]:
    """Search all sources sequentially with polite pacing and post-processing."""
    results = {}

    api_config = load_api_config()

    print(f"  Searching all sources for: {query}")

    results['arxiv'] = search_arxiv(query, max_results=max_per_source)
    time.sleep(3)  # Rate limit: arXiv is ~1 req/3s
    print(f"    arXiv: {len(results['arxiv'])} papers")

    results['semantic_scholar'] = search_semantic_scholar(
        query,
        api_config=api_config,
        limit=max_per_source,
    )
    time.sleep(1)
    print(f"    Semantic Scholar: {len(results['semantic_scholar'])} papers")

    results['crossref'] = search_crossref(query, api_config=api_config, rows=max_per_source)
    time.sleep(1)
    print(f"    CrossRef: {len(results['crossref'])} papers")

    results['openalex'] = search_openalex(query, per_page=max_per_source)
    print(f"    OpenAlex: {len(results['openalex'])} papers")

    # Merge and deduplicate
    all_papers: List[Dict[str, Any]] = []
    for source_papers in results.values():
        all_papers.extend(source_papers)

    unique = deduplicate_papers(all_papers)
    filtered = filter_papers(unique, since_year=since_year, open_access_only=open_access_only)
    ranked = rank_papers(filtered, top_n=top_n)

    return {
        'query': query,
        'total_raw': len(all_papers),
        'total_unique': len(unique),
        'total_final': len(ranked),
        'by_source': {k: len(v) for k, v in results.items()},
        'filters': {
            'since_year': since_year,
            'open_access_only': open_access_only,
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
        max_per_source=max(1, min(args.max_per_source, 200)),
        since_year=args.since_year,
        open_access_only=args.open_access_only,
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
