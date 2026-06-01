---
title: Home
nav_order: 1
---

# Sisyphus Academica

**Open-source research pipeline — literature review, novelty generation, citation verification, and adversarial review.**

A self-coordinating pipeline of 20+ specialized agents that helps researchers find papers, generate novel hypotheses, verify citations, and improve writing quality.

---

## Quick Start

### One command (recommended)

```bash
pip install sisyphus-academica
sisyphus demo     # See the pipeline in action (no API keys needed)
sisyphus write "transformer efficiency"   # Full pipeline
```

### Without installing (portable skills)

```bash
git clone https://github.com/argahv/sisyphus-academica
cp -r skills/novelty-engines ~/.claude/skills/
cp -r skills/reviewers ~/.claude/skills/
```

These skills work with Claude Code, Codex, Cursor, Gemini CLI, and any agent that reads SKILL.md.

### Full pipeline (requires agent platform)

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
bash install.sh
# Select "research-director" → "write a paper about [topic]"
```

---

## Documentation

| Page | Description |
|------|-------------|
| [Installation Guide](guide/installation) | Step-by-step setup guide |
| [Architecture](architecture) | System design, component roles, data flow |
| [Pipeline Phases](pipeline) | All 10 phases: literature → novelty → writing → review → PDF |
| [Agent Catalog](agents) | Every agent: orchestrator, subagents, novelty engines, reviewers |
| [Novelty Engines](novelty-engines) | Deep dive into all 6 novelty engines |
| [Adversarial Reviewers](reviewers) | All 10 reviewer personas with evaluation criteria |
| [Tool Reference](tools) | CLI docs for sisyphus command, literature_client, citation_verifier |
| [FAQ](faq) | Frequently asked questions |

---

## What Makes This Different

| Capability | Other AI Paper Tools | Sisyphus Academica |
|---|---|---|
| Literature review | 10-20 papers | **500+ papers via 5 parallel scouts** |
| Citation accuracy | ~60% (40% hallucination) | **100% verified against 2+ sources** |
| AI-sounding text | Post-hoc cleanup | **41 Humanizer patterns as generation constraints** |
| Voice calibration | None | **Learns author's voice from writing samples** |
| Novelty generation | "What's the gap?" | **6 novelty engines × counterfactual history × cross-domain mining** |
| Adversarial review | None | **10 distinct reviewer personas** |

---

## The Novelty Engines

1. **The Contrarian** — Inverts every well-established claim, generates 10 counter-hypotheses
2. **The Cross-Pollinator** — Imports solutions from 15 distant fields (astrodynamics → biology, monetary policy → ML)
3. **The Assumption Excavator** — Finds unstated assumptions and tests what breaks if false
4. **The Counterfactual Generator** — Rewrites the field's history without the most-cited papers
5. **The Paradox Sifter** — Cross-references "Limitations" sections to find contradictions
6. **The Heretic** — Generates 50 wild hypotheses from title+abstract alone, finds the "haunting idea"

---

## The Quality Gates

1. **Citation Verification** — Every citation checked against Semantic Scholar + CrossRef. No exceptions.
2. **Statistical Audit** — Every p-value, effect size, sample size validated. No p-hacking.
3. **AI-Pattern Detection** — 41 Humanizer patterns scanned. Density < 2/1000 words.
4. **Style Audit** — Zero em dashes. Voice consistent with author's profile.
5. **Adversarial Review** — All 10 reviewer personas must recommend acceptance.

---

## Quick Links

- [GitHub Repository](https://github.com/argahv/sisyphus-academica)
- [Issues](https://github.com/argahv/sisyphus-academica/issues)
- [Discussions](https://github.com/argahv/sisyphus-academica/discussions)
- [Release Notes](https://github.com/argahv/sisyphus-academica/releases)
- [License: MIT](https://github.com/argahv/sisyphus-academica/blob/main/LICENSE)
