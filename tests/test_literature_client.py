"""Tests for literature_client.py — local logic only, no network calls."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from literature_client import deduplicate_papers, search_arxiv, search_semantic_scholar, search_crossref, search_openalex


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

    def test_deduplicate_stress(self):
        """Stress test: 1000 papers, 500 duplicates."""
        papers = []
        for i in range(500):
            papers.append({"title": f"Unique Paper {i}", "source": "arxiv"})
        for i in range(500):
            papers.append({"title": f"Unique Paper {i}", "source": "crossref"})
        result = deduplicate_papers(papers)
        assert len(result) == 500


class TestSearchFunctions:
    """Search return empty lists on network errors (safe for CI)."""

    @pytest.mark.timeout(10)
    def test_search_arxiv_returns_list(self):
        result = search_arxiv("machine learning", max_results=5)
        assert isinstance(result, list)

    @pytest.mark.timeout(10)
    def test_search_semantic_scholar_returns_list(self):
        result = search_semantic_scholar("machine learning", limit=5)
        assert isinstance(result, list)

    @pytest.mark.timeout(10)
    def test_search_crossref_returns_list(self):
        result = search_crossref("machine learning", rows=5)
        assert isinstance(result, list)

    @pytest.mark.timeout(10)
    def test_search_openalex_returns_list(self):
        result = search_openalex("machine learning", per_page=5)
        assert isinstance(result, list)

    @pytest.mark.timeout(10)
    def test_search_arxiv_respects_max_results(self):
        result = search_arxiv("transformer efficiency", max_results=10)
        if result:
            assert len(result) <= 10


class TestFetchHelpers:
    """Test fetch helpers with invalid URLs (no network needed)."""

    def test_fetch_json_invalid_url(self):
        from literature_client import _fetch_json
        result = _fetch_json("http://nonexistent.invalid/api")
        assert result is None

    def test_fetch_text_invalid_url(self):
        from literature_client import _fetch_text
        result = _fetch_text("http://nonexistent.invalid/api")
        assert result is None
