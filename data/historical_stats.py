import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch
from data.historical_stats import calculate_team_stats


class TestHistoricalStats(unittest.TestCase):

    def setUp(self):
        kickoff = datetime(
            2026,
            9,
            20,
            15,
            0,
            tzinfo=timezone.utc,
        )

        self.matches = [
            HistoricalMatch(
                match_id="1",
                home_team="Arsenal",
                away_team="Chelsea",
                league="Premier League",
                kickoff=kickoff,
                home_goals=2,
                away_goals=1,
                odds={"home_win": 2.0},
            ),
            HistoricalMatch(
                match_id="2",
                home_team="Chelsea",
                away_team="Liverpool",
                league="Premier League",
                kickoff=kickoff,
                home_goals=1,
                away_goals=3,
                odds={"home_win": 2.5},
            ),
            HistoricalMatch(
                match_id="3",
                home_team="Liverpool",
                away_team="Arsenal",
                league="Premier League",
                kickoff=kickoff,
                home_goals=2,
                away_goals=2,
                odds={"home_win": 2.2},
            ),
        ]

    def test_returns_team_stats(self):
        stats = calculate_team_stats(self.matches)

        self.assertIn("Arsenal", stats)
        self.assertIn("Chelsea", stats)
        self.assertIn("Liverpool", stats)

    def test_counts_matches_played(self):
        stats = calculate_team_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["matches"], 2)
        self.assertEqual(stats["Chelsea"]["matches"], 2)
        self.assertEqual(stats["Liverpool"]["matches"], 2)

    def test_counts_goals_for_correctly(self):
        stats = calculate_team_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["goals_for"], 4)
        self.assertEqual(stats["Chelsea"]["goals_for"], 2)
        self.assertEqual(stats["Liverpool"]["goals_for"], 5)

    def test_counts_goals_against_correctly(self):
        stats = calculate_team_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["goals_against"], 3)
        self.assertEqual(stats["Chelsea"]["goals_against"], 5)
        self.assertEqual(stats["Liverpool"]["goals_against"], 3)

    def test_calculates_average_goals_for(self):
        stats = calculate_team_stats(self.matches)

        self.assertAlmostEqual(stats["Arsenal"]["avg_goals_for"], 2.0)
        self.assertAlmostEqual(stats["Chelsea"]["avg_goals_for"], 1.0)
        self.assertAlmostEqual(stats["Liverpool"]["avg_goals_for"], 2.5)

    def test_calculates_average_goals_against(self):
        stats = calculate_team_stats(self.matches)

        self.assertAlmostEqual(stats["Arsenal"]["avg_goals_against"], 1.5)
        self.assertAlmostEqual(stats["Chelsea"]["avg_goals_against"], 2.5)
        self.assertAlmostEqual(stats["Liverpool"]["avg_goals_against"], 1.5)

    def test_empty_match_list_returns_empty_stats(self):
        stats = calculate_team_stats([])

        self.assertEqual(stats, {})

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_team_stats(None)

    def test_invalid_match_item_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_team_stats([self.matches[0], "invalid"])


if __name__ == "__main__":
    unittest.main()
