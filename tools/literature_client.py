#!/usr/bin/env python3
"""
Sisyphus Academica — Literature API Client
Multi-source literature search: arXiv, Semantic Scholar, CrossRef, OpenAlex
Returns deduplicated, structured paper metadata.
"""

import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional


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


def _fetch_json(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Optional[dict]:
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'SisyphusAcademica/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None


def _parse_arxiv_entry(entry) -> Dict:
    paper = {
        'title': ' '.join((entry.find('atom:title', ARXIV_NS).text or '').split()),
        'summary': (entry.find('atom:summary', ARXIV_NS).text or '').strip(),
        'published': entry.find('atom:published', ARXIV_NS).text or '',
        'arxiv_id': entry.find('atom:id', ARXIV_NS).text or '',
        'authors': [],
        'categories': [],
        'source': 'arxiv'
    }
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


def _build_ss_paper(item: Dict) -> Dict:
    return {
        'title': item.get('title', ''),
        'year': item.get('year', ''),
        'abstract': item.get('abstract', ''),
        'citation_count': item.get('citationCount', 0),
        'authors': [a.get('name', '') for a in item.get('authors', [])],
        'external_ids': item.get('externalIds', {}),
        'venue': item.get('publicationVenue', {}).get('name', ''),
        'source': 'semantic_scholar'
    }


def _build_cr_paper(item: Dict) -> Dict:
    return {
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


def _build_oa_paper(item: Dict) -> Dict:
    return {
        'title': item.get('title', ''),
        'doi': item.get('doi', ''),
        'cited_by_count': item.get('cited_by_count', 0),
        'authors': [a.get('author', {}).get('display_name', '') for a in item.get('authorships', [])],
        'open_access': item.get('open_access', {}).get('is_oa', False),
        'concepts': [c.get('display_name', '') for c in item.get('concepts', [])[:5]],
        'year': item.get('publication_year', ''),
        'source': 'openalex'
    }


def search_arxiv(query: str, max_results: int = 500) -> List[Dict]:
    """Search arXiv with pagination (200 per page via 'start' offset)."""
    effective_max = min(max_results, MAX_PER_SOURCE)
    all_papers = []
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
            req = urllib.request.Request(url, headers={'User-Agent': 'SisyphusAcademica/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                root = ET.fromstring(resp.read().decode('utf-8'))
        except Exception:
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


def search_semantic_scholar(query: str, max_results: int = 500) -> List[Dict]:
    """Search Semantic Scholar with pagination (100 per page via 'offset')."""
    effective_max = min(max_results, MAX_PER_SOURCE)
    all_papers = []
    offset = 0

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
        data = _fetch_json(url)
        if data is None:
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


def search_crossref(query: str, max_results: int = 200) -> List[Dict]:
    """Search CrossRef with pagination (50 per page via 'offset')."""
    effective_max = min(max_results, MAX_PER_SOURCE)
    all_papers = []
    offset = 0

    while len(all_papers) < effective_max:
        remaining = effective_max - len(all_papers)
        fetch = min(50, remaining)
        params = urllib.parse.urlencode({
            'query': query,
            'rows': fetch,
            'offset': offset,
            'select': 'DOI,title,author,abstract,container-title,volume,page,ISSN,URL,published-print'
        })
        url = f"{CROSSREF_API}?{params}"
        data = _fetch_json(url, headers={
            'User-Agent': 'SisyphusAcademica/1.0 (mailto:research@example.com)',
            'Accept': 'application/json'
        })
        if data is None:
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


def search_openalex(query: str, max_results: int = 200) -> List[Dict]:
    """Search OpenAlex with pagination (50 per page via 'page' param)."""
    effective_max = min(max_results, MAX_PER_SOURCE)
    all_papers = []
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
        data = _fetch_json(url)
        if data is None:
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


def deduplicate_papers(all_papers: List[Dict]) -> List[Dict]:
    """Remove duplicate papers across sources using title similarity."""
    seen_titles = set()
    unique = []
    
    for paper in all_papers:
        title = paper.get('title')
        if not title or not isinstance(title, str):
            continue
        title = title.lower().strip()
        # Simple dedup: normalize and check first 80 chars
        key = title[:80]
        if key and key not in seen_titles:
            seen_titles.add(key)
            unique.append(paper)
    
    return unique


def search_all(query: str, max_results: int = 500) -> Dict:
    """Search all sources with pagination up to max_results per source."""
    results = {}
    print(f"  Searching all sources for: {query}")

    results['arxiv'] = search_arxiv(query, max_results)
    print(f"    arXiv: {len(results['arxiv'])} papers")

    results['semantic_scholar'] = search_semantic_scholar(query, max_results)
    print(f"    Semantic Scholar: {len(results['semantic_scholar'])} papers")

    results['crossref'] = search_crossref(query, max_results)
    print(f"    CrossRef: {len(results['crossref'])} papers")

    results['openalex'] = search_openalex(query, max_results)
    print(f"    OpenAlex: {len(results['openalex'])} papers")

    all_papers = []
    for source_papers in results.values():
        all_papers.extend(source_papers)
    unique = deduplicate_papers(all_papers)

    return {
        'query': query,
        'total_raw': len(all_papers),
        'total_unique': len(unique),
        'by_source': {k: len(v) for k, v in results.items()},
        'papers': unique
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sisyphus Academica Literature Client')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--max-results', type=int, default=500,
                        help='Max papers per source (default: 500)')
    args = parser.parse_args()
    
    results = search_all(args.query, max_results=args.max_results)
    
    output = json.dumps(results, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
