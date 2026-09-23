import unittest

from prediction.engine import predict_match


class PredictionEngineTests(unittest.TestCase):

    def test_prediction_returns_all_required_markets(self):
        result = predict_match(1.8, 1.2)

        expected_keys = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_result_probabilities_are_between_zero_and_one(self):
        result = predict_match(1.8, 1.2)

        for probability in result.values():
            self.assertGreaterEqual(probability, 0.0)
            self.assertLessEqual(probability, 1.0)

    def test_match_result_probabilities_are_close_to_one(self):
        result = predict_match(1.8, 1.2)

        total = (
            result["home_win"]
            + result["draw"]
            + result["away_win"]
        )

        self.assertAlmostEqual(total, 1.0, places=3)

    def test_over_and_under_add_to_one(self):
        result = predict_match(1.8, 1.2)

        total = (
            result["over_2_5"]
            + result["under_2_5"]
        )

        self.assertAlmostEqual(total, 1.0, places=6)

    def test_btts_yes_and_no_add_to_one(self):
        result = predict_match(1.8, 1.2)

        total = (
            result["btts_yes"]
            + result["btts_no"]
        )

        self.assertAlmostEqual(total, 1.0, places=6)

    def test_higher_home_goals_should_increase_home_win_probability(self):
        normal = predict_match(1.5, 1.2)
        stronger_home = predict_match(2.0, 1.2)

        self.assertGreater(
            stronger_home["home_win"],
            normal["home_win"],
        )

    def test_invalid_home_expected_goals_are_rejected(self):
        with self.assertRaises(ValueError):
            predict_match(0, 1.2)

    def test_invalid_away_expected_goals_are_rejected(self):
        with self.assertRaises(ValueError):
            predict_match(1.8, 0)

    def test_invalid_max_goals_is_rejected(self):
        with self.assertRaises(ValueError):
            predict_match(1.8, 1.2, max_goals=0)


if __name__ == "__main__":
    unittest.main()
