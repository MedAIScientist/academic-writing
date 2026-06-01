#!/usr/bin/env python3
"""Sisyphus Academica — Interactive configuration."""

import shutil
from pathlib import Path


def run_configure():
    """Interactive setup for API keys."""
    repo_dir = Path(__file__).resolve().parent.parent.parent
    env_example = repo_dir / ".env.example"
    env_file = repo_dir / ".env"

    print("Sisyphus Academica — Configuration")
    print()

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  Created .env from .env.example")
    elif env_file.exists():
        print("  .env already exists")

    print()
    print("  Literature API keys (optional, free):")
    print()

    ss_key = input("  Semantic Scholar API key? (free — get at semanticscholar.org) [enter to skip]: ").strip()
    if ss_key:
        _set_env(env_file, "SEMANTIC_SCHOLAR_API_KEY", ss_key)
        print("  ✓ Saved")

    crossref_email = input("  CrossRef email? (for higher rate limits) [enter to skip]: ").strip()
    if crossref_email:
        _set_env(env_file, "CROSSREF_EMAIL", crossref_email)
        print("  ✓ Saved")

    print()
    print("  Done. You can now run:")
    print("    sisyphus demo")

    # Create output dirs
    for d in ["out/papers", "out/figures", "data"]:
        (repo_dir / d).mkdir(parents=True, exist_ok=True)


def _set_env(env_file: Path, key: str, value: str):
    """Set a key=value in .env, preserving existing content."""
    if not env_file.exists():
        env_file.write_text(f"{key}={value}\n")
        return

    lines = env_file.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    env_file.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    run_configure()
