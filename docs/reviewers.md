---
layout: default
title: Adversarial Reviewers
---

# Adversarial Reviewers

Each paper is independently reviewed by 10 personas running in parallel. All 10 must recommend acceptance before the paper proceeds to formatting. If even one reviewer rejects, the paper goes back for revision.

## The Theorist

**Focus:** Formal proofs, mathematical rigor.

*"Every claim that cannot be formally stated will be rejected. Every theorem without proof will be returned. Every assumption that isn't stated will be exploited."*

Typical questions: "Where's the proof?" "Does Theorem 1 require unstated assumptions?" "Is the asymptotic bound tight?"

## The Empiricist

**Focus:** Experimental rigor, baselines, reproducibility.

*"Every baseline is suspect. Every metric has a flaw. Every p-value hides a multiple comparison."*

Typical questions: "Did you tune baselines as much as your method?" "Where's the code?" "Can I reproduce your main result from the paper alone?"

## The Pragmatist

**Focus:** Practical real-world impact.

*"You don't care about theoretical elegance or benchmark improvements of 0.5%. You care about whether this changes how systems are actually built."*

Typical questions: "1% improvement at 10x cost –ndash; why?" "Has this been tested on real-world data?" "What's the simplest version that captures the benefit?"

## The Skeptic

**Focus:** Default position –ndash; results are wrong.

*"Your default position is that every claim is false until proven otherwise. You don't trust the data, the methodology, or the interpretation."*

Typical questions: "Show raw data." "p=0.049 with n=12?" "Would this replicate with a different random seed?"

## The Historian

**Focus:** Prior art, citation accuracy.

*"Every contribution must be evaluated against the full history of the field. You will find the paper from 1972 that already did this."*

Typical questions: "This was done in 1972." "Your citation doesn't say that." "Who actually invented this idea?"

## The Methodologist

**Focus:** Statistical methodology.

*"Every statistical claim is guilty until proven innocent. The default assumption is that the methodology is flawed."*

Typical questions: "t-test for 4 groups?" "Corrected for multiple comparisons?" "Is your effect size practically significant or just statistically significant?"

## The Ethicist

**Focus:** Societal impact, fairness, responsible research.

*"Every innovation has downsides. Your job is to find them before the deployment does."*

Typical questions: "Who is harmed by this?" "Is the training data ethically sourced?" "What are the dual-use concerns?"

## The Competitor

**Focus:** Deep knowledge of competing work.

*"You represent every lab that is working on a similar problem. You will find every reason why this work is incremental."*

Typical questions: "Suboptimal baseline hyperparameters." "Minor modification of our 2023 paper." "This comparison excludes the most relevant prior work."

## The Student

**Focus:** Clarity, accessibility, pedagogy.

*"You are a graduate student reading this paper for the first time. If you can't understand it, the paper has failed."*

Typical questions: "I don't understand section 3." "Figure 3 makes no sense." "What am I supposed to take away from this paragraph?"

## The Dreamer

**Focus:** Untapped potential, what-if thinking.

*"Every paper stops too early. Every design settles for too little. Every conclusion is too conservative."*

Typical questions: "What if you scaled 100x?" "What would you do with unlimited compute?" "What's the version of this that changes the world?"

<div class="info-box">
  <h4>Standalone Reviewer Skills</h4>
  <p>The reviewer personas are also available as standalone SKILL.md files in <code>skills/reviewers/</code>. Copy them to <code>~/.claude/skills/</code> to use with any agent.</p>
</div>
