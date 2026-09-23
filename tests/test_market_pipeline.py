import unittest

from markets.pipeline import run_market_pipeline


class TestMarketPipeline(unittest.TestCase):

    def setUp(self):
        self.predictions = {
            "home_win": 0.50,
            "draw": 0.25,
            "away_win": 0.25,
            "over_2_5": 0.60,
            "under_2_5": 0.40,
            "btts_yes": 0.55,
            "btts_no": 0.45,
        }

        self.odds = {
            "home_win": 2.20,
            "draw": 4.00,
            "away_win": 4.50,
            "over_2_5": 1.80,
            "under_2_5": 2.00,
            "btts_yes": 1.90,
            "btts_no": 2.10,
        }

    def test_pipeline_returns_all_available_markets(self):
        results = run_market_pipeline(
            self.predictions,
            self.odds,
        )

        self.assertEqual(len(results), 7)

    def test_pipeline_passes_minimum_edge(self):
        results = run_market_pipeline(
            self.predictions,
            self.odds,
            minimum_edge=100.0,
        )

        for result in results:
            self.assertFalse(result.qualified)

    def test_pipeline_skips_missing_odds(self):
        odds = self.odds.copy()
        del odds["draw"]

        results = run_market_pipeline(
            self.predictions,
            odds,
        )

        self.assertEqual(len(results), 6)

        markets = [result.market for result in results]
        self.assertNotIn("draw", markets)

    def test_pipeline_returns_market_analysis_objects(self):
        results = run_market_pipeline(
            self.predictions,
            self.odds,
        )

        for result in results:
            self.assertTrue(hasattr(result, "market"))
            self.assertTrue(hasattr(result, "model_probability"))
            self.assertTrue(hasattr(result, "odds"))
            self.assertTrue(hasattr(result, "expected_value"))
            self.assertTrue(hasattr(result, "value_edge"))
            self.assertTrue(hasattr(result, "qualified"))

    def test_predictions_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_market_pipeline(
                [],
                self.odds,
            )

    def test_odds_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_market_pipeline(
                self.predictions,
                [],
            )


if __name__ == "__main__":
    unittest.main()
