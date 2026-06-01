---
layout: default
title: Agent Catalog
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

Also available as **17 standalone portable skills** under the <code>skills/</code> directory — install via <code>npx skills add argahv/sisyphus-academica</code>.

| Agent | Approach |
|-------|----------|
| **Contrarian** | Inverts field claims &rarr; 10 counter-hypotheses |
| **Cross-Pollinator** | Imports solutions from 15 distant fields |
| **Assumption Excavator** | Finds unstated assumptions, tests if false |
| **Counterfactual Generator** | Rewrites field history without key papers |
| **Paradox Sifter** | Cross-references Limitations sections for contradictions |
| **Heretic** | Crown jewel. 50 wild hypotheses from title+abstract alone. |

## Adversarial Reviewers

Standalone versions also in <code>skills/reviewers/</code>.

| Persona | Focus | Typical Critique |
|---------|-------|-----------------|
| Theorist | Formal proofs, mathematical rigor | "Where's the formal proof?" |
| Empiricist | Experimental design, baselines | "Your baseline is wrong" |
| Pragmatist | Practical applicability | "Does this matter in practice?" |
| Skeptic | Default: results are wrong | "Show me error bars" |
| Historian | Prior art, citation accuracy | "This was done in 1972" |
| Methodologist | Statistical methodology | "Your test assumes normality" |
| Ethicist | Societal implications | "What are the downsides?" |
| Competitor | Novelty relative to existing work | "Minor mod of our 2023 paper" |
| Student | Clarity and accessibility | "I don't understand section 3" |
| Dreamer | "What if you went further?" | "You stopped too early" |

## Skills (Portable)

The <code>skills/</code> directory contains 17 standalone SKILL.md files. Install with a single command:

```bash
npx skills add argahv/sisyphus-academica
```

Invoke in any agent:

```
/contrarian "The claim: 'Attention is all you need'"
/cross-pollinator "Problem: How to reduce LLM hallucination"
/heretic "Paper: 'Scaling Laws for Neural Language Models'"
```
