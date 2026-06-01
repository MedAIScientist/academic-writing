# Security Policy

## Reporting a Vulnerability

Sisyphus Academica processes API keys (Semantic Scholar, CrossRef) and runs LLM agents that can execute code. If you discover a security vulnerability:

1. **Do not open a public issue.**
2. Email the maintainer directly at the address listed in the [GitHub profile](https://github.com/argahv).
3. Include a description of the vulnerability, steps to reproduce, and any potential impact.

You should receive a response within 48 hours. If you don't, follow up.

## What to Report

- Exposure of API keys or credentials
- Code execution vulnerabilities in agent prompts or tools
- Data leakage between paper projects
- Insecure defaults in configuration files

## Scope

- `tools/*.py` — Python CLI tools
- `orchestrator/`, `subagents/`, `novelty-engines/`, `reviewers/` — agent prompt files
- `install.sh` — installation script
- `docker-compose.yml`, `Dockerfile` — container configuration

## Out of Scope

- LLM prompt injection in user-supplied paper content (this is expected behavior)
- Hallucinated citations (handled by the verification pipeline, not a security issue)
- AI-written text patterns (handled by the style auditor, not a security issue)
