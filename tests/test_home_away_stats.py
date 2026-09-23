import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch
from data.home_away_stats import calculate_home_away_stats


class TestHomeAwayStats(unittest.TestCase):

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

    def test_returns_all_teams(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertIn("Arsenal", stats)
        self.assertIn("Chelsea", stats)
        self.assertIn("Liverpool", stats)

    def test_home_match_count_is_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["home_matches"], 1)
        self.assertEqual(stats["Chelsea"]["home_matches"], 1)
        self.assertEqual(stats["Liverpool"]["home_matches"], 1)

    def test_away_match_count_is_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["away_matches"], 1)
        self.assertEqual(stats["Chelsea"]["away_matches"], 1)
        self.assertEqual(stats["Liverpool"]["away_matches"], 1)

    def test_home_goals_for_are_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["home_goals_for"], 2)
        self.assertEqual(stats["Chelsea"]["home_goals_for"], 1)
        self.assertEqual(stats["Liverpool"]["home_goals_for"], 2)

    def test_away_goals_for_are_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertEqual(stats["Arsenal"]["away_goals_for"], 2)
        self.assertEqual(stats["Chelsea"]["away_goals_for"], 1)
        self.assertEqual(stats["Liverpool"]["away_goals_for"], 3)

    def test_home_average_goals_for_is_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertAlmostEqual(
            stats["Arsenal"]["home_avg_goals_for"],
            2.0,
        )

    def test_away_average_goals_for_is_correct(self):
        stats = calculate_home_away_stats(self.matches)

        self.assertAlmostEqual(
            stats["Arsenal"]["away_avg_goals_for"],
            2.0,
        )

    def test_empty_match_list_returns_empty_stats(self):
        stats = calculate_home_away_stats([])

        self.assertEqual(stats, {})

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_home_away_stats(None)


if __name__ == "__main__":
    unittest.main()
