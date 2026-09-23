import unittest

from markets.engine import (
    SUPPORTED_MARKETS,
    get_market_probability,
    get_supported_markets,
)


class TestMarketEngine(unittest.TestCase):

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

    def test_supported_markets_count(self):
        self.assertEqual(len(SUPPORTED_MARKETS), 7)

    def test_get_supported_markets(self):
        markets = get_supported_markets()

        self.assertEqual(len(markets), 7)
        self.assertIn("home_win", markets)
        self.assertIn("over_2_5", markets)
        self.assertIn("btts_yes", markets)

    def test_get_market_probability(self):
        probability = get_market_probability(
            self.predictions,
            "home_win",
        )

        self.assertEqual(probability, 0.50)

    def test_get_each_market_probability(self):
        for market in SUPPORTED_MARKETS:
            probability = get_market_probability(
                self.predictions,
                market,
            )

            self.assertGreaterEqual(probability, 0.0)
            self.assertLessEqual(probability, 1.0)

    def test_invalid_market(self):
        with self.assertRaises(ValueError):
            get_market_probability(
                self.predictions,
                "invalid_market",
            )

    def test_predictions_must_be_dict(self):
        with self.assertRaises(TypeError):
            get_market_probability(
                [],
                "home_win",
            )

    def test_missing_prediction(self):
        predictions = self.predictions.copy()
        del predictions["home_win"]

        with self.assertRaises(ValueError):
            get_market_probability(
                predictions,
                "home_win",
            )

    def test_probability_must_be_numeric(self):
        predictions = self.predictions.copy()
        predictions["home_win"] = "0.50"

        with self.assertRaises(TypeError):
            get_market_probability(
                predictions,
                "home_win",
            )

    def test_probability_range(self):
        predictions = self.predictions.copy()
        predictions["home_win"] = 1.5

        with self.assertRaises(ValueError):
            get_market_probability(
                predictions,
                "home_win",
            )


if __name__ == "__main__":
    unittest.main()
