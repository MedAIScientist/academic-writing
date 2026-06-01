# Reddit r/MachineLearning — Launch Post
## Post at H+0 of launch window (Tuesday 9am PT)

---

**Title:** [P] We built a 20-agent swarm that writes research papers with 0% hallucinated citations and 6 novelty engines — here's the pipeline

**Body:**

We got tired of AI paper tools that hallucinate citations, sound obviously AI-written, and produce zero original ideas. Every tool does post-hoc cleanup of AI-isms. Every tool asks "what's the gap?" the same way. Every tool has a ~40% citation hallucination rate.

So we built Sisyphus Academica — a self-coordinating swarm of 20+ specialized agents that produces publication-ready research papers differently:

**What's different:**

1. **Citation verification, not generation** — every citation is checked against Semantic Scholar + CrossRef APIs. Must be found in 2+ sources or it doesn't go in the paper. We measured 0% hallucination rate on our SIREN paper (26 citations).

2. **6 novelty engines that think like no human can** — The Contrarian inverts field assumptions, The Cross-Pollinator imports solutions from astrodynamics/epidemiology/music theory, The Heretic generates 50 wild hypotheses from only the title+abstract then scores them against the actual paper to find the "haunting idea" (what the paper SHOULD have been).

3. **41 anti-AI-writing patterns enforced at generation time** — not post-hoc cleanup. Every writer agent has the Humanizer skill loaded as a hard constraint. Zero em dashes. Zero significance inflation. Zero AI vocabulary.

4. **10 adversarial reviewer personas** — Theorist, Empiricist, Skeptic, Competitor, Student, Dreamer, etc. All 10 must recommend acceptance before a paper is formatted. The SIREN paper went from Avg 4.6/10 → 8/10 across 4 revision rounds.

**Pipeline:** Research Director → 5 parallel literature scouts → 6 novelty engines (50+ hypotheses) → gap analyzer → parallel writing swarm (5 agents) → verifier (citations + stats + AI-patterns) → 10 adversarial reviewers → style auditor → LaTeX formatter → PDF.

**Full output example:** We ran it on "Intent-Based Blockchain Execution via Agentic RAG and Swarm Consensus" — 13-page PDF, 26 verified citations, 3 publication-ready figures, 0 AI-pattern violations, 0 em dashes, 0 hallucinated references. All in `examples/siren-paper/`.

**Stack:** OpenCode-compatible agent platform, provider-agnostic (any OpenAI-compatible or Anthropic API), Python CLI tools for literature search + citation verification.

MIT license. You can swap in any LLM backend.

https://github.com/argahv/sisyphus-academica

Happy to answer questions about the architecture, the Heretic engine's scoring methodology, or the adversarial review protocol.

---

**Comments strategy:**
- If someone asks "does this actually work?": link to the SIREN paper PDF and mention the 0% hallucination stat
- If someone asks about the Heretic: describe the "haunting idea" concept in detail
- If someone asks "how is this different from NotebookLM": point to the comparison table in README (novelty engines + adversarial review + citation verification)
- If someone asks about cost: explain it depends on LLM provider, but the pipeline is designed for efficiency
