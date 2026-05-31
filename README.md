# MedAI Academic Writing — The Research Paper Writing Army

Highly inspired by https://github.com/argahv/sisyphus-academica 

**Not a writing assistant. Not a chatbot with a LaTeX plugin. A self-coordinating swarm of 20+ specialized agents that produces publication-ready research papers with genuine novelty, zero hallucinated citations, and absolutely no detectable AI-written patterns.**

## What Makes This Different

| Capability | Every Other AI Paper Tool | MedAI Academic Writing |
|---|---|---|
| Literature review | Searches 10-20 papers | **500+ papers via 5 parallel scouts** |
| Citation accuracy | ~60% (40% hallucination rate) | **100% verified against 2+ sources** |
| AI-sounding text | Post-hoc cleanup | **41 Humanizer patterns as generation constraints from token 1** |
| Voice calibration | None | **Learns author's voice from writing samples** |
| Novelty generation | "What's the gap?" (same as everyone) | **6 novelty engines × counterfactual history × cross-domain mining × assumption excavation** |
| Adversarial review | None | **10 distinct reviewer personas** |
| Thinking angles | 1 perspective | **Infinite parallel perspectives including the Heretic** |

## Architecture

```
                     ┌──────────────────────────────┐
                     │  Research Director            │
                     │  (orchestrator)               │
                     └────────┬─────────────────────┘
                              │
         ┌────────────────────┼─────────────────────────┐
         ▼                    ▼                          ▼
   ┌───────────┐    ┌────────────────┐    ┌──────────────────────┐
   │ Literature│    │ 6 Novelty      │    │ Gap Analyzer         │
   │ Scout ×5  │    │ Engines        │    │ + Methodology        │
   └───────────┘    └────────────────┘    └──────────────────────┘
                              │
         ┌────────────────────┼─────────────────────────┐
         ▼                    ▼                          ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  Parallel Writing Swarm (5 agents + 41 Humanizer patterns)   │
   └──────────────────────────┬──────────────────────────────────┘
                              │
   ┌─────────────────────────────────────────────────────────────┐
   │  Verifier: Citations × Statistics × AI-Pattern Detection    │
   └──────────────────────────┬──────────────────────────────────┘
                              │
   ┌─────────────────────────────────────────────────────────────┐
   │  Adversarial Review: 10 reviewer personas (parallel)        │
   └──────────────────────────┬──────────────────────────────────┘
                              │
   ┌─────────────────────────────────────────────────────────────┐
   │  Style Auditor: Humanizer certification, em dash zero check │
   └──────────────────────────┬──────────────────────────────────┘
                              │
   ┌─────────────────────────────────────────────────────────────┐
   │  Formatter: LaTeX template, BibTeX, figures, PDF            │
   └─────────────────────────────────────────────────────────────┘
```

## The Novelty Engines (The Moat)

Six engines that think like no human can:

1. **The Contrarian** — Inverts every well-established claim in the field
2. **The Cross-Pollinator** — Imports solutions from 15 completely unrelated fields
3. **The Assumption Excavator** — Finds unstated assumptions and tests what breaks if they're false
4. **The Counterfactual Generator** — Rewrites the field's history without key papers
5. **The Paradox Sifter** — Cross-references every "Limitations" section to find ignored contradictions
6. **The Heretic** — **Crown jewel.** Generates 50 wild hypotheses from title+abstract alone, then scores them against the actual paper

## The Adversarial Reviewers

Each paper is independently reviewed by 10 distinct personas running in parallel:
- Theorist, Empiricist, Pragmatist, Skeptic, Historian, Methodologist, Ethicist, Competitor, Student, Dreamer

All 10 must pass before the paper proceeds to formatting.

## Quality Gates

1. **Citation Verification**: Every citation checked against 2+ sources
2. **Statistical Audit**: Every p-value, effect size, and sample size validated
3. **AI-Pattern Detection**: 41 Humanizer patterns scanned. Density must be < 2/1000 words
4. **Style Audit**: Zero em dashes allowed. Pattern density < 1/2000 words. Voice must match author profile
5. **Adversarial Review**: All 10 reviewer personas must recommend acceptance

## Quick Start

```bash
# Install
cd /root/sisyphus-academica
bash install.sh

# Start a paper
# Select research-director from the OpenCode agent tab
# Then say: "write a paper about [topic]"

# Or run the pipeline manually:
python3 tools/literature_client.py "transformer efficiency" --output papers/literature.json
python3 tools/citation_verifier.py --findings papers/draft.json --output papers/verified.json
```

## Tooling Upgrades

### Literature Client

The literature client now supports stronger deduplication, environment-aware API headers,
paper ranking, filtering, and markdown report export.

```bash
# Top-50 recent papers from 2021+, plus markdown summary
python3 tools/literature_client.py "retrieval augmented generation" \
      --max-per-source 120 \
      --since-year 2021 \
      --top 50 \
      --output out/papers/literature.json \
      --report-md out/papers/literature-report.md
```

### Citation Verifier

The verifier now extracts citations from manuscript text context (not empty claims),
supports strict two-source validation, and exposes configurable title match thresholds.

```bash
# Verify markdown manuscript with strict 2-source checks
python3 tools/citation_verifier.py \
      --text-file out/papers/draft.md \
      --strict-two-source \
      --min-match-score 0.50 \
      --output out/papers/citation-audit.json
```

Use `.env` values from `.env.example` for `SEMANTIC_SCHOLAR_API_KEY` and
`CROSSREF_EMAIL` to improve API reliability and rate limits.

## Directory Structure

```
sisyphus-academica/
├── orchestrator/          # Research Director agent
├── subagents/             # Core writing pipeline agents
├── novelty-engines/       # 6 novelty generation agents
├── reviewers/             # 10 adversarial reviewer personas
├── skills/                # Academic Humanizer skill (extends blader/humanizer)
├── tools/                 # Python toolchain
├── templates/             # LaTeX venue templates
├── config/                # Agent config + settings
├── data/                  # Research memory + voice profiles
└── out/                   # Generated papers and figures
```

## Acknowledgments

- **Humanizer** by blader — the 30-pattern AI-detection skill this system builds on
- **OpenCode** + **OhMyOpenAgent** — the agent orchestration platform
