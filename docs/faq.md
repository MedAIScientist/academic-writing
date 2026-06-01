---
layout: default
title: FAQ
---

# FAQ

## General

**Q: What is Sisyphus Academica?**
A self-coordinating pipeline of 20+ specialized agents that helps researchers find papers, generate novel hypotheses, verify citations, and improve writing quality.

**Q: Does this require a specific LLM provider?**
No. Works with any OpenAI-compatible or Anthropic API. Edit <code>config/agent-config.json</code> to switch models.

**Q: Do I need OpenCode?**
The full 10-phase pipeline uses OpenCode's agent system, but the Python tools (<code>sisyphus search</code>, <code>sisyphus verify</code>) and portable skills work standalone with any agent or CLI.

**Q: Is there a demo I can try without installing anything?**

```bash
git clone https://github.com/argahv/sisyphus-academica.git && cd sisyphus-academica && pip install -e .
sisyphus demo
```

## Installation

**Q: How do I install?**

```bash
git clone https://github.com/argahv/sisyphus-academica.git && cd sisyphus-academica && pip install -e .
```

Or for the full pipeline: <code>git clone</code> + <code>bash install.sh</code> (requires OpenCode).

**Q: Is there a PyPI package?**
Yes: <code>git clone https://github.com/argahv/sisyphus-academica.git && cd sisyphus-academica && pip install -e .</code>. This installs the CLI tools (<code>sisyphus search</code>, <code>verify</code>, <code>bibtex</code>, <code>demo</code>, <code>configure</code>).

**Q: What about the portable skills?**
The <code>skills/</code> directory contains 6 novelty engines and 5 reviewer personas as standalone SKILL.md files. Copy them to <code>~/.claude/skills/</code> to use with any agent.

## Pipeline

**Q: How long does a paper take?**
30 minutes to 4 hours depending on LLM speed, literature volume, and revision rounds.

**Q: What if no novelty engine produces a useful hypothesis?**
The system reports "no novel angle found" and refuses to write the paper.

## Quality

**Q: How reliable is citation verification?**
Every citation checked against 2+ sources (Semantic Scholar AND CrossRef). If neither source finds it, the paper is **blocked**.

**Q: How strict is AI-pattern detection?**
Very strict. Pattern density &lt; 1 per 2000 words. Zero em dashes allowed. One em dash = automatic failure.

**Q: What does "all 10 reviewers must pass" mean?**
All 10 personas must recommend acceptance. Even one rejection sends the paper back for revision.

## Development

**Q: How do I run tests?**

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

**Q: How do I contribute?**
See <a href="https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md">CONTRIBUTING.md</a>. Look for <code>good-first-issue</code> labels.
