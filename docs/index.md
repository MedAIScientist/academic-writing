---
layout: default
title: Home
---

<div class="hero">
  <h1>Open-source research pipeline</h1>
  <p class="subhead">Literature review, novelty generation, citation verification, and adversarial review. A self-coordinating pipeline of 20+ specialized agents for researchers.</p>
  <div class="button-group">
    <a href="https://github.com/argahv/sisyphus-academica" class="btn-primary btn-large">View on GitHub</a>
    <a href="https://github.com/argahv/novelty-skills" class="btn-secondary btn-large">Novelty Skills</a>
  </div>
</div>

## Quick Start

<div class="demo-block">
  <div class="cmd"><span class="prompt">$</span> <span class="input">pip install sisyphus-academica</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">academica demo</span></div>
  <div class="output">Running pipeline on example topic: 'Transformer Efficiency' ...</div>
  <div class="cmd" style="margin-top:var(--space-sm)"><span class="prompt">$</span> <span class="input">academica search "transformer efficiency"</span></div>
</div>

<p>Or use the novelty engines as standalone agent skills — no install needed:</p>

<div class="demo-block">
  <div class="cmd"><span class="prompt">$</span> <span class="input">cp -r skills/novelty-engines ~/.claude/skills/</span></div>
  <div class="cmd"><span class="prompt">$</span> <span class="input">cp -r skills/reviewers ~/.claude/skills/</span></div>
</div>

<p>Compatible with <strong>Claude Code, Codex, Cursor, Gemini CLI</strong>, and any agent that reads SKILL.md.</p>

<hr class="section">

## What Makes This Different

<div class="comparison-wrap">
<table>
  <thead>
    <tr><th>Capability</th><th>Other AI Paper Tools</th><th>Sisyphus Academica</th></tr>
  </thead>
  <tbody>
    <tr><td>Literature review</td><td>10-20 papers</td><td><strong>500+ papers via 5 parallel scouts</strong></td></tr>
    <tr><td>Citation accuracy</td><td>~60% (40% hallucination)</td><td><strong>100% verified against 2+ sources</strong></td></tr>
    <tr><td>AI-sounding text</td><td>Post-hoc cleanup</td><td><strong>41 Humanizer patterns as generation constraints</strong></td></tr>
    <tr><td>Voice calibration</td><td>None</td><td><strong>Learns author's voice from writing samples</strong></td></tr>
    <tr><td>Novelty generation</td><td>"What's the gap?"</td><td><strong>6 novelty engines × counterfactual history × cross-domain mining</strong></td></tr>
    <tr><td>Adversarial review</td><td>None</td><td><strong>10 distinct reviewer personas</strong></td></tr>
  </tbody>
</table>
</div>

<hr class="section">

## The Novelty Engines

<div class="engine-grid">
  <div class="engine-card">
    <div class="engine-icon">🔄</div>
    <h3>Contrarian</h3>
    <p class="tagline">Invert every well-established claim</p>
    <p>Generates 10 counter-hypotheses by inverting claims across 6 axes: polarity, direction, scope, relevance, existence, priority.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">🦋</div>
    <h3>Cross-Pollinator</h3>
    <p class="tagline">Solutions from 15 distant fields</p>
    <p>Maps concepts from astrodynamics onto biology, from monetary policy onto ML. Extract the mechanism, not the metaphor.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">🔍</div>
    <h3>Assumption Excavator</h3>
    <p class="tagline">Find what everyone assumed</p>
    <p>Surfaces resource, behavioral, environmental, temporal, and causal assumptions. Tests what breaks if each is false.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">⏳</div>
    <h3>Counterfactual Generator</h3>
    <p class="tagline">The field without its key papers</p>
    <p>Removes the most-cited papers from history. Traces ripple effects. Finds suppressed alternatives that deserve a second look.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">🎭</div>
    <h3>Paradox Sifter</h3>
    <p class="tagline">Contradictions everyone ignores</p>
    <p>Cross-references Limitations sections across papers. Finds direct contradictions, mutual ignorance, hidden dependencies, and escalations.</p>
  </div>

  <div class="engine-card">
    <div class="engine-icon">🔥</div>
    <h3>Heretic</h3>
    <p class="tagline">50 wild hypotheses from any abstract</p>
    <p>The crown jewel. Generates 50 hypotheses from title+abstract alone, scores against the actual paper, finds the haunting idea.</p>
  </div>
</div>

<hr class="section">

## The Quality Gates

<div class="gate-list">
  <div class="gate-item">
    <span class="num">1</span>
    <span><strong>Citation Verification</strong> — Every reference checked against Semantic Scholar + CrossRef. Must be found in 2+ sources. No exceptions.</span>
  </div>
  <div class="gate-item">
    <span class="num">2</span>
    <span><strong>Statistical Audit</strong> — Every p-value, effect size, sample size, and test selection validated. No p-hacking, no multiple comparison errors.</span>
  </div>
  <div class="gate-item">
    <span class="num">3</span>
    <span><strong>AI-Pattern Detection</strong> — 41 Humanizer patterns scanned. Density must be &lt; 2 violations per 1000 words.</span>
  </div>
  <div class="gate-item">
    <span class="num">4</span>
    <span><strong>Style Audit</strong> — Zero em dashes. Voice must match the author's writing profile.</span>
  </div>
  <div class="gate-item">
    <span class="num">5</span>
    <span><strong>Adversarial Review</strong> — All 10 reviewer personas must recommend acceptance. Not a subset. All 10.</span>
  </div>
</div>

<hr class="section">

## Pipeline Overview

<div class="arch-diagram">                     ┌──────────────────────────────┐
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
   └──────────────────────────┬──────────────────────────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │  Paper   │
                        │  PDF     │
                        └──────────┘</div>

<hr class="section">

## Project Structure

```
sisyphus-academica/
├── orchestrator/          # Research Director agent
├── subagents/             # Writing pipeline agents (writer, verifier, etc.)
├── novelty-engines/       # 6 novelty generation agents
├── reviewers/             # 10 adversarial reviewer personas
├── skills/                # Standalone skill files (portable)
├── tools/                 # Python CLI toolchain
├── templates/             # LaTeX venue templates
├── config/                # Agent configuration
├── examples/siren-paper/  # Full pipeline output (13-page paper)
├── tests/                 # Python unit tests
└── docs/                  # This documentation site
```

<div class="button-group">
  <a href="{{ '/guide/installation' | relative_url }}" class="btn-primary">Installation Guide</a>
  <a href="{{ '/architecture' | relative_url }}" class="btn-secondary">Architecture</a>
  <a href="{{ '/novelty-engines' | relative_url }}" class="btn-secondary">Novelty Engines</a>
</div>
