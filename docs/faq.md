---
title: FAQ
nav_order: 8
---

# FAQ

## General

**Q: What is Sisyphus Academica?**
A self-coordinating pipeline of 20+ specialized agents that helps researchers find papers, generate novel hypotheses, verify citations, and improve writing quality. Not a paper mill — a research assistant.

**Q: Does this require a specific LLM provider?**
No. Works with any OpenAI-compatible or Anthropic API. Edit `config/agent-config.json` or set your provider in the environment.

**Q: Do I need OpenCode?**
The full 10-phase pipeline uses OpenCode's agent system, but the Python tools (`sisyphus search`, `sisyphus verify`) and portable skills (under `skills/`) work standalone with any agent or CLI.

**Q: Is there a demo I can try without installing anything?**
```bash
pip install sisyphus-academica
sisyphus demo
```

## Installation

**Q: How do I install?**
```bash
pip install sisyphus-academica
```
Or for the full pipeline: `git clone` + `bash install.sh` (requires OpenCode).

**Q: Is there a PyPI package?**
Yes: `pip install sisyphus-academica`. This installs the CLI tools (`sisyphus search`, `verify`, `bibtex`, `demo`, `configure`).

**Q: What about the portable skills?**
The `skills/` directory contains 6 novelty engines and 5 reviewer personas as standalone SKILL.md files. Copy them to `~/.claude/skills/` to use with any agent.

## Pipeline

**Q: How long does a paper take?**
30 minutes to 4 hours depending on LLM speed, literature volume, revision rounds.

**Q: Can I add my own template?**
Yes. See the [Contributing Guide](https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md).

## Novelty

**Q: What makes the novelty engines different from brainstorming?**
They think from cognitive frames no human naturally occupies: inverting field claims, importing from distant fields, rewriting history without key papers. Each engine follows a structured protocol with falsifiable outputs.

**Q: What if no novelty engine produces a useful hypothesis?**
The system reports "no novel angle found" and refuses to write the paper.

**Q: How many hypotheses do the engines generate?**
Up to 50 per engine per run, depending on the engine. The Heretic generates exactly 50 per paper.

## Quality

**Q: How reliable is citation verification?**
Every citation checked against 2+ sources (Semantic Scholar AND CrossRef). If neither source finds it, the paper is blocked.

**Q: How strict is AI-pattern detection?**
Very strict. Pattern density < 2 per 1000 words, with 41 patterns scanned. Zero em dashes allowed. One em dash = automatic failure.

**Q: What does "all 10 reviewers must pass" mean?**
All 10 personas must recommend acceptance. Even one rejection sends the paper back for revision.

## Development

**Q: How do I run tests?**
```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

**Q: How do I lint?**
```bash
pip install -e ".[dev]"
flake8 tools/ --max-line-length=100 --ignore=E501,W291
```

**Q: How do I contribute?**
See [CONTRIBUTING.md](https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md). Look for `good-first-issue` labels.
