<div align="center">

# Sisyphus Academica

**Open-source research pipeline — literature review, novelty generation, citation verification, and adversarial review.**

[![CI](https://github.com/argahv/sisyphus-academica/actions/workflows/ci.yml/badge.svg)](https://github.com/argahv/sisyphus-academica/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)
[![GitHub Stars](https://img.shields.io/github/stars/argahv/sisyphus-academica?style=social)](https://github.com/argahv/sisyphus-academica)

</div>

A self-coordinating pipeline of 20+ specialized agents that helps researchers find papers, generate novel hypotheses, verify citations, and improve writing quality.

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e .
academica demo
```

---

## What It Does

| Task | Without Sisyphus | With Sisyphus |
|------|------------------|---------------|
| Literature review | Read 10-50 papers manually | Scouts 400+ across 4 APIs in parallel |
| Citation checking | Trust the author | Verified against Semantic Scholar + CrossRef |
| Novel ideas | "What's the gap?" | 6 engines generate 50+ structured hypotheses |
| Writing quality | Post-hoc AI detection | 41 Humanizer patterns enforced during generation |
| Peer review | Wait months for reviewers | 10 adversarial personas review in parallel |

**SIREN paper output** ([view full example](examples/siren-paper/)): 13-page PDF, 26 verified citations, 3 figures, 0 hallucinated references, 0 AI-pattern violations.

---

## Quick Start

### Python CLI tools

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e .

academica demo              # Interactive pipeline demo (no API keys)
academica search QUERY      # Search 4 academic APIs in parallel
academica verify FILE       # Verify citations in a paper JSON
academica bibtex DOI        # Generate BibTeX from DOI
academica configure         # Set up API keys interactively
```

### Portable agent skills (any agent)

```bash
git clone https://github.com/argahv/sisyphus-academica
cp -r skills/novelty-engines ~/.claude/skills/
cp -r skills/reviewers ~/.claude/skills/
```

```
/contrarian "The claim: 'Attention is all you need'"
/cross-pollinator "Problem: How to reduce LLM hallucination"
```

### Full paper pipeline (requires OpenCode)

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
bash install.sh
# OpenCode → agent tab → select "research-director"
# → "write a paper about transformer efficiency"
```

---

## What You Get

### 6 Novelty Engines

| Engine | What it does | Best for |
|--------|-------------|----------|
| **Contrarian** | Inverts every well-established claim — 10 counter-hypotheses | Breaking consensus thinking |
| **Cross-Pollinator** | Imports solutions from 15 distant fields | Stuck problems |
| **Assumption Excavator** | Finds unstated assumptions, tests if false | Design reviews |
| **Counterfactual Generator** | Rewrites field history without key papers | Overlooked approaches |
| **Paradox Sifter** | Cross-references Limitations sections for contradictions | Literature gaps |
| **Heretic** | 50 wild hypotheses from title+abstract, scores vs reality | Breakthrough ideas |

### 10 Adversarial Reviewers

| Persona | Focus | Typical Critique |
|---------|-------|-----------------|
| Theorist | Formal proofs | "Where's the formal proof?" |
| Empiricist | Experimental design | "Your baseline is wrong" |
| Pragmatist | Practical applicability | "Does this matter in practice?" |
| Skeptic | Default: results are wrong | "Show me error bars" |
| Historian | Prior art | "This was done in 1972" |
| Methodologist | Statistical methodology | "Your test assumes normality" |
| Ethicist | Societal implications | "What are the downsides?" |
| Competitor | Novelty relative to existing work | "Minor mod of our 2023 paper" |
| Student | Clarity | "I don't understand section 3" |
| Dreamer | "What if you went further?" | "You stopped too early" |

---

## Quality Gates

Every paper passes 5 gates. If any fails, it goes back to revision.

1. **Citation Verification** — Every reference checked against Semantic Scholar + CrossRef. 2+ sources.
2. **Statistical Audit** — Every p-value, effect size, sample size validated.
3. **AI-Pattern Detection** — 41 patterns scanned (30 base + 11 academic). Density < 2/1000 words.
4. **Style Audit** — Zero em dashes. Voice matches author's profile.
5. **Adversarial Review** — All 10 reviewer personas must recommend acceptance.

---

## Development

```bash
git clone https://github.com/argahv/sisyphus-academica.git
cd sisyphus-academica
pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

## Project Structure

```
sisyphus-academica/
├── orchestrator/          # Research Director agent
├── subagents/             # Writing pipeline agents
├── novelty-engines/       # 6 novelty generation engines
├── reviewers/             # 10 adversarial reviewer personas
├── skills/                # Standalone skill files (portable)
├── tools/                 # Python CLI toolchain
├── templates/             # LaTeX venue templates
├── examples/siren-paper/  # Full pipeline output (13-page paper)
├── tests/                 # Python unit tests
└── docs/                  # GitHub Pages documentation
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
