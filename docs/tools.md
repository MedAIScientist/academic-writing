---
title: Tool Reference
nav_order: 7
---

# Tool Reference

## sisyphus CLI

The `sisyphus` command provides access to all pipeline tools:

```bash
sisyphus demo              # Run demo (no API keys needed)
sisyphus configure         # Interactive API key setup
sisyphus search QUERY      # Search literature (arXiv, S2, CrossRef, OpenAlex)
sisyphus verify FILE       # Verify citations in a paper JSON file
sisyphus bibtex DOI        # Generate BibTeX entry from a DOI
```

## literature_client.py

Multi-source literature search aggregator (arXiv, Semantic Scholar, CrossRef, OpenAlex).

```bash
python3 tools/literature_client.py "transformer efficiency" --output papers/literature.json
# Or via sisyphus CLI:
sisyphus search "transformer efficiency"
```

### Sources

| Source | Max Results | API |
|--------|-------------|-----|
| arXiv | Up to 200 | OAI-PMH |
| Semantic Scholar | Up to 100 | REST API |
| CrossRef | Up to 50 | REST API |
| OpenAlex | Up to 50 | REST API |

All sources are queried in parallel via ThreadPoolExecutor.

### Output

```json
{
  "query": "transformer efficiency",
  "total_raw": 400,
  "total_unique": 310,
  "by_source": { "arxiv": 200, "semantic_scholar": 100, "crossref": 50, "openalex": 50 },
  "papers": [
    {
      "title": "Efficient Transformers: A Survey",
      "authors": ["Tay, Y.", "Dehghani, M."],
      "year": 2022,
      "citation_count": 450,
      "doi": "10.1145/3530811"
    }
  ]
}
```

### Arguments

| Arg | Description |
|-----|-------------|
| `query` | Search query (positional, required) |
| `-o, --output` | Output JSON file path |

## citation_verifier.py

Verifies citations against Semantic Scholar and CrossRef. Blocks papers with hallucinated references.

```bash
python3 tools/citation_verifier.py --findings papers/draft.json --output papers/verified.json
python3 tools/citation_verifier.py --citation "Attention is all you need"
# Or via sisyphus CLI:
sisyphus verify --citation "Attention is all you need"
```

### Verification Process

1. Extract citations from `[bracket]` notation in the paper text
2. Search Semantic Scholar API
3. Search CrossRef API
4. If found in 2+ sources → **verified**
5. If found in 1 source → **weak verification** (flagged)
6. If found in 0 sources → **hallucinated** (blocks submission)

### Arguments

| Arg | Description |
|-----|-------------|
| `-f, --findings` | Findings JSON file with paper text |
| `-o, --output` | Output verification report |
| `-c, --citation` | Verify a single citation string |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All citations verified |
| 1 | Unverifiable citations found (paper blocked) |
