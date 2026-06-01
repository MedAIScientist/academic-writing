# X/Twitter Thread — Launch Post
## Post at H+24 of launch window (Wednesday 9am PT)

---

**Tweet 1 (hook):**
We built a 20-agent AI swarm that writes research papers.
6 novelty engines. 10 adversarial reviewers. 0% hallucinated citations.
And it's open source. 🧵

**Tweet 2 (the problem):**
Existing AI paper tools have 3 unfixable problems:
1. ~40% citation hallucination rate
2. Zero original ideas (everyone asks "what's the gap?" the same way)
3. Post-hoc "humanization" that doesn't fool anyone

We designed a system that solves all three.

**Tweet 3 (citation verification):**
Every citation is checked against Semantic Scholar + CrossRef APIs.
Must be found in 2+ sources or it doesn't go in the paper.
26 citations in our SIREN paper. 0 hallucinated. 100% verified.
No other tool does this.

**Tweet 4 (novelty engines):**
6 novelty engines that think like no human researcher can:
- The Contrarian: inverts every field assumption
- The Cross-Pollinator: imports from astrodynamics, epidemiology, music theory
- The Heretic: reads ONLY title+abstract, generates 50 wild hypotheses about what the paper COULD be, then compares against reality

**Tweet 5 (the Haunting Idea):**
The Heretic finds the "haunting idea" — a hypothesis that:
- Wasn't explored in the paper
- COULD have been tested
- Would change the conclusions if true
- The authors never considered

It's the paper they SHOULD have written.

**Tweet 6 (anti-AI text):**
41 anti-AI-writing patterns enforced at generation time.
Not post-hoc cleanup. Every writer agent has the Humanizer skill as a hard constraint.
Zero em dashes. Zero significance inflation. Zero AI vocabulary.
The output passes as human-written on first pass.

**Tweet 7 (the reviewers):**
10 adversarial reviewer personas review every paper independently:
Theorist, Empiricist, Pragmatist, Skeptic, Historian, Methodologist, Ethicist, Competitor, Student, Dreamer

All 10 must recommend acceptance before formatting.
Our SIREN paper went from Avg 4.6 → 8.0 after 4 revision rounds.

**Tweet 8 (full pipeline):**
The complete pipeline:
Voice calibration → 5 parallel lit scouts (500+ papers) → 6 novelty engines (50+ hypotheses) → parallel writing (5 agents) → citation/stats/AI-pattern verification → 10 adversarial reviewers → style audit → LaTeX PDF

30 min to 4 hours per paper.

**Tweet 9 (open source):**
MIT licensed. Provider-agnostic (any OpenAI-compatible or Anthropic API).
Python CLI tools. Full example output included.

https://github.com/argahv/sisyphus-academica

**Tweet 10 (star CTA):**
If you write research papers, this will save you weeks.
Star the repo and try it on your next paper.

And if you've built something similar, I'd love to hear about it — drop a comment.

---

**Attachments to include:**
- Screenshot of the pipeline architecture diagram from README
- Screenshot of the comparison table (vs GPT-4/NotebookLM)
- Link to the SIREN paper PDF
- GIF of the pipeline executing (if available)

**Hashtags:** #opensource #ai #research #academic #llm #agents #multiagent
