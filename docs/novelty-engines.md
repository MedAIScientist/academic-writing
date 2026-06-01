---
layout: default
title: Novelty Engines
---

# Novelty Engines

The novelty engines are the core differentiator. Each thinks from a completely different cognitive frame. They produce hypotheses that no human reviewer would generate, then score them for novelty and tractability.

<div class="engine-grid">
  <div class="engine-card">
    <div class="engine-icon">C</div>
    <h3>Contrarian</h3>
    <p class="tagline">"What if the field is wrong about one fundamental assumption?"</p>
    <p>Reads the literature, extracts every "well-established" claim, inverts it across 6 axes: polarity, direction, scope, relevance, existence, priority. Outputs 10 counter-hypotheses ranked by impact if true &times; plausibility.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">X</div>
    <h3>Cross-Pollinator</h3>
    <p class="tagline">"What does a completely unrelated field know about this problem?"</p>
    <p>Imports solutions from 15 unrelated fields: astrodynamics, epidemiology, portfolio theory, thermodynamics, linguistics, ecology, economics, neuroscience, materials science, music theory, urban planning, immunology, geology, philosophy of science. Extracts the mechanism, not the metaphor.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">A</div>
    <h3>Assumption Excavator</h3>
    <p class="tagline">"What unstated assumptions does every paper make?"</p>
    <p>Extracts assumptions at 3 levels: explicit (stated), implicit (never stated but present), foundational (so basic the field doesn't state them). Builds assumption trees and identifies the critical 1-3 that would cause catastrophic failure if false.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">G</div>
    <h3>Counterfactual Generator</h3>
    <p class="tagline">"What if the key paper had never been published?"</p>
    <p>Builds the field's history as a DAG, identifies branching points, rewrites history. Example: "What if the Transformer had failed on WMT 2014?" &rarr; No BERT, no GPT-1, LSTM research continues for years. Outputs 5 counterfactual histories with traced consequences.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">P</div>
    <h3>Paradox Sifter</h3>
    <p class="tagline">"What contradictions does everyone notice but nobody resolves?"</p>
    <p>Extracts every "Limitations" and "Future Work" sentence from the entire literature. Cross-references to find contradictions, elephants in the room, and paradoxes classified as: direct contradiction, mutual ignorance, hidden dependency, or escalation.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">H</div>
    <h3>Heretic (Crown Jewel)</h3>
    <p class="tagline">"What if I read only the title and abstract, then generated 50 wild guesses?"</p>
    <p>Reads ONLY the title and abstract. Generates 50 wild hypotheses in 5 categories (methodological, theoretical, empirical, foundational, wild cards). Then reads the full paper and scores each hypothesis. The <strong>Haunting Idea</strong> is the one the authors should have explored but didn't &ndash; novelty gap &ge; 8, tractability &ge; 5, impact &ge; 7, surprise &ge; 8.</p>
  </div>
</div>

## Example: Heretic Engine Output

**Input paper:** "Attention Is All You Need" (Vaswani et al., 2017)

**Haunting idea found:** "What if the attention mechanism's success is not due to attention at all, but due to the residual pathway allowing gradients to flow through 100+ layers? Any architecture with the same residual structure might perform equivalently."

| Metric | Score |
|--------|-------|
| Novelty Gap | 9/10 |
| Surprise Factor | 9/10 |
| Tractability | 7/10 |
| Potential Impact | 8/10 |
| **Overall** | **92.6** |

**Minimum experiment:** Compare a Transformer against a version with attention replaced by learned linear mixing (no pairwise interactions), keeping the residual structure identical. If performance gap &lt; 15%, the hypothesis is confirmed.

<div class="button-group">
  <a href="{{ '/pipeline' | relative_url }}" class="btn-secondary">Pipeline Phases</a>
  <a href="{{ '/agents' | relative_url }}" class="btn-secondary">Agent Catalog</a>
</div>
