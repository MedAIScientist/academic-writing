#!/usr/bin/env python3
"""
MedAI Academic Writing - Citation Verifier
Verifies citations against Semantic Scholar and CrossRef.
Flags likely hallucinations and weakly supported references.
"""

import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"
CROSSREF_API = "https://api.crossref.org/works"


@dataclass(frozen=True)
class APIConfig:
    semantic_scholar_api_key: str
    crossref_email: str


def _load_env_file() -> None:
    env_path = Path('.env')
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_api_config() -> APIConfig:
    _load_env_file()
    return APIConfig(
        semantic_scholar_api_key=os.getenv('SEMANTIC_SCHOLAR_API_KEY', '').strip(),
        crossref_email=os.getenv('CROSSREF_EMAIL', '').strip(),
    )


def _normalize_title(text: str) -> str:
    return ' '.join(re.sub(r'[^a-z0-9 ]+', ' ', (text or '').lower()).split())


def _title_similarity(left: str, right: str) -> float:
    left_tokens = set(_normalize_title(left).split())
    right_tokens = set(_normalize_title(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return overlap / union


def _clip_text(text: str, max_chars: int = 240) -> str:
    compact = ' '.join((text or '').split())
    return compact[:max_chars]


def _context_from_span(text: str, start: int, end: int) -> str:
    """Return nearest sentence-like context around a span."""
    left = max(text.rfind('.', 0, start), text.rfind('!', 0, start), text.rfind('?', 0, start), text.rfind('\n', 0, start))
    right_candidates = [
        idx
        for idx in (text.find('.', end), text.find('!', end), text.find('?', end), text.find('\n', end))
        if idx != -1
    ]
    right = min(right_candidates) if right_candidates else len(text)
    context = text[left + 1:right + 1].strip()
    return context if context else text[max(0, start - 80): min(len(text), end + 80)].strip()


def _looks_like_bracket_citation(key: str) -> bool:
    """Heuristic gate to reduce false positives from generic bracketed text."""
    candidate = key.strip()
    if not candidate:
        return False
    if candidate.startswith('http://') or candidate.startswith('https://'):
        return False
    if candidate.startswith('@'):
        return True
    if re.fullmatch(r'\d+(?:[\s,\-]+\d+)*', candidate):
        return True
    if re.search(r'(19|20)\d{2}', candidate):
        return True
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9:_\-]{2,}', candidate):
        return True
    return False


def search_semantic_scholar(title: str, api_config: APIConfig) -> Dict[str, Any]:
    """Search Semantic Scholar for a paper by title."""
    params = urllib.parse.urlencode(
        {
            'query': title,
            'limit': 3,
            'fields': 'title,authors,year,abstract,citationCount,externalIds',
        }
    )
    url = f"{SEMANTIC_SCHOLAR_API}/search?{params}"

    try:
        headers = {'User-Agent': 'medai/1.1'}
        if api_config.semantic_scholar_api_key:
            headers['x-api-key'] = api_config.semantic_scholar_api_key
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('data', [{}])[0] if data.get('data') else {}
    except Exception:
        return {}


def search_crossref(title: str, api_config: APIConfig) -> Dict[str, Any]:
    """Search CrossRef for a paper by title."""
    params = urllib.parse.urlencode(
        {
            'query': title,
            'rows': 2,
            'select': 'DOI,title,author,container-title',
        }
    )
    url = f"{CROSSREF_API}?{params}"

    try:
        user_agent = 'medai/1.1'
        if api_config.crossref_email:
            user_agent = f"{user_agent} (mailto:{api_config.crossref_email})"

        req = urllib.request.Request(
            url,
            headers={'User-Agent': user_agent, 'Accept': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        items = data.get('message', {}).get('items', [])
        return items[0] if items else {}
    except Exception:
        return {}


def verify_citation(
    citation_key: str,
    claim: str,
    api_config: APIConfig,
    min_match_score: float,
    require_two_sources: bool,
) -> Dict[str, Any]:
    """Verify one citation using multiple metadata sources."""
    result: Dict[str, Any] = {
        'citation_key': citation_key,
        'claim': _clip_text(claim),
        'semantic_scholar': None,
        'crossref': None,
        'verified': False,
        'match_score': 0.0,
        'issues': [],
    }

    query = _clip_text(claim) if claim.strip() else citation_key.strip()
    if not query:
        result['issues'].append('Empty citation query')
        return result

    ss_result = search_semantic_scholar(query, api_config=api_config)
    if ss_result:
        result['semantic_scholar'] = {
            'title': ss_result.get('title', ''),
            'year': ss_result.get('year', ''),
            'citation_count': ss_result.get('citationCount', 0),
            'external_ids': ss_result.get('externalIds', {}),
        }

    cr_result = search_crossref(query, api_config=api_config)
    if cr_result:
        result['crossref'] = {
            'doi': cr_result.get('DOI', ''),
            'title': ' '.join(cr_result.get('title', [''])),
            'container': cr_result.get('container-title', [''])[0]
            if cr_result.get('container-title')
            else '',
        }

    if result['semantic_scholar'] and result['crossref']:
        ss_title = result['semantic_scholar'].get('title', '')
        cr_title = result['crossref'].get('title', '')
        score = _title_similarity(ss_title, cr_title)
        result['match_score'] = round(score, 4)
        if score >= min_match_score:
            result['verified'] = True
        else:
            result['issues'].append(
                f"Source title mismatch (score={score:.3f} < threshold={min_match_score:.3f})"
            )
    elif result['semantic_scholar'] or result['crossref']:
        if require_two_sources:
            result['issues'].append('Found in only 1 source while strict mode requires 2 sources')
        else:
            result['verified'] = True
            result['issues'].append('Found in only 1 source - weak verification')
    else:
        result['issues'].append('Paper not found in any source - may be hallucinated')

    return result


def extract_citations(text: str) -> List[Dict[str, str]]:
    """Extract citation keys and sentence-level context from text."""
    citations: List[Dict[str, str]] = []
    seen_pairs = set()
    if not text.strip():
        return citations

    for match in re.finditer(r'\[([^\]]+)\]', text):
        key = match.group(1).strip()
        if not key:
            continue
        if not _looks_like_bracket_citation(key):
            continue
        if re.match(r'^\s*\(\s*(?:https?://|www\.|doi:|mailto:)', text[match.end():], flags=re.IGNORECASE):
            # Markdown link label patterns: [label](url) or [label] (url)
            continue
        context = _context_from_span(text, match.start(), match.end())
        pair = (key, context)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        citations.append({'key': key, 'claim': context})

    for match in re.finditer(r'\(([A-Z][A-Za-z\-]+(?:\s+et al\.)?,\s*(?:19|20)\d{2})\)', text):
        key = match.group(1).strip()
        context = _context_from_span(text, match.start(), match.end())
        pair = (key, context)
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        citations.append({'key': key, 'claim': context})

    return citations


def findings_to_text(findings: Dict[str, Any]) -> str:
    """Extract manuscript text from a findings payload."""
    for key in ('paper', 'text', 'content', 'manuscript'):
        value = findings.get(key)
        if isinstance(value, str) and value.strip():
            return value

    sections = findings.get('sections')
    if isinstance(sections, list):
        text_blocks: List[str] = []
        for section in sections:
            if isinstance(section, dict):
                maybe_text = section.get('text') or section.get('content')
                if isinstance(maybe_text, str):
                    text_blocks.append(maybe_text)
        return '\n\n'.join(text_blocks)

    return ''


def verify_citations(
    findings: Dict[str, Any],
    api_config: APIConfig,
    min_match_score: float,
    require_two_sources: bool,
) -> Dict[str, Any]:
    """Verify all extracted citations from findings."""
    text = findings_to_text(findings)
    citations = extract_citations(text)

    details = [
        verify_citation(
            citation['key'],
            citation['claim'],
            api_config=api_config,
            min_match_score=min_match_score,
            require_two_sources=require_two_sources,
        )
        for citation in citations
    ]

    verified_count = sum(1 for item in details if item['verified'])
    hallucinated = [item for item in details if not item['verified']]

    return {
        'total_citations': len(details),
        'verified': verified_count,
        'hallucinated_count': len(hallucinated),
        'issues_count': sum(len(item.get('issues', [])) for item in details),
        'hallucinated_citations': [item['citation_key'] for item in hallucinated],
        'blocked': len(hallucinated) > 0,
        'min_match_score': min_match_score,
        'strict_two_source': require_two_sources,
        'details': details,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='MedAI Academic Writing Citation Verifier')
    parser.add_argument('--findings', '-f', help='Findings JSON file')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--citation', '-c', help='Verify a single citation (overrides --findings)')
    parser.add_argument('--text-file', help='Raw manuscript text/markdown file to scan')
    parser.add_argument(
        '--min-match-score',
        type=float,
        default=0.45,
        help='Minimum title similarity score for strict two-source checks (default: 0.45)',
    )
    parser.add_argument(
        '--strict-two-source',
        action='store_true',
        help='Require both Semantic Scholar and CrossRef for each citation',
    )
    args = parser.parse_args()

    api_config = load_api_config()
    min_match_score = max(0.0, min(args.min_match_score, 1.0))

    if args.citation:
        result = verify_citation(
            'manual',
            args.citation,
            api_config=api_config,
            min_match_score=min_match_score,
            require_two_sources=args.strict_two_source,
        )
        print(json.dumps(result, indent=2))
        return

    if not args.findings and not args.text_file:
        parser.error('Provide --findings or --text-file (or use --citation)')

    findings: Dict[str, Any] = {}
    if args.findings:
        with open(args.findings, encoding='utf-8') as infile:
            findings = json.load(infile)
    if args.text_file:
        with open(args.text_file, encoding='utf-8') as infile:
            findings['paper'] = infile.read()

    result = verify_citations(
        findings,
        api_config=api_config,
        min_match_score=min_match_score,
        require_two_sources=args.strict_two_source,
    )

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as outfile:
            outfile.write(output)
        print(f"Verification results written to {args.output}")
    else:
        print(output)

    if result['blocked']:
        print(f"\n[BLOCKED] {result['hallucinated_count']} unverifiable citations found")
        for citation in result['hallucinated_citations']:
            print(f"  - {citation}")
        raise SystemExit(1)

    print(f"\n[PASS] All {result['verified']}/{result['total_citations']} citations verified")
    raise SystemExit(0)


if __name__ == '__main__':
    main()
