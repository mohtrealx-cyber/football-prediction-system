import unittest

from prediction.feature_prediction import predict_match_from_features


class TestFeaturePrediction(unittest.TestCase):

    def setUp(self):
        self.features = {
            "home_attack_strength": 1.20,
            "home_defense_strength": 1.00,
            "away_attack_strength": 0.90,
            "away_defense_strength": 1.10,
            "home_recent_points": 7,
            "away_recent_points": 4,
            "home_form_goals_for": 6,
            "away_form_goals_for": 4,
            "home_home_avg_goals": 1.80,
            "away_away_avg_goals": 1.20,
            "league_avg_home_goals": 1.50,
            "league_avg_away_goals": 1.10,
        }

    def test_returns_dictionary(self):
        result = predict_match_from_features(self.features)

        self.assertIsInstance(result, dict)

    def test_expected_goals_are_preserved(self):
        result = predict_match_from_features(self.features)

        self.assertIn("expected_home_goals", result)
        self.assertIn("expected_away_goals", result)

        self.assertGreater(
            result["expected_home_goals"],
            0.0,
        )

        self.assertGreater(
            result["expected_away_goals"],
            0.0,
        )

    def test_all_required_markets_are_present(self):
        result = predict_match_from_features(self.features)

        required_markets = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        self.assertTrue(
            required_markets.issubset(result.keys())
        )

    def test_all_market_probabilities_are_valid(self):
        result = predict_match_from_features(self.features)

        markets = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        for market in markets:
            self.assertIsInstance(
                result[market],
                (int, float),
            )

            self.assertGreaterEqual(
                result[market],
                0.0,
            )

            self.assertLessEqual(
                result[market],
                1.0,
            )

    def test_match_result_probabilities_sum_to_one(self):
        result = predict_match_from_features(self.features)

        total = (
            result["home_win"]
            + result["draw"]
            + result["away_win"]
        )

        self.assertAlmostEqual(
            total,
            1.0,
            places=6,
        )

    def test_over_under_probabilities_sum_to_one(self):
        result = predict_match_from_features(self.features)

        total = (
            result["over_2_5"]
            + result["under_2_5"]
        )

        self.assertAlmostEqual(
            total,
            1.0,
            places=6,
        )

    def test_btts_probabilities_sum_to_one(self):
        result = predict_match_from_features(self.features)

        total = (
            result["btts_yes"]
            + result["btts_no"]
        )

        self.assertAlmostEqual(
            total,
            1.0,
            places=6,
        )

    def test_invalid_features_are_rejected(self):
        with self.assertRaises((TypeError, ValueError, KeyError)):
            predict_match_from_features([])


if __name__ == "__main__":
    unittest.main()
