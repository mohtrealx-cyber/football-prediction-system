import unittest
from datetime import datetime

from pipeline.engine import run_match_pipeline


class PipelineEngineTests(unittest.TestCase):

    def setUp(self):
        self.match = {
            "match_id": "M001",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league": "Premier League",
            "kickoff": datetime(2026, 9, 24, 20, 0),
            "status": "scheduled",
            "odds": {
                "over_2_5": 2.00,
            },
        }

    def _make_match(self):
        from data.models import Match

        return Match(
            match_id=self.match["match_id"],
            home_team=self.match["home_team"],
            away_team=self.match["away_team"],
            league=self.match["league"],
            kickoff=self.match["kickoff"],
            status=self.match["status"],
            odds=self.match["odds"],
        )

    def test_pipeline_returns_all_main_fields(self):
        result = run_match_pipeline(
            match=self._make_match(),
            market="over_2_5",
            home_expected_goals=1.8,
            away_expected_goals=1.2,
            odds=2.00,
        )

        expected_keys = {
            "match_id",
            "home_team",
            "away_team",
            "league",
            "kickoff",
            "market",
            "model_probability",
            "odds",
            "market_probability",
            "expected_value",
            "value_edge",
            "qualified",
            "score",
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_pipeline_connects_prediction_and_odds(self):
        result = run_match_pipeline(
            match=self._make_match(),
            market="over_2_5",
            home_expected_goals=1.8,
            away_expected_goals=1.2,
            odds=2.00,
        )

        self.assertEqual(result["market"], "over_2_5")
        self.assertAlmostEqual(result["odds"], 2.00)
        self.assertGreater(result["model_probability"], 0.0)
        self.assertLess(result["model_probability"], 1.0)

    def test_good_value_can_qualify(self):
        result = run_match_pipeline(
            match=self._make_match(),
            market="over_2_5",
            home_expected_goals=1.8,
            away_expected_goals=1.2,
            odds=2.00,
            minimum_edge=5.0,
        )

        self.assertTrue(result["qualified"])
        self.assertGreater(result["value_edge"], 5.0)

    def test_high_minimum_edge_can_reject_selection(self):
        result = run_match_pipeline(
            match=self._make_match(),
            market="over_2_5",
            home_expected_goals=1.8,
            away_expected_goals=1.2,
            odds=2.00,
            minimum_edge=20.0,
        )

        self.assertFalse(result["qualified"])

    def test_score_is_created(self):
        result = run_match_pipeline(
            match=self._make_match(),
            market="over_2_5",
            home_expected_goals=1.8,
            away_expected_goals=1.2,
            odds=2.00,
        )

        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 100.0)

    def test_unsupported_market_is_rejected(self):
        with self.assertRaises(ValueError):
            run_match_pipeline(
                match=self._make_match(),
                market="first_goal_scorer",
                home_expected_goals=1.8,
                away_expected_goals=1.2,
                odds=2.00,
            )

    def test_invalid_odds_are_rejected(self):
        with self.assertRaises(ValueError):
            run_match_pipeline(
                match=self._make_match(),
                market="over_2_5",
                home_expected_goals=1.8,
                away_expected_goals=1.2,
                odds=1.00,
            )

    def test_invalid_expected_goals_are_rejected(self):
        with self.assertRaises(ValueError):
            run_match_pipeline(
                match=self._make_match(),
                market="over_2_5",
                home_expected_goals=0.0,
                away_expected_goals=1.2,
                odds=2.00,
            )


if __name__ == "__main__":
    unittest.main()
