import unittest

from markets.full_pipeline import run_full_market_pipeline


class TestFullMarketPipeline(unittest.TestCase):

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

    def test_full_pipeline_returns_all_markets(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        self.assertEqual(len(results), 7)

    def test_every_result_has_score(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        for result in results:
            self.assertIn("score", result)

    def test_results_are_sorted_by_score(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        scores = [result["score"] for result in results]

        self.assertEqual(
            scores,
            sorted(scores, reverse=True),
        )

    def test_market_information_is_preserved(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        markets = [result["market"] for result in results]

        self.assertIn("home_win", markets)
        self.assertIn("over_2_5", markets)
        self.assertIn("btts_yes", markets)

    def test_missing_odds_are_skipped(self):
        odds = self.odds.copy()
        del odds["draw"]

        results = run_full_market_pipeline(
            self.predictions,
            odds,
        )

        self.assertEqual(len(results), 6)

    def test_custom_minimum_edge_is_passed_through(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
            minimum_edge=100.0,
        )

        for result in results:
            self.assertFalse(result["qualified"])

    def test_predictions_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_full_market_pipeline(
                [],
                self.odds,
            )

    def test_odds_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_full_market_pipeline(
                self.predictions,
                [],
            )


if __name__ == "__main__":
    unittest.main()import unittest

from markets.full_pipeline import run_full_market_pipeline


class TestFullMarketPipeline(unittest.TestCase):

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

    def test_full_pipeline_returns_all_markets(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        self.assertEqual(len(results), 7)

    def test_every_result_has_score(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        for result in results:
            self.assertIn("score", result)

    def test_results_are_sorted_by_score(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        scores = [result["score"] for result in results]

        self.assertEqual(
            scores,
            sorted(scores, reverse=True),
        )

    def test_market_information_is_preserved(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
        )

        markets = [result["market"] for result in results]

        self.assertIn("home_win", markets)
        self.assertIn("over_2_5", markets)
        self.assertIn("btts_yes", markets)

    def test_missing_odds_are_skipped(self):
        odds = self.odds.copy()
        del odds["draw"]

        results = run_full_market_pipeline(
            self.predictions,
            odds,
        )

        self.assertEqual(len(results), 6)

    def test_custom_minimum_edge_is_passed_through(self):
        results = run_full_market_pipeline(
            self.predictions,
            self.odds,
            minimum_edge=100.0,
        )

        for result in results:
            self.assertFalse(result["qualified"])

    def test_predictions_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_full_market_pipeline(
                [],
                self.odds,
            )

    def test_odds_must_be_dict(self):
        with self.assertRaises(TypeError):
            run_full_market_pipeline(
                self.predictions,
                [],
            )


if __name__ == "__main__":
    unittest.main()
