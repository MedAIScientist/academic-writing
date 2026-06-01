# FAQ

## General

**Q: Does this require a specific LLM provider?**
No. Edit `config/agent-config.json` to use any OpenAI-compatible or Anthropic API.

**Q: Do I need OpenCode?**
Yes. The agents are designed for the OpenCode agent platform.

## Pipeline

**Q: How long does a paper take?**
30 minutes to 4 hours depending on LLM speed, literature volume, revision rounds.

**Q: Can I add my own template?**
Yes. See the [Template Guide](https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md#adding-a-venue-template).

## Novelty

**Q: What if no novelty engine produces a useful hypothesis?**
The system reports "no novel angle found" and refuses to write the paper.

## Quality

**Q: How reliable is citation verification?**
Every citation checked against 2+ sources (Semantic Scholar AND CrossRef). If neither source finds it, the paper is **blocked**.

**Q: How strict is AI-pattern detection?**
Very strict. Pattern density < 1 per 2000 words. Zero em dashes allowed. One em dash = automatic failure.

**Q: What does "all 10 reviewers must pass" mean?**
All 10 personas must recommend acceptance. Even one rejection sends the paper back for revision.

## Development

**Q: How do I run tests?**
```bash
python -m pytest tests/ -v
```

**Q: How do I lint?**
```bash
flake8 tools/ --max-line-length=100
```

**Q: How do I contribute?**
See [CONTRIBUTING.md](https://github.com/argahv/sisyphus-academica/blob/main/CONTRIBUTING.md). Look for `good-first-issue` labels.
