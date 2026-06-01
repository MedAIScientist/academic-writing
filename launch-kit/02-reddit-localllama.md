# Reddit r/LocalLLaMA — Launch Post
## Post at H+0 of launch window (Tuesday 9am PT)

---

**Title:** Open-source paper-writing army: 20+ agents, 6 novelty engines, 10 adversarial reviewers — generates LaTeX PDFs with verified citations

**Body:**

We just open-sourced Sisyphus Academica — a multi-agent system that writes research papers. It's designed to solve three specific problems with existing AI paper tools:

1. **Citation hallucination** (~40% with current tools) → every citation verified against 2+ APIs before insertion
2. **Zero novelty** (every tool just asks "what's the gap?") → 6 novelty engines generate 50+ hypotheses from different cognitive frames
3. **Obvious AI-written text** (post-hoc "humanization") → 41 anti-AI-writing patterns enforced at generation time

**Architecture:**
- Research Director orchestrator deploys parallel subagents
- 5 literature scouts hit arXiv, Semantic Scholar, CrossRef, OpenAlex simultaneously
- 6 novelty engines (Contrarian, Cross-Pollinator, Assumption Excavator, Counterfactual Generator, Paradox Sifter, Heretic)
- Parallel writing swarm with Humanizer constraints
- 3-module verifier (citations, statistics, AI-patterns)
- 10 adversarial reviewer personas
- Style auditor → LaTeX formatter → PDF

**Provider-agnostic:** works with any OpenAI-compatible or Anthropic API. Edit one config file to switch between GPT-4o, Claude, Grok, etc.

**Live example:** We ran the full pipeline on a blockchain/AI paper. Output: 13-page PDF, 26 verified citations, 3 figures, 0 AI-isms. Full output in `examples/siren-paper/`.

https://github.com/argahv/sisyphus-academica

MIT. 30 min to 4 hours per paper depending on LLM speed and revision rounds.

---

**Comments strategy:**
- If asked about local models: mention the provider-agnostic config and that users can plug in local models via Ollama/vLLM
- If asked about OpenCode requirement: mention the Python CLI tools work standalone
- If asked about comparison to GPT-4 directly writing a paper: point to the hallucination stat and novelty engines
