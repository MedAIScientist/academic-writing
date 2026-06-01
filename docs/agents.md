---
title: Agent Catalog
nav_order: 4
---

# Agent Catalog

Sisyphus Academica has 20+ agents organized into 5 groups.

## Orchestrator

| Agent | Role |
|-------|------|
| **Research Director** | Conducts the full 10-phase pipeline. Deploys subagents, collects results, loops on failure. |

## Subagents (Pipeline)

| Agent | Role |
|-------|------|
| **Literature Scout** | Multi-source literature search (arXiv, Semantic Scholar, CrossRef, OpenAlex) |
| **Gap Analyzer** | Identifies genuine research gaps from the literature corpus |
| **Methodology Designer** | Recommends statistical tests, power analysis, confound controls |
| **Data Engineer** | Writes analysis code, generates publication-ready figures |
| **Writer** | Writes paper sections with 41 Humanizer patterns as hard constraints |
| **Verifier** | 3-module verification: citations, statistics, AI-patterns |
| **Style Auditor** | Final Humanizer certification gate |
| **Formatter** | LaTeX template matching, BibTeX, PDF compilation |

## Novelty Engines

| Agent | Approach |
|-------|----------|
| **The Contrarian** | Inverts field claims → 10 counter-hypotheses |
| **The Cross-Pollinator** | Imports solutions from 15 distant fields |
| **The Assumption Excavator** | Finds unstated assumptions, tests if false |
| **The Counterfactual Generator** | Rewrites field history without key papers |
| **The Paradox Sifter** | Cross-references "Limitations" sections for contradictions |
| **The Heretic** | Generates 50 wild hypotheses from title+abstract alone |

These are also available as **standalone portable skills** in the `skills/novelty-engines/` directory — copy them to `~/.claude/skills/` and use with any agent.

## Adversarial Reviewers

| Persona | Focus |
|---------|-------|
| Theorist | Formal proofs, mathematical rigor |
| Empiricist | Experimental design, baselines |
| Pragmatist | Practical applicability |
| Skeptic | "Your results are wrong" |
| Historian | Prior art, citation accuracy |
| Methodologist | Statistical correctness |
| Ethicist | Societal implications |
| Competitor | Novelty relative to existing work |
| Student | Clarity and accessibility |
| Dreamer | "What if you went further?" |

Standalone versions also in `skills/reviewers/`.

## Skills (Portable)

The `skills/` directory contains standalone SKILL.md files for 6 novelty engines and 5 reviewer personas. These work with any agent that reads the SKILL.md format (Claude Code, Codex, Cursor, Gemini CLI, etc.).

To use:

```bash
cp -r skills/novelty-engines ~/.claude/skills/
cp -r skills/reviewers ~/.claude/skills/
```

Then invoke in any agent:

```
/contrarian "The claim: 'Attention is all you need'"
/cross-pollinator "Problem: How to reduce LLM hallucination"
/heretic "Paper: 'Scaling Laws for Neural Language Models'"
```
