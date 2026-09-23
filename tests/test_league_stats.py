import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch
from data.league_stats import calculate_league_stats


class TestLeagueStats(unittest.TestCase):

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
                home_team="Liverpool",
                away_team="Everton",
                league="Premier League",
                kickoff=kickoff,
                home_goals=3,
                away_goals=1,
                odds={"home_win": 1.8},
            ),
        ]

    def test_returns_league_stats(self):
        stats = calculate_league_stats(self.matches)

        self.assertIn("matches", stats)
        self.assertIn("avg_home_goals", stats)
        self.assertIn("avg_away_goals", stats)
        self.assertIn("avg_total_goals", stats)

    def test_counts_matches(self):
        stats = calculate_league_stats(self.matches)

        self.assertEqual(stats["matches"], 2)

    def test_calculates_average_home_goals(self):
        stats = calculate_league_stats(self.matches)

        self.assertAlmostEqual(
            stats["avg_home_goals"],
            2.5,
        )

    def test_calculates_average_away_goals(self):
        stats = calculate_league_stats(self.matches)

        self.assertAlmostEqual(
            stats["avg_away_goals"],
            1.0,
        )

    def test_calculates_average_total_goals(self):
        stats = calculate_league_stats(self.matches)

        self.assertAlmostEqual(
            stats["avg_total_goals"],
            3.5,
        )

    def test_empty_matches_return_zero_stats(self):
        stats = calculate_league_stats([])

        self.assertEqual(stats["matches"], 0)
        self.assertEqual(stats["avg_home_goals"], 0.0)
        self.assertEqual(stats["avg_away_goals"], 0.0)
        self.assertEqual(stats["avg_total_goals"], 0.0)

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_league_stats(None)

    def test_invalid_match_item_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_league_stats(["invalid"])

    def test_invalid_mixed_match_list_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_league_stats([
                self.matches[0],
                "invalid",
            ])


if __name__ == "__main__":
    unittest.main()
