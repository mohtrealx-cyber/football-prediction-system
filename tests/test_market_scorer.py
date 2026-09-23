import unittest

from markets.scorer import score_market_analyses
from analysis.engine import SelectionAnalysis


class TestMarketScorer(unittest.TestCase):

    def setUp(self):
        self.analyses = [
            SelectionAnalysis(
                market="home_win",
                model_probability=0.70,
                odds=1.80,
                market_probability=1 / 1.80,
                expected_value=0.26,
                value_edge=14.44,
                qualified=True,
            ),
            SelectionAnalysis(
                market="over_2_5",
                model_probability=0.60,
                odds=1.90,
                market_probability=1 / 1.90,
                expected_value=0.14,
                value_edge=7.37,
                qualified=True,
            ),
            SelectionAnalysis(
                market="btts_yes",
                model_probability=0.55,
                odds=2.00,
                market_probability=0.50,
                expected_value=0.10,
                value_edge=5.00,
                qualified=True,
            ),
        ]

    def test_scores_all_analyses(self):
        results = score_market_analyses(self.analyses)

        self.assertEqual(len(results), 3)

    def test_score_is_added(self):
        results = score_market_analyses(self.analyses)

        for result in results:
            self.assertIn("score", result)

    def test_scores_are_numeric(self):
        results = score_market_analyses(self.analyses)

        for result in results:
            self.assertIsInstance(result["score"], float)

    def test_results_are_sorted_highest_first(self):
        results = score_market_analyses(self.analyses)

        scores = [result["score"] for result in results]

        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_original_analysis_is_not_modified(self):
        original_markets = [analysis.market for analysis in self.analyses]

        score_market_analyses(self.analyses)

        self.assertEqual(
            [analysis.market for analysis in self.analyses],
            original_markets,
        )

    def test_empty_list_is_allowed(self):
        results = score_market_analyses([])

        self.assertEqual(results, [])

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            score_market_analyses({})

    def test_missing_model_probability_is_rejected(self):
        class BadAnalysis:
            value_edge = 5.0

        with self.assertRaises(ValueError):
            score_market_analyses([BadAnalysis()])

    def test_missing_value_edge_is_rejected(self):
        class BadAnalysis:
            model_probability = 0.60

        with self.assertRaises(ValueError):
            score_market_analyses([BadAnalysis()])


if __name__ == "__main__":
    unittest.main()
