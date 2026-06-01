---
layout: default
title: Installation Guide
---

# Installation Guide

## Quick Install (Python package)

The Python CLI tools (literature search, citation verification, demo) install in one command:

<div class="demo-block">
  <div class="cmd"><span class="prompt">$</span> <span class="input">pip install sisyphus-academica</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">sisyphus demo</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">sisyphus configure</span></div>
</div>

<div class="info-box">
  <h4>No API keys needed to start</h4>
  <p>The <code class="language-plaintext highlighter-rouge">sisyphus demo</code> command runs entirely offline with built-in example data. Configure API keys only when you need live literature searches.</p>
</div>

## Full Pipeline Install (OpenCode agents)

For the complete 10-phase paper pipeline (literature review → novelty generation → writing → review → PDF), you need an agent platform:

<div class="demo-block">
  <div class="cmd"><span class="prompt">$</span> <span class="input">git clone https://github.com/argahv/sisyphus-academica.git</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">cd sisyphus-academica</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">bash install.sh</span></div>
</div>

Then open OpenCode, select the **research-director** agent, and type:

```
write a paper about [your topic]
```

## Portable Skills (any agent)

The novelty engines and reviewer personas work as standalone agent skills with any agent that reads the SKILL.md format (Claude Code, Codex, Cursor, Gemini CLI):

<div class="demo-block">
  <div class="cmd"><span class="prompt">$</span> <span class="input">git clone https://github.com/argahv/sisyphus-academica</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">cp -r skills/novelty-engines ~/.claude/skills/</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">cp -r skills/reviewers ~/.claude/skills/</span></div>
</div>

Then invoke in any agent:

```
/contrarian "The claim: 'Attention is all you need'"
/cross-pollinator "Problem: How to reduce LLM hallucination"
/heretic "Paper: 'Scaling Laws for Neural Language Models'"
```

## Requirements

| Component | Requirement |
|-----------|-------------|
| Python CLI tools | Python 3.10+ |
| Full pipeline | OpenCode (or compatible agent platform) |
| PDF output | LaTeX (optional — Docker image available) |
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
  <a href="https://github.com/argahv/sisyphus-academica/issues" class="btn-secondary">Report Issue</a>
</div>
