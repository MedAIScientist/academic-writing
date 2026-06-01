# Hacker News — Show HN Post
## Post at H+6 of launch window (Tuesday 3pm PT)

---

**Title:** Show HN: Sisyphus Academica — 20-agent swarm that writes research papers with verified citations and zero AI-isms

**Body:**

I've been working on this for a while and finally open-sourced it.

The problem with AI paper tools is that they hallucinate citations (~40% rate in our tests), produce obviously AI-written text, and generate zero novel ideas. Every tool does post-hoc cleanup of AI patterns. None verify citations against real sources. None try to generate original hypotheses.

Sisyphus Academica approaches this differently — it's a self-coordinating swarm of 20+ specialized agents. Here's what makes it different from everything else out there:

**No citation hallucinations.** Every reference is checked against Semantic Scholar and CrossRef APIs. Must be found in 2+ sources or it doesn't go in the paper. Our SIREN paper had 26 citations, all verified, zero hallucinations.

**6 novelty engines.** Instead of "what's the gap?", the system deploys 6 agents that think from completely different angles. The Heretic (crown jewel) reads only the title and abstract, generates 50 wild hypotheses about what the paper COULD contain, then compares each against the actual paper. The gap between what it IS and what it COULD HAVE BEEN is where the next paper lives.

**41 anti-AI-writing constraints at generation time.** Not post-hoc cleanup. Every writer agent has the Humanizer skill loaded as a hard constraint. The output passes as human-written on first pass.

**10 adversarial reviewers.** The paper is independently reviewed by 10 personas (Theorist, Empiricist, Skeptic, Competitor, Dreamer, etc.). All 10 must pass before formatting. Our SIREN paper went from an average of 4.6/10 to 8/10 across 4 revision rounds.

**The full pipeline:**
1. Voice calibration (learns author's writing style)
2. 5 parallel literature scouts (500+ papers)
3. 6 novelty engines (50+ hypotheses)
4. Hypothesis selection + methodology design
5. Parallel writing (5 agents, Humanizer-constrained)
6. 3-module verification (citations, stats, AI-patterns)
7. 10-persona adversarial review
8. Style audit → LaTeX → PDF

The whole thing is MIT licensed, provider-agnostic (works with any OpenAI-compatible or Anthropic API), and takes 30 minutes to 4 hours per paper.

Stack: OpenCode-compatible agent platform, Python CLI tools.

GitHub: https://github.com/argahv/sisyphus-academica

I'll be in the comments for the next few hours if anyone wants to discuss the architecture, the novelty engine design, or the verification protocol.

---

**Timing note:** Post at 3pm PT = 6pm ET = midnight CET. This captures US afternoon peak + European evening. Stay in comments for 12+ hours.

**Comments strategy:**
- Technical HN audience — they'll want details about the verification methodology, the agent orchestration, and the Heretic's scoring algorithm
- Be transparent about limitations (stub templates, requires OpenCode)
- Answer "show me the output" with the SIREN paper link
- If someone asks "how is this not just prompt chains?" — explain the verification gates and the multi-source citation verification
