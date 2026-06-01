#!/usr/bin/env python3
"""
academica CLI — research pipeline tools.

Usage:
    academica demo              Run demo (generates mini paper, no API keys)
    academica configure         Set up API keys interactively
    academica search QUERY      Search literature (arXiv, Semantic Scholar, etc.)
    academica verify FILE       Verify citations in a paper JSON file
    academica bibtex DOI        Generate BibTeX entry from a DOI
"""

import sys


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    command = args[0]

    if command == "demo":
        from .demo import run_demo
        run_demo()
    elif command == "configure":
        from .configure import run_configure
        run_configure()
    elif command == "search":
        query = " ".join(args[1:]) if len(args) > 1 else ""
        if not query:
            print("Usage: sisyphus search QUERY")
            sys.exit(1)
        from sisyphus.tools.literature_client import search_all
        import json
        results = search_all(query)
        print(json.dumps(results, indent=2))
    elif command == "verify":
        if len(args) < 2:
            print("Usage: sisyphus verify FILE (or --citation CITATION)")
            sys.exit(1)
        if args[1] == "--citation":
            from sisyphus.tools.citation_verifier import verify_citation
            import json
            result = verify_citation("manual", " ".join(args[2:]))
            print(json.dumps(result, indent=2))
        else:
            from sisyphus.tools.citation_verifier import verify_citations
            import json
            with open(args[1]) as f:
                findings = json.load(f)
            result = verify_citations(findings)
            print(json.dumps(result, indent=2))
    elif command == "bibtex":
        if len(args) < 2:
            print("Usage: sisyphus bibtex DOI")
            sys.exit(1)
        from sisyphus.tools.citation_verifier import generate_bibtex
        bib = generate_bibtex({"doi": args[1], "title": "Untitled", "year": "n.d."})
        print(bib)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
