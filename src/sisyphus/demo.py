#!/usr/bin/env python3
"""Sisyphus Academica — Demo Mode. No API keys required."""

import textwrap


def run_demo():
    """Print a demo of the Sisyphus pipeline using example data."""
    print("╔═══════════════════════════════════════════════╗")
    print("║     Sisyphus Academica — Demo Mode            ║")
    print("╚═══════════════════════════════════════════════╝")
    print()
    print("Running pipeline on example topic: 'Transformer Efficiency'")
    print()

    # Phase 1: Literature Review
    print("[1/6] Literature Review (simulated)")
    print("  → 5 parallel scouts searching 4 sources...")
    print("  → arXiv: 187 papers")
    print("  → Semantic Scholar: 234 papers")
    print("  → CrossRef: 98 papers")
    print("  → OpenAlex: 156 papers")
    print("  → Total unique: 412 papers after dedup")
    print()

    # Phase 1.5: Novelty Engines
    print("[2/6] Novelty Generation")
    print("  → Contrarian: 10 counter-hypotheses")
    print("  → Cross-Pollinator: 15 field imports")
    print("  → Assumption Excavator: 24 assumptions found")
    print("  → Counterfactual Generator: rewriting field history...")
    print("  → Paradox Sifter: 3 contradictions found")
    print("  → Heretic: 50 hypotheses generated, haunting idea identified")
    print()

    # Show example output from the Heretic
    print("  Example — Heretic Engine output:")
    print()
    print(textwrap.dedent("""\
      Haunting idea: What if the attention mechanism's success is not due to
      attention at all, but due to residual connections enabling deeper
      training? Any architecture with similar skip connections might perform
      equivalently.

      Score: Novelty Gap 9/10, Surprise 9/10, Tractability 7/10, Impact 8/10
      Overall: 92.6
    """))
    print()

    # Phase 2-4
    print("[3/6] Methodology Design & Data Engineering")
    print("  → Selected hypothesis: Residual depth > attention mechanism")
    print("  → Power analysis: n=1000 required for 0.8 power")
    print("  → Experimental protocol: controlled comparison")
    print("  → Analysis code generated")
    print()

    # Phase 5: Writing
    print("[4/6] Parallel Writing (5 agents)")
    print("  → Abstract: 247 words, 0 AI-pattern violations")
    print("  → Introduction: 892 words, 0 violations")
    print("  → Methods: 1,204 words, 0 violations")
    print("  → Results: 1,567 words, 0 violations")
    print("  → Discussion: 1,103 words, 0 violations")
    print("  → All 41 Humanizer patterns enforced during generation")
    print()

    # Phase 6: Verification
    print("[5/6] Verification")
    print("  → Citations: 32 verified across 2+ sources, 0 hallucinated")
    print("  → Statistics: All tests validated, no p-hacking detected")
    print("  → AI-patterns: 417/417 sentences passed, 0 violations")
    print("  → Style: 0 em dashes, voice consistent with profile")
    print()

    # Phase 7: Adversarial Review
    print("[6/6] Adversarial Review (10 personas)")
    reviews = [
        ("Theorist", "8/10", "Formal proof needs work, but novel claim"),
        ("Empiricist", "7/10", "Baseline selection could be stronger"),
        ("Pragmatist", "9/10", "Directly applicable to production systems"),
        ("Skeptic", "7/10", "Results plausible but need replication"),
        ("Historian", "8/10", "Good prior art coverage, missed 2 papers"),
        ("Methodologist", "8/10", "Statistical approach is sound"),
        ("Ethicist", "9/10", "No concerns — standard research"),
        ("Competitor", "7/10", "Sufficiently different from existing work"),
        ("Student", "9/10", "Very clear writing, easy to follow"),
        ("Dreamer", "8/10", "Interesting but could push further"),
    ]
    for persona, score, comment in reviews:
        print(f"  → {persona}: {score} — {comment}")
    print()
    print("  → Average score: 8.0/10 — All 10 recommend acceptance ✓")
    print()

    print("════════════════════════════════════════════════")
    print("  Demo complete.")
    print()
    print("  To run the real pipeline:")
    print("    sisyphus write \"your topic\"")
    print()
    print("  Configure API keys:")
    print("    sisyphus configure")
    print()
    print("  ⭐ Star the repo: https://github.com/argahv/sisyphus-academica")
    print()
    print("  Novelty skills (portable, no install needed):")
    print("    https://github.com/argahv/novelty-skills")


if __name__ == "__main__":
    run_demo()
