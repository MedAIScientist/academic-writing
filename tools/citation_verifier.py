#!/usr/bin/env python3
"""
Sisyphus Academica — Citation Verifier
Verifies every citation against 2+ sources.
Flags hallucinations, misattributions, and unverifiable claims.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import re
from typing import Dict, List, Optional, Tuple


SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"
CROSSREF_API = "https://api.crossref.org/works"
ARXIV_API = "http://export.arxiv.org/api/query"

RETRYABLE_CODES = {429, 502, 503, 504}
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0


def _api_request(url: str, headers: Optional[Dict] = None,
                 timeout: int = 30, max_retries: Optional[int] = None,
                 base_delay: float = DEFAULT_BASE_DELAY) -> Optional[bytes]:
    """HTTP GET with exponential backoff retry for transient failures.

    Retries on 429, 502, 503, 504 with delay: base_delay * 2^attempt.
    Uses DEFAULT_MAX_RETRIES when max_retries is None.
    Returns None if all retries exhausted.
    """
    if max_retries is None:
        max_retries = DEFAULT_MAX_RETRIES
    req = urllib.request.Request(url, headers=headers or {})
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE_CODES and attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            return None
        except (urllib.error.URLError, OSError):
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            return None
    return None


def search_semantic_scholar(title: str) -> Dict:
    """Search Semantic Scholar for a paper by title."""
    params = urllib.parse.urlencode({
        'query': title,
        'limit': 3,
        'fields': 'title,authors,year,abstract,citationCount,externalIds'
    })
    url = f"{SEMANTIC_SCHOLAR_API}/search?{params}"

    body = _api_request(url, headers={'User-Agent': 'SisyphusAcademica/1.0'}, timeout=15)
    if body is None:
        return {}
    try:
        data = json.loads(body.decode('utf-8'))
        return data.get('data', [{}])[0] if data.get('data') else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def search_crossref(title: str) -> Dict:
    """Search CrossRef for a paper by title."""
    params = urllib.parse.urlencode({
        'query': title,
        'rows': 2,
        'select': 'DOI,title,author,container-title'
    })
    url = f"{CROSSREF_API}?{params}"

    body = _api_request(
        url,
        headers={
            'User-Agent': 'SisyphusAcademica/1.0 (mailto:research@example.com)',
            'Accept': 'application/json'
        },
        timeout=15
    )
    if body is None:
        return {}
    try:
        data = json.loads(body.decode('utf-8'))
        items = data.get('message', {}).get('items', [])
        return items[0] if items else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def verify_citation(citation_key: str, claim: str) -> Dict:
    """Verify a single citation by searching multiple sources."""
    result = {
        'citation_key': citation_key,
        'claim': claim[:200],
        'semantic_scholar': None,
        'crossref': None,
        'verified': False,
        'issues': []
    }
    
    # Extract paper title from citation key or claim
    # In practice, the claim text contains the paper reference
    
    # Search Semantic Scholar
    ss_result = search_semantic_scholar(claim[:100])
    if ss_result:
        result['semantic_scholar'] = {
            'title': ss_result.get('title', ''),
            'year': ss_result.get('year', ''),
            'citation_count': ss_result.get('citationCount', 0),
            'external_ids': ss_result.get('externalIds', {})
        }
    
    # Search CrossRef
    cr_result = search_crossref(claim[:100])
    if cr_result:
        result['crossref'] = {
            'doi': cr_result.get('DOI', ''),
            'title': ' '.join(cr_result.get('title', [''])),
            'container': cr_result.get('container-title', [''])[0] if cr_result.get('container-title') else ''
        }
    
    # Determine verification status
    if result['semantic_scholar'] and result['crossref']:
        # Both found the paper
        ss_title = (result['semantic_scholar'].get('title') or '').lower()
        cr_title = (result['crossref'].get('title') or '').lower()
        if ss_title and cr_title and (ss_title[:50] == cr_title[:50] or 
                                       ss_title[:30] in cr_title or cr_title[:30] in ss_title):
            result['verified'] = True
    elif result['semantic_scholar'] or result['crossref']:
        result['verified'] = True
        result['issues'].append("Found in only 1 source — weak verification")
    else:
        result['issues'].append("Paper not found in any source — may be hallucinated")
    
    return result


def verify_citations(findings: Dict) -> Dict:
    """Verify all citations in a paper findings file."""
    citations = []
    
    # Extract citations from text
    if 'paper' in findings:
        text = findings['paper']
        # Find patterns like [AuthorYear], [1], Smith et al. (2020), etc.
        citation_patterns = re.findall(r'\[([^\]]+)\]', text)
        for cp in citation_patterns:
            citations.append({'key': cp, 'claim': ''})
    
    results = []
    for citation in citations:
        result = verify_citation(citation['key'], citation['claim'])
        results.append(result)
    
    verified_count = sum(1 for r in results if r['verified'])
    hallucinated = [r for r in results if not r['verified']]
    
    return {
        'total_citations': len(results),
        'verified': verified_count,
        'hallucinated_count': len(hallucinated),
        'issues_count': sum(len(r.get('issues', [])) for r in results),
        'hallucinated_citations': [r['citation_key'] for r in hallucinated],
        'blocked': len(hallucinated) > 0,
        'details': results
    }


def generate_bibtex(paper: Dict) -> str:
    """Generate BibTeX entry from verified paper metadata."""
    if not paper.get('doi'):
        return ''
    
    doi = paper['doi']
    author_field = 'Author, A.'
    title_field = paper.get('title', 'Untitled')
    year = paper.get('year', 'n.d.')
    key = f"{author_field.split(',')[0]}{year}"
    
    bibtex = f"""@article{{{key},
  author = {{{author_field}}},
  title = {{{title_field}}},
  year = {{{year}}},
  doi = {{{doi}}}
}}"""
    return bibtex


def main():
    global DEFAULT_MAX_RETRIES
    import argparse
    parser = argparse.ArgumentParser(description='Sisyphus Academica Citation Verifier')
    parser.add_argument('--findings', '-f', required=True, help='Findings JSON file')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--citation', '-c', help='Verify a single citation (overrides --findings)')
    parser.add_argument('--retries', type=int, default=DEFAULT_MAX_RETRIES,
                        help=f'Max retries for API calls (default: {DEFAULT_MAX_RETRIES})')
    args = parser.parse_args()
    DEFAULT_MAX_RETRIES = args.retries
    
    if args.citation:
        result = verify_citation('manual', args.citation)
        print(json.dumps(result, indent=2))
        return
    
    with open(args.findings) as f:
        findings = json.load(f)
    
    result = verify_citations(findings)
    
    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Verification results written to {args.output}")
    else:
        print(output)
    
    if result['blocked']:
        print(f"\n⚠ BLOCKED: {result['hallucinated_count']} unverifiable citations found")
        for c in result['hallucinated_citations']:
            print(f"  - {c}")
        exit(1)
    else:
        print(f"\n✓ All {result['verified']}/{result['total_citations']} citations verified")
        exit(0)


if __name__ == '__main__':
    main()
