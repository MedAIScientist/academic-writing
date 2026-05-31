"""Tests for literature_client.py — local logic only, no network calls."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from literature_client import deduplicate_papers


class TestDeduplicatePapers:
    """deduplicate_papers() — pure local dedup logic."""

    def test_empty_list(self):
        assert deduplicate_papers([]) == []

    def test_single_paper(self):
        papers = [{"title": "Test Paper", "source": "arxiv"}]
        result = deduplicate_papers(papers)
        assert len(result) == 1
        assert result[0]["title"] == "Test Paper"

    def test_identical_titles_deduplicated(self):
        papers = [
            {"title": "Same Title", "source": "arxiv"},
            {"title": "Same Title", "source": "semantic_scholar"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_case_insensitive_dedup(self):
        papers = [
            {"title": "Machine Learning", "source": "arxiv"},
            {"title": "machine learning", "source": "crossref"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_different_titles_preserved(self):
        papers = [
            {"title": "Paper One", "source": "arxiv"},
            {"title": "Paper Two", "source": "arxiv"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 2

    def test_trailing_whitespace_normalized(self):
        papers = [
            {"title": "  Title  ", "source": "arxiv"},
            {"title": "title", "source": "crossref"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_long_titles_truncated_to_80_chars(self):
        long_title = "A" * 100
        slightly_different = "A" * 80 + "B" * 20
        papers = [
            {"title": long_title, "source": "arxiv"},
            {"title": slightly_different, "source": "crossref"},
        ]
        # First 80 chars are identical, so they deduplicate
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_none_or_empty_title_skipped(self):
        papers = [
            {"title": None, "source": "arxiv"},
            {"title": "", "source": "crossref"},
            {"title": "Real Paper", "source": "arxiv"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1
        assert result[0]["title"] == "Real Paper"

    def test_does_not_mutate_input(self):
        papers = [{"title": "Test", "source": "arxiv"}]
        original = papers.copy()
        deduplicate_papers(papers)
        assert papers == original
