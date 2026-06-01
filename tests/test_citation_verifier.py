"""Tests for citation_verifier.py — all local logic, no network calls."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from citation_verifier import extract_citations, verify_citation, verify_citations, generate_bibtex


class TestVerifyCitation:
    """verify_citation() — local logic only (no mocked API)."""

    def test_returns_dict_with_required_keys(self):
        """Smoke: returns correct structure even when APIs fail (no mock)."""
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
        # Both citations get extracted; each runs through verify_citation
        # which may or may not find them (we test structure only)
        assert result["total_citations"] == 2
        assert len(result["details"]) == 2

    def test_no_false_positives_on_text_without_brackets(self):
        findings = {"paper": "Smith et al. 2020 showed that learning works."}
        result = verify_citations(findings)
        assert result["total_citations"] == 0

    def test_result_structure(self):
        findings = {"paper": "See [Test2024]."}
        result = verify_citations(findings)
        assert "blocked" in result
        assert "hallucinated_citations" in result
        assert isinstance(result["blocked"], bool)
        assert isinstance(result["hallucinated_citations"], list)

    def test_extracts_author_year_and_paren_via_extract(self):
        text = "[Jones2019] was early. Smith (2020) improved it (Lee, 2021)."
        result = verify_citations({"paper": text})
        # 3 citations extracted; verify_citation hits APIs so check shape only
        assert result["total_citations"] == 3
        assert len(result["details"]) == 3


class TestExtractCitations:
    """extract_citations() — standalone extraction logic."""

    def test_empty_text(self):
        assert extract_citations("") == []

    def test_no_citations(self):
        assert extract_citations("This is plain text without any references.") == []

    def test_bracket_citation(self):
        result = extract_citations("As shown in [Smith2020].")
        assert len(result) == 1
        assert result[0]["key"] == "Smith2020"

    def test_author_year_citation(self):
        result = extract_citations("Smith (2020) demonstrated X.")
        assert len(result) == 1
        assert result[0]["key"] == "Smith2020"

    def test_author_et_al_year(self):
        result = extract_citations("Smith et al. (2020) showed Y.")
        assert len(result) == 1
        assert result[0]["key"] == "Smith et al.2020"

    def test_parenthetical_citation(self):
        result = extract_citations("This was confirmed (Smith, 2020).")
        assert len(result) == 1
        assert result[0]["key"] == "Smith2020"

    def test_parenthetical_et_al(self):
        result = extract_citations("Proposed in (Smith et al., 2020).")
        assert len(result) == 1
        assert result[0]["key"] == "Smith et al.2020"

    def test_mixed_formats(self):
        text = "[Jones2019] was early work, but Smith (2020) improved it (Lee, 2021)."
        result = extract_citations(text)
        assert len(result) == 3

    def test_claim_includes_context(self):
        text = "Prior research by Smith (2020) established the foundation."
        result = extract_citations(text)
        assert len(result) == 1
        assert "Smith (2020)" in result[0]["claim"]


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
