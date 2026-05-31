#!/usr/bin/env python3
"""
MedAI Academic Writing - One-command pipeline runner.
Runs literature retrieval, optional citation verification, and report generation.
"""

import json
from pathlib import Path
from typing import Any, Dict

from citation_verifier import load_api_config, verify_citations
from literature_client import build_markdown_report, search_all


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def run_pipeline(args) -> Dict[str, Any]:
    literature = search_all(
        query=args.query,
        max_per_source=max(1, min(args.max_per_source, 200)),
        since_year=args.since_year,
        open_access_only=args.open_access_only,
        domain=args.domain,
        top_n=args.top,
    )

    out_dir = Path(args.out_dir)
    literature_json_path = out_dir / 'literature.json'
    literature_md_path = out_dir / 'literature-report.md'
    _write_json(literature_json_path, literature)
    _write_text(literature_md_path, build_markdown_report(literature))

    citation_audit_path = out_dir / 'citation-audit.json'
    if args.manuscript:
        manuscript_path = Path(args.manuscript)
        try:
            manuscript_text = manuscript_path.read_text(encoding='utf-8')
            findings = {'paper': manuscript_text}
            citation_audit = verify_citations(
                findings=findings,
                api_config=load_api_config(),
                min_match_score=max(0.0, min(args.min_match_score, 1.0)),
                require_two_sources=args.strict_two_source,
            )
        except OSError as err:
            citation_audit = {
                'blocked': True,
                'error': f'Cannot read manuscript file: {manuscript_path} ({err})',
                'total_citations': 0,
                'verified': 0,
                'hallucinated_count': 0,
            }
    else:
        citation_audit = {
            'skipped': True,
            'reason': 'No manuscript provided. Pass --manuscript to run citation checks.',
            'total_citations': 0,
            'verified': 0,
            'hallucinated_count': 0,
            'blocked': False,
        }
    _write_json(citation_audit_path, citation_audit)

    summary_path = out_dir / 'pipeline-summary.md'
    summary_lines = [
        '# Pipeline Summary',
        '',
        f"- Query: {args.query}",
        f"- Literature raw count: {literature['total_raw']}",
        f"- Literature final count: {literature['total_final']}",
        f"- Ranking domain: {literature['filters']['effective_domain']}",
        f"- Citation audit blocked: {citation_audit.get('blocked', False)}",
        '',
        '## Artifacts',
        f"- {literature_json_path}",
        f"- {literature_md_path}",
        f"- {citation_audit_path}",
    ]
    _write_text(summary_path, '\n'.join(summary_lines))

    return {
        'literature_json': str(literature_json_path),
        'literature_report': str(literature_md_path),
        'citation_audit': str(citation_audit_path),
        'summary': str(summary_path),
        'blocked': bool(citation_audit.get('blocked', False)),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Run literature + citation pipeline in one command')
    parser.add_argument('query', help='Research query')
    parser.add_argument('--manuscript', help='Path to manuscript text/markdown for citation audit')
    parser.add_argument('--out-dir', default='out/papers', help='Artifact output directory')

    parser.add_argument('--max-per-source', type=int, default=100)
    parser.add_argument('--since-year', type=int)
    parser.add_argument('--open-access-only', action='store_true')
    parser.add_argument(
        '--domain',
        choices=['auto', 'general', 'fast-moving-ml', 'theory', 'biomedical'],
        default='auto',
        help='Ranking profile for literature ordering',
    )
    parser.add_argument('--top', type=int)

    parser.add_argument('--strict-two-source', action='store_true')
    parser.add_argument('--min-match-score', type=float, default=0.45)

    args = parser.parse_args()
    artifacts = run_pipeline(args)
    print(json.dumps(artifacts, indent=2))
    if artifacts['blocked']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
