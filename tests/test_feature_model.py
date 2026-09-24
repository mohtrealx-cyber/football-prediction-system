import unittest

from prediction.feature_model import predict_from_features


class TestFeatureModel(unittest.TestCase):

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
        result = predict_from_features(self.features)

        self.assertIsInstance(result, dict)

    def test_expected_goals_are_present(self):
        result = predict_from_features(self.features)

        self.assertIn("expected_home_goals", result)
        self.assertIn("expected_away_goals", result)

    def test_expected_goals_are_numeric(self):
        result = predict_from_features(self.features)

        self.assertIsInstance(
            result["expected_home_goals"],
            (int, float),
        )
        self.assertIsInstance(
            result["expected_away_goals"],
            (int, float),
        )

    def test_expected_goals_are_non_negative(self):
        result = predict_from_features(self.features)

        self.assertGreaterEqual(
            result["expected_home_goals"],
            0.0,
        )
        self.assertGreaterEqual(
            result["expected_away_goals"],
            0.0,
        )

    def test_home_strength_affects_home_expected_goals(self):
        normal = predict_from_features(self.features)

        stronger = self.features.copy()
        stronger["home_attack_strength"] = 1.60

        result = predict_from_features(stronger)

        self.assertGreater(
            result["expected_home_goals"],
            normal["expected_home_goals"],
        )

    def test_away_strength_affects_away_expected_goals(self):
        normal = predict_from_features(self.features)

        stronger = self.features.copy()
        stronger["away_attack_strength"] = 1.30

        result = predict_from_features(stronger)

        self.assertGreater(
            result["expected_away_goals"],
            normal["expected_away_goals"],
        )

    def test_league_baseline_affects_expected_goals(self):
        normal = predict_from_features(self.features)

        higher_scoring_league = self.features.copy()
        higher_scoring_league["league_avg_home_goals"] = 2.00
        higher_scoring_league["league_avg_away_goals"] = 1.50

        result = predict_from_features(higher_scoring_league)

        self.assertGreater(
            result["expected_home_goals"],
            normal["expected_home_goals"],
        )
        self.assertGreater(
            result["expected_away_goals"],
            normal["expected_away_goals"],
        )

    def test_missing_feature_is_rejected(self):
        incomplete = self.features.copy()
        del incomplete["home_attack_strength"]

        with self.assertRaises((KeyError, ValueError, TypeError)):
            predict_from_features(incomplete)

    def test_features_must_be_dictionary(self):
        with self.assertRaises(TypeError):
            predict_from_features([])


if __name__ == "__main__":
    unittest.main()
