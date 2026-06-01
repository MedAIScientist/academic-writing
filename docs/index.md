# Sisyphus Academica

**Not a writing assistant. Not a chatbot with a LaTeX plugin. A self-coordinating swarm of 20+ specialized agents that produces publication-ready research papers with genuine novelty, zero hallucinated citations, and no detectable AI-written patterns.**

---

## Quick Start

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
bash install.sh
cp .env.example .env
# Edit .env with your API keys
# Select "research-director" from agent tab
# Type: "write a paper about [topic]"
```

## Documentation

| Page | Description |
|------|-------------|
| [Architecture](architecture) | System design, component roles, data flow |
| [Pipeline Phases](pipeline) | All 10 phases: literature review → novelty → writing → review → PDF |
| [Agent Catalog](agents) | Every agent: orchestrator, subagents, novelty engines, reviewers |
| [Novelty Engines](novelty-engines) | Deep dive into all 6 novelty engines |
| [Adversarial Reviewers](reviewers) | All 10 reviewer personas with evaluation criteria |
| [Tool Reference](tools) | CLI docs for literature_client.py and citation_verifier.py |
| [Contributing](https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md) | How to contribute |
| [FAQ](faq) | Frequently asked questions |

## What Makes This Different

| Capability | Other AI Paper Tools | Sisyphus Academica |
|---|---|---|
| Literature review | 10-20 papers | **500+ papers via 5 parallel scouts** |
| Citation accuracy | ~60% (40% hallucination) | **100% verified against 2+ sources** |
| AI-sounding text | Post-hoc cleanup | **41 Humanizer patterns as generation constraints** |
| Voice calibration | None | **Learns author's voice from writing samples** |
| Novelty generation | "What's the gap?" | **6 novelty engines × counterfactual history × cross-domain mining** |
| Adversarial review | None | **10 distinct reviewer personas** |

## The Novelty Engines

1. **The Contrarian** — Inverts every well-established claim
2. **The Cross-Pollinator** — Imports solutions from 15 unrelated fields
3. **The Assumption Excavator** — Finds unstated assumptions, tests if false
4. **The Counterfactual Generator** — Rewrites the field's history without key papers
5. **The Paradox Sifter** — Cross-references "Limitations" sections for contradictions
6. **The Heretic** — Generates 50 wild hypotheses from title+abstract alone

## The Quality Gates

1. **Citation Verification** — Every citation checked against 2+ sources
2. **Statistical Audit** — Every p-value, effect size, sample size validated
3. **AI-Pattern Detection** — 41 patterns scanned, density < 2/1000 words
4. **Style Audit** — Zero em dashes, voice consistent with author
5. **Adversarial Review** — All 10 reviewer personas must accept

## Quick Links

- [GitHub Repository](https://github.com/argahv/sisyphus-academica)
- [Issues](https://github.com/argahv/sisyphus-academica/issues)
- [Discussions](https://github.com/argahv/sisyphus-academica/discussions)
- [Release Notes](https://github.com/argahv/sisyphus-academica/releases)
- [License: MIT](https://github.com/argahv/sisyphus-academica/blob/main/LICENSE)
