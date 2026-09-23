import unittest

from markets.generator import generate_market_analyses


class TestMarketGenerator(unittest.TestCase):

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

    def test_generates_all_available_markets(self):
        results = generate_market_analyses(
            self.predictions,
            self.odds,
        )

        self.assertEqual(len(results), 7)

    def test_missing_odds_are_skipped(self):
        odds = self.odds.copy()
        del odds["draw"]
        del odds["btts_no"]

        results = generate_market_analyses(
            self.predictions,
            odds,
        )

        self.assertEqual(len(results), 5)

        markets = [result.market for result in results]

        self.assertNotIn("draw", markets)
        self.assertNotIn("btts_no", markets)

    def test_results_contain_market_names(self):
        results = generate_market_analyses(
            self.predictions,
            self.odds,
        )

        markets = [result.market for result in results]

        self.assertIn("home_win", markets)
        self.assertIn("draw", markets)
        self.assertIn("over_2_5", markets)
        self.assertIn("btts_yes", markets)

    def test_results_contain_model_probabilities(self):
        results = generate_market_analyses(
            self.predictions,
            self.odds,
        )

        for result in results:
            self.assertGreaterEqual(result.model_probability, 0.0)
            self.assertLessEqual(result.model_probability, 1.0)

    def test_results_contain_odds(self):
        results = generate_market_analyses(
            self.predictions,
            self.odds,
        )

        for result in results:
            self.assertGreater(result.odds, 1.0)

    def test_custom_minimum_edge_is_used(self):
        results = generate_market_analyses(
            self.predictions,
            self.odds,
            minimum_edge=100.0,
        )

        for result in results:
            self.assertFalse(result.qualified)

    def test_predictions_must_be_dict(self):
        with self.assertRaises(TypeError):
            generate_market_analyses(
                [],
                self.odds,
            )

    def test_odds_must_be_dict(self):
        with self.assertRaises(TypeError):
            generate_market_analyses(
                self.predictions,
                [],
            )


if __name__ == "__main__":
    unittest.main()
