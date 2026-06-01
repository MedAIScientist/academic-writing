"""Shared test fixtures for Sisyphus Academica tests."""

import sys
from pathlib import Path

# Ensure tools directory is importable in all tests
TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
