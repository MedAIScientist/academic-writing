---
layout: default
title: Installation Guide
---

# Installation Guide

## Python CLI Tools

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e .

sisyphus demo              # Interactive pipeline demo (no API keys needed)
sisyphus search QUERY      # Search 4 academic APIs in parallel
sisyphus verify FILE       # Verify citations in a paper JSON
sisyphus bibtex DOI        # Generate BibTeX from a DOI
sisyphus configure         # Set up API keys interactively
```

## Agent Skills (Any Agent)

Install via the standard skills CLI:

```bash
npx skills add argahv/sisyphus-academica          # Browse and select
npx skills add argahv/sisyphus-academica -s '*'   # Install all 17
npx skills add argahv/novelty-skills               # Standalone thinking tools
```

Or clone and copy manually:

```bash
git clone https://github.com/argahv/sisyphus-academica
cp -r skills/contrarian ~/.claude/skills/
```

## Full Paper Pipeline (OpenCode)

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
bash install.sh
```

Select "research-director" from the agent tab and type: `write a paper about [topic]`

## Requirements

| Component | Requirement |
|-----------|-------------|
| Python CLI tools | Python 3.10+ |
| Full pipeline | OpenCode (or compatible agent platform) |
| PDF output | LaTeX (optional — Docker image) |
| Literature search | Semantic Scholar API key (free, recommended) |

## Development

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e ".[dev]"
python -m pytest tests/ -v
```

<div class="button-group">
  <a href="https://github.com/argahv/sisyphus-academica" class="btn-primary">GitHub Repository</a>
  <a href="https://github.com/argahv/novelty-skills" class="btn-secondary">Novelty Skills</a>
</div>
