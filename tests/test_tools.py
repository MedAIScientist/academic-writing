import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import citation_verifier  # noqa: E402
import literature_client  # noqa: E402
import paper_pipeline  # noqa: E402


class CitationVerifierTests(unittest.TestCase):
    def test_extract_citations_bracket_and_parenthetical(self):
        text = (
            'Prior studies show this effect [Smith2020]. '
            'A replication exists (Doe et al., 2021).'
        )
        citations = citation_verifier.extract_citations(text)
        keys = {item['key'] for item in citations}
        self.assertIn('Smith2020', keys)
        self.assertIn('Doe et al., 2021', keys)

    def test_findings_to_text_sections_fallback(self):
        payload = {
            'sections': [
                {'title': 'Intro', 'text': 'Alpha'},
                {'title': 'Methods', 'content': 'Beta'},
            ]
        }
        text = citation_verifier.findings_to_text(payload)
        self.assertIn('Alpha', text)
        self.assertIn('Beta', text)

    def test_title_similarity_identical_titles(self):
        score = citation_verifier._title_similarity(
            'A Unified Framework for Retrieval',
            'A Unified Framework for Retrieval',
        )
        self.assertGreaterEqual(score, 0.99)

    def test_markdown_links_are_not_citations(self):
        text = 'See [Project Site](https://example.com) and citation [Smith2024].'
        citations = citation_verifier.extract_citations(text)
        keys = {item['key'] for item in citations}
        self.assertIn('Smith2024', keys)
        self.assertNotIn('Project Site', keys)

    def test_markdown_links_with_space_or_newline_are_not_citations(self):
        text = (
            'Link one [Project Site] (https://example.com).\n'
            'Link two [Tool Page]\n(https://example.org).\n'
            'Citation [Lee2023] remains.'
        )
        citations = citation_verifier.extract_citations(text)
        keys = {item['key'] for item in citations}
        self.assertEqual(keys, {'Lee2023'})

    def test_parenthetical_note_after_citation_still_counts(self):
        text = 'This was shown before [Smith2024] (see Appendix A).'
        citations = citation_verifier.extract_citations(text)
        keys = {item['key'] for item in citations}
        self.assertIn('Smith2024', keys)


class LiteratureRankingTests(unittest.TestCase):
    def test_infer_domain_from_query(self):
        self.assertEqual(
            literature_client.infer_domain_from_query('LLM transformer benchmark'),
            'fast-moving-ml',
        )
        self.assertEqual(
            literature_client.infer_domain_from_query('proof complexity bounds'),
            'theory',
        )

    def test_infer_domain_avoids_substring_false_positive(self):
        self.assertEqual(
            literature_client.infer_domain_from_query('agent management principles'),
            'general',
        )

    def test_domain_ranking_changes_priority(self):
        papers = [
            {'title': 'Old but famous', 'year': 2015, 'citation_count': 225, 'source': 'semantic_scholar'},
            {'title': 'New and promising', 'year': 2025, 'citation_count': 25, 'source': 'semantic_scholar'},
        ]

        theory_ranked = literature_client.rank_papers(
            papers,
            query='proof complexity',
            domain='theory',
            top_n=2,
        )
        fast_ranked = literature_client.rank_papers(
            papers,
            query='transformer agent benchmark',
            domain='fast-moving-ml',
            top_n=2,
        )

        self.assertEqual(theory_ranked[0]['title'], 'Old but famous')
        self.assertEqual(fast_ranked[0]['title'], 'New and promising')

    def test_crossref_year_fallback(self):
        item = {
            'published-online': {'date-parts': [[2022, 8, 1]]},
            'issued': {'date-parts': [[2021, 1, 1]]},
        }
        self.assertEqual(literature_client._crossref_year(item), 2022)


class PipelineTests(unittest.TestCase):
    @patch('paper_pipeline.verify_citations')
    @patch('paper_pipeline.load_api_config')
    @patch('paper_pipeline.search_all')
    def test_pipeline_writes_artifacts(self, mock_search_all, mock_load_api_config, mock_verify_citations):
        mock_search_all.return_value = {
            'query': 'test query',
            'total_raw': 10,
            'total_unique': 8,
            'total_final': 5,
            'by_source': {'arxiv': 3, 'semantic_scholar': 2},
            'filters': {'effective_domain': 'general'},
            'papers': [{'title': 'A', 'sources': ['arxiv']}],
        }
        mock_load_api_config.return_value = citation_verifier.APIConfig('', '')
        mock_verify_citations.return_value = {'blocked': False, 'total_citations': 0, 'verified': 0}

        with tempfile.TemporaryDirectory() as tmp_dir:
            manuscript_path = Path(tmp_dir) / 'draft.md'
            manuscript_path.write_text('Text with [Ref2024].', encoding='utf-8')

            args = type('Args', (), {
                'query': 'test query',
                'manuscript': str(manuscript_path),
                'out_dir': tmp_dir,
                'max_per_source': 50,
                'since_year': None,
                'open_access_only': False,
                'domain': 'general',
                'top': 5,
                'strict_two_source': False,
                'min_match_score': 0.45,
            })

            result = paper_pipeline.run_pipeline(args)
            self.assertFalse(result['blocked'])

            for key in ('literature_json', 'literature_report', 'citation_audit', 'summary'):
                path = Path(result[key])
                self.assertTrue(path.exists(), f'Missing artifact: {key}')

            summary = Path(result['summary']).read_text(encoding='utf-8')
            self.assertIn('Ranking domain: general', summary)

            literature_json = json.loads(Path(result['literature_json']).read_text(encoding='utf-8'))
            self.assertEqual(literature_json['query'], 'test query')

    @patch('paper_pipeline.search_all')
    def test_pipeline_without_manuscript_skips_citation(self, mock_search_all):
        mock_search_all.return_value = {
            'query': 'test query',
            'total_raw': 5,
            'total_unique': 4,
            'total_final': 2,
            'by_source': {'arxiv': 2},
            'filters': {'effective_domain': 'general'},
            'papers': [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            args = type('Args', (), {
                'query': 'test query',
                'manuscript': None,
                'out_dir': tmp_dir,
                'max_per_source': 10,
                'since_year': None,
                'open_access_only': False,
                'domain': 'general',
                'top': 5,
                'strict_two_source': False,
                'min_match_score': 0.45,
            })
            result = paper_pipeline.run_pipeline(args)
            audit = json.loads(Path(result['citation_audit']).read_text(encoding='utf-8'))
            self.assertTrue(audit.get('skipped'))
            self.assertFalse(result['blocked'])

    @patch('paper_pipeline.search_all')
    def test_pipeline_missing_manuscript_blocks(self, mock_search_all):
        mock_search_all.return_value = {
            'query': 'test query',
            'total_raw': 5,
            'total_unique': 4,
            'total_final': 2,
            'by_source': {'arxiv': 2},
            'filters': {'effective_domain': 'general'},
            'papers': [],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            args = type('Args', (), {
                'query': 'test query',
                'manuscript': str(Path(tmp_dir) / 'missing.md'),
                'out_dir': tmp_dir,
                'max_per_source': 10,
                'since_year': None,
                'open_access_only': False,
                'domain': 'general',
                'top': 5,
                'strict_two_source': False,
                'min_match_score': 0.45,
            })
            result = paper_pipeline.run_pipeline(args)
            audit = json.loads(Path(result['citation_audit']).read_text(encoding='utf-8'))
            self.assertTrue(result['blocked'])
            self.assertIn('Cannot read manuscript file', audit.get('error', ''))


if __name__ == '__main__':
    unittest.main()
