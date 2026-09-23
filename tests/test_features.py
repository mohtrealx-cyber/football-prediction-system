import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch
from data.models import Match
from data.features import build_match_features


class TestFeatureEngineering(unittest.TestCase):

    def setUp(self):
        self.historical_matches = [
            HistoricalMatch(
                match_id="1",
                home_team="Arsenal",
                away_team="Chelsea",
                league="EPL",
                kickoff=datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc),
                home_goals=2,
                away_goals=1,
                odds={
                    "home_win": 2.0,
                    "draw": 3.5,
                    "away_win": 4.0,
                },
            ),
            HistoricalMatch(
                match_id="2",
                home_team="Liverpool",
                away_team="Arsenal",
                league="EPL",
                kickoff=datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc),
                home_goals=1,
                away_goals=1,
                odds={
                    "home_win": 2.2,
                    "draw": 3.3,
                    "away_win": 3.2,
                },
            ),
            HistoricalMatch(
                match_id="3",
                home_team="Arsenal",
                away_team="Manchester City",
                league="EPL",
                kickoff=datetime(2026, 1, 15, 15, 0, tzinfo=timezone.utc),
                home_goals=0,
                away_goals=3,
                odds={
                    "home_win": 3.0,
                    "draw": 3.5,
                    "away_win": 2.0,
                },
            ),
        ]

        self.target_match = Match(
            match_id="target",
            home_team="Arsenal",
            away_team="Manchester City",
            league="EPL",
            kickoff=datetime(2026, 1, 10, 15, 0, tzinfo=timezone.utc),
            status="scheduled",
            odds={
                "home_win": 2.0,
                "draw": 3.5,
                "away_win": 4.0,
            },
        )

    def test_returns_dictionary(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        self.assertIsInstance(features, dict)

    def test_required_features_are_present(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        required_features = {
            "home_attack_strength",
            "home_defense_strength",
            "away_attack_strength",
            "away_defense_strength",
            "home_recent_points",
            "away_recent_points",
            "home_form_goals_for",
            "away_form_goals_for",
            "home_home_avg_goals",
            "away_away_avg_goals",
            "league_avg_home_goals",
            "league_avg_away_goals",
        }

        self.assertTrue(required_features.issubset(features.keys()))

    def test_future_matches_are_not_used(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        # Match 3 happened after the target kickoff and must not affect
        # any features for the target match.
        self.assertEqual(features["home_recent_points"], 4)

    def test_cutoff_match_is_not_used(self):
        cutoff_match = HistoricalMatch(
            match_id="cutoff",
            home_team="Arsenal",
            away_team="West Ham",
            league="EPL",
            kickoff=datetime(2026, 1, 10, 15, 0, tzinfo=timezone.utc),
            home_goals=5,
            away_goals=0,
            odds={
                "home_win": 1.5,
                "draw": 4.0,
                "away_win": 6.0,
            },
        )

        history = self.historical_matches + [cutoff_match]

        features = build_match_features(
            history,
            self.target_match,
        )

        self.assertEqual(features["home_recent_points"], 4)

    def test_home_features_use_home_matches(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        # Arsenal's only historical home match before the target was:
        # Arsenal 2-1 Chelsea
        self.assertEqual(features["home_home_avg_goals"], 2.0)

    def test_away_features_use_away_matches(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        # Manchester City has no historical away match before the target.
        self.assertEqual(features["away_away_avg_goals"], 0.0)

    def test_league_features_use_only_previous_matches(self):
        features = build_match_features(
            self.historical_matches,
            self.target_match,
        )

        # Only matches 1 and 2 happened before the target.
        self.assertAlmostEqual(
            features["league_avg_home_goals"],
            1.5,
        )

        self.assertAlmostEqual(
            features["league_avg_away_goals"],
            1.0,
        )

    def test_non_list_history_is_rejected(self):
        with self.assertRaises(TypeError):
            build_match_features(
                "invalid",
                self.target_match,
            )

    def test_invalid_target_match_is_rejected(self):
        with self.assertRaises(TypeError):
            build_match_features(
                self.historical_matches,
                "invalid",
            )


if __name__ == "__main__":
    unittest.main()
