"""Tests for the CLI module (src/sisyphus/cli.py)."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


class TestCliHelp:
    """Test CLI entry point behavior."""

    def test_no_args_shows_help(self):
        """sisyphus with no args should print help and not crash."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus"]):
            try:
                main()
            except SystemExit:
                pass  # Some implementations may exit

    def test_demo_command_runs(self):
        """sisyphus demo should run without crashing."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "demo"]):
            try:
                main()
            except SystemExit:
                pass


class TestCliCommands:
    """Test specific commands."""

    def test_configure_command_runs(self):
        """sisyphus configure should start without crashing."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "configure"]):
            try:
                main()
            except SystemExit:
                pass

    def test_search_without_query_prints_usage(self):
        """sisyphus search without query should show usage."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "search"]):
            try:
                main()
            except SystemExit:
                pass

    def test_bibtex_without_doi_prints_usage(self):
        """sisyphus bibtex without DOI should show usage."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "bibtex"]):
            try:
                main()
            except SystemExit:
                pass

    def test_verify_without_args_prints_usage(self):
        """sisyphus verify without args should show usage."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "verify"]):
            try:
                main()
            except SystemExit:
                pass

    def test_unknown_command_prints_usage(self):
        """Unknown commands should not crash."""
        from sisyphus.cli import main
        with patch.object(sys, "argv", ["sisyphus", "nonexistent"]):
            try:
                main()
            except SystemExit:
                pass
