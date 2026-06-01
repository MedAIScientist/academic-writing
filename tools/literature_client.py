#!/usr/bin/env python3
"""
Sisyphus Academica — Literature API Client
Multi-source literature search: arXiv, Semantic Scholar, CrossRef, OpenAlex
Returns deduplicated, structured paper metadata.
"""

import difflib
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


def search_arxiv(query: str, max_results: int = 200) -> List[Dict]:
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
        req = urllib.request.Request(url, headers={'User-Agent': 'SisyphusAcademica/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode('utf-8')
        
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


def search_semantic_scholar(query: str, limit: int = 100) -> List[Dict]:
    """Search Semantic Scholar. Returns papers with citation counts."""
    params = urllib.parse.urlencode({
        'query': query,
        'limit': min(limit, 100),
        'fields': 'title,authors,year,abstract,citationCount,externalIds,publicationVenue'
    })
    url = f"{SEMANTIC_SCHOLAR_API}/search?{params}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SisyphusAcademica/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
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


def search_crossref(query: str, rows: int = 50) -> List[Dict]:
    """Search CrossRef. Returns papers with DOIs and BibTeX-ready metadata."""
    params = urllib.parse.urlencode({
        'query': query,
        'rows': min(rows, 50),
        'select': 'DOI,title,author,abstract,container-title,volume,page,ISSN,URL,published-print'
    })
    url = f"{CROSSREF_API}?{params}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'SisyphusAcademica/1.0 (mailto:research@example.com)',
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


def search_openalex(query: str, per_page: int = 50) -> List[Dict]:
    """Search OpenAlex. Broad coverage including non-English works."""
    params = urllib.parse.urlencode({
        'filter': f'title.search:{query}',
        'per_page': min(per_page, 50),
        'sort': 'cited_by_count:desc'
    })
    url = f"{OPENALEX_API}?{params}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SisyphusAcademica/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
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


def deduplicate_papers(all_papers: List[Dict], fuzzy_threshold: float = 0.0) -> List[Dict]:
    """Remove duplicate papers across sources using title similarity.

    Uses exact matching on first 80 chars as fast path.
    When fuzzy_threshold > 0, also checks near-duplicates via difflib.SequenceMatcher.
    """
    seen_titles = []
    unique = []

    for paper in all_papers:
        title = paper.get('title')
        if not title or not isinstance(title, str):
            continue
        normalized = title.lower().strip()
        if not normalized:
            continue

        # Fast path: exact prefix match
        key = normalized[:80]
        if key in seen_titles:
            continue

        if fuzzy_threshold > 0.0:
            # Slow path: fuzzy match against all seen titles
            is_duplicate = False
            for seen in seen_titles:
                ratio = difflib.SequenceMatcher(None, normalized[:80], seen).ratio()
                if ratio >= fuzzy_threshold:
                    is_duplicate = True
                    break
            if is_duplicate:
                continue

        seen_titles.append(key)
        unique.append(paper)

    return unique


def search_all(query: str) -> Dict:
    """Search all sources in parallel (simulated sequential for API limits)."""
    results = {}
    
    print(f"  Searching all sources for: {query}")
    
    results['arxiv'] = search_arxiv(query)
    time.sleep(3)  # Rate limit: arXiv is ~1 req/3s
    print(f"    arXiv: {len(results['arxiv'])} papers")
    
    results['semantic_scholar'] = search_semantic_scholar(query)
    time.sleep(1)
    print(f"    Semantic Scholar: {len(results['semantic_scholar'])} papers")
    
    results['crossref'] = search_crossref(query)
    time.sleep(1)
    print(f"    CrossRef: {len(results['crossref'])} papers")
    
    results['openalex'] = search_openalex(query)
    print(f"    OpenAlex: {len(results['openalex'])} papers")
    
    # Merge and deduplicate (with fuzzy matching at 0.85 threshold)
    all_papers = []
    for source_papers in results.values():
        all_papers.extend(source_papers)

    unique = deduplicate_papers(all_papers, fuzzy_threshold=0.85)
    
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
    args = parser.parse_args()
    
    results = search_all(args.query)
    
    output = json.dumps(results, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
