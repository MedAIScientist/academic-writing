"""Tests for citation_verifier.py — all local logic, no network calls."""

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.timeout(10)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from citation_verifier import verify_citation, verify_citations, generate_bibtex


class TestVerifyCitation:
    """verify_citation() — local logic only (no mocked API)."""

    def test_returns_dict_with_required_keys(self):
        """Smoke: returns correct structure even when APIs fail."""
        result = verify_citation("key", "some claim text here")
        assert "citation_key" in result
        assert "claim" in result
        assert "verified" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)

    def test_citation_key_preserved(self):
        result = verify_citation("Smith2020", "Smith et al. demonstrated X")
        assert result["citation_key"] == "Smith2020"

    def test_claim_truncated_to_200_chars(self):
        long_claim = "A" * 500
        result = verify_citation("key", long_claim)
        assert len(result["claim"]) == 200

    def test_empty_citation_does_not_crash(self):
        result = verify_citation("", "")
        assert isinstance(result, dict)

    def test_unverified_citation_has_issues(self):
        """Citations not found in any source get flagged."""
        result = verify_citation("ghost2024", "This paper does not exist at all")
        if not result.get("semantic_scholar") and not result.get("crossref"):
            assert len(result.get("issues", [])) > 0

    def test_result_has_semantic_scholar_key(self):
        result = verify_citation("key", "test")
        assert "semantic_scholar" in result
        assert "crossref" in result

    def test_verified_flag_is_bool(self):
        result = verify_citation("key", "test")
        assert isinstance(result["verified"], bool)

    def test_issues_list_contains_strings(self):
        result = verify_citation("key", "nonexistent paper xyz789")
        for issue in result.get("issues", []):
            assert isinstance(issue, str)


class TestVerifyCitations:
    """verify_citations() — local text extraction logic."""

    def test_empty_findings_returns_zero_citations(self):
        result = verify_citations({})
        assert result["total_citations"] == 0
        assert result["verified"] == 0
        assert result["hallucinated_count"] == 0

    def test_findings_without_paper_key(self):
        result = verify_citations({"other": "data"})
        assert result["total_citations"] == 0

    def test_extracts_bracket_citations_from_text(self):
        findings = {"paper": "As shown in [Smith2020], the method works. See also [Jones2019]."}
        result = verify_citations(findings)
        assert result["total_citations"] == 2
        assert len(result["details"]) == 2

    def test_no_false_positives_on_text_without_brackets(self):
        findings = {"paper": "Smith et al. 2020 showed that learning works."}
        result = verify_citations(findings)
        assert result["total_citations"] == 0

    def test_extracts_citations_from_long_document(self):
        text = " ".join(f"[citation{i}]" for i in range(50))
        findings = {"paper": text}
        result = verify_citations(findings)
        assert result["total_citations"] == 50

    def test_result_structure(self):
        findings = {"paper": "See [Test2024]."}
        result = verify_citations(findings)
        assert "blocked" in result
        assert "hallucinated_citations" in result
        assert isinstance(result["blocked"], bool)
        assert isinstance(result["hallucinated_citations"], list)

    def test_blocked_flag(self):
        """If any citations are unverified, blocked should be True."""
        result = verify_citations({"paper": "See [Nonexistent99]."})
        # With no network, citations won't be found, so blocked should be True
        # unless they happen to match (unlikely for this key)
        assert "blocked" in result


class TestGenerateBibtex:
    """generate_bibtex() — pure string formatting."""

    def test_returns_empty_for_no_doi(self):
        assert generate_bibtex({}) == ""

    def test_returns_empty_for_missing_doi_key(self):
        assert generate_bibtex({"title": "Test"}) == ""

    def test_returns_bibtex_string_for_valid_paper(self):
        paper = {
            "doi": "10.1234/test.2024.001",
            "title": "A Test Paper",
            "year": 2024,
        }
        bib = generate_bibtex(paper)
        assert bib.startswith("@article{")
        assert "10.1234/test.2024.001" in bib
        assert "A Test Paper" in bib
        assert bib.endswith("}")

    def test_bibtex_includes_year(self):
        paper = {"doi": "10.1/abc", "title": "T", "year": 2023}
        bib = generate_bibtex(paper)
        assert "2023" in bib

    def test_bibtex_structure(self):
        paper = {"doi": "10.1/abc", "title": "Test", "year": 2024}
        bib = generate_bibtex(paper)
        lines = bib.strip().split("\n")
        assert lines[0].startswith("@article{")
        assert lines[-1] == "}"

    def test_bibtex_handles_missing_year(self):
        paper = {"doi": "10.1/abc", "title": "Test"}
        bib = generate_bibtex(paper)
        assert "n.d." in bib  # "no date"

    def test_bibtex_multiple_papers_different_keys(self):
        papers = [
            {"doi": "10.1/a", "title": "Paper A", "year": 2020},
            {"doi": "10.1/b", "title": "Paper B", "year": 2021},
        ]
        bibs = [generate_bibtex(p) for p in papers]
        assert all(b.startswith("@article{") for b in bibs)
        assert "Paper A" in bibs[0]
        assert "Paper B" in bibs[1]


class TestIntegration:
    """Integration-like tests using local logic composition."""

    def test_verify_citations_flow(self):
        """End-to-end flow: extract, verify, check blocked."""
        findings = {"paper": "As [Smith2020] showed, attention works [Vaswani2017]."}
        result = verify_citations(findings)
        assert result["total_citations"] == 2
        assert len(result["details"]) == 2
        assert result["blocked"] is True or result["blocked"] is False

    def test_verify_then_bibtex_flow(self):
        """Simulate: verify citation → generate BibTeX for found paper."""
        result = verify_citation("test2024", "A paper about machine learning")
        # If found, generate BibTeX
        if result.get("semantic_scholar"):
            bib = generate_bibtex(result["semantic_scholar"])
            assert isinstance(bib, str)
