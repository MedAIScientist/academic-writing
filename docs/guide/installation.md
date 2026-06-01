---
title: Installation Guide
nav_order: 0
---

# Sisyphus Academica — Installation Guide

**Open-source research pipeline — literature review, novelty generation, citation verification, and adversarial review.**

---

## Quick Install (Python package)

```bash
pip install sisyphus-academica
```

Then try the demo (no API keys needed):

```bash
sisyphus demo
```

Configure your literature search keys:

```bash
sisyphus configure
```

Search papers:

```bash
sisyphus search "transformer efficiency"
```

## Full Pipeline Install (OpenCode agents)

Requires a model provider (OpenAI, Anthropic, or any OpenAI-compatible API):

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
bash install.sh
```

Then: `opencode → agent tab → select "research-director"` → type `write a paper about [topic]`

## Portable Skills (any agent)

The novelty engines and reviewer personas work as standalone agent skills:

```bash
git clone https://github.com/argahv/sisyphus-academica
cp -r skills/novelty-engines ~/.claude/skills/
cp -r skills/reviewers ~/.claude/skills/
```

Compatible with Claude Code, Codex, Cursor, Gemini CLI, and any agent that reads SKILL.md.

## Development

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Requirements

- Python 3.10+
- For full pipeline: OpenCode (or compatible agent platform)
- For PDF output: LaTeX (optional — Docker image available)

## Need Help?

- [Open an issue](https://github.com/argahv/sisyphus-academica/issues)
- [Start a discussion](https://github.com/argahv/sisyphus-academica/discussions)
