---
layout: default
title: Tool Reference
---

# Tool Reference

## sisphyus CLI

The <code>sisyphus</code> command provides access to all pipeline tools:

| Command | Description |
|---------|-------------|
| <code>sisyphus demo</code> | Run demo with built-in example data (no API keys) |
| <code>sisyphus configure</code> | Interactive API key setup |
| <code>academica search QUERY</code> | Search literature across 4 APIs |
| <code>academica verify FILE</code> | Verify citations in a paper JSON file |
| <code>academica bibtex DOI</code> | Generate BibTeX entry from a DOI |

## literature_client.py

Multi-source literature search aggregator. Queries arXiv, Semantic Scholar, CrossRef, and OpenAlex in parallel.

```bash
python3 tools/literature_client.py "transformer efficiency" --output papers/literature.json
```

**Sources:**

| Source | Max Results | API |
|--------|-------------|-----|
| arXiv | Up to 200 | OAI-PMH |
| Semantic Scholar | Up to 100 | REST API |
| CrossRef | Up to 50 | REST API |
| OpenAlex | Up to 50 | REST API |

**Arguments:**

| Arg | Description |
|-----|-------------|
| <code>query</code> | Search query (positional, required) |
| <code>-o, --output</code> | Output JSON file path |

## citation_verifier.py

Verifies citations against Semantic Scholar and CrossRef. Blocks papers with hallucinated references.

```bash
python3 tools/citation_verifier.py --findings papers/draft.json --output papers/verified.json
python3 tools/citation_verifier.py --citation "Attention is all you need"
```

**Verification process:**

1. Extract citations from <code>[bracket]</code> notation in the paper text
2. Search Semantic Scholar API
3. Search CrossRef API
4. If found in 2+ sources: **verified**
5. If found in 1 source: **weak verification** (flagged)
6. If found in 0 sources: **hallucinated** (blocks submission)

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | All citations verified |
| 1 | Unverifiable citations found (paper blocked) |
