import unittest
from datetime import datetime, timezone, timedelta

from data.historical_models import HistoricalMatch
from data.form_stats import calculate_recent_form


class TestRecentForm(unittest.TestCase):

    def setUp(self):
        base = datetime(
            2026,
            9,
            1,
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
                kickoff=base,
                home_goals=2,
                away_goals=0,
                odds={"home_win": 2.0},
            ),
            HistoricalMatch(
                match_id="2",
                home_team="Liverpool",
                away_team="Arsenal",
                league="Premier League",
                kickoff=base + timedelta(days=2),
                home_goals=1,
                away_goals=1,
                odds={"home_win": 2.1},
            ),
            HistoricalMatch(
                match_id="3",
                home_team="Arsenal",
                away_team="Manchester City",
                league="Premier League",
                kickoff=base + timedelta(days=4),
                home_goals=0,
                away_goals=2,
                odds={"home_win": 2.5},
            ),
            HistoricalMatch(
                match_id="4",
                home_team="Chelsea",
                away_team="Arsenal",
                league="Premier League",
                kickoff=base + timedelta(days=6),
                home_goals=0,
                away_goals=1,
                odds={"home_win": 2.3},
            ),
        ]

    def test_returns_team_form(self):
        form = calculate_recent_form(self.matches)

        self.assertIn("Arsenal", form)
        self.assertIn("Chelsea", form)
        self.assertIn("Liverpool", form)

    def test_counts_wins_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["wins"], 2)

    def test_counts_draws_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["draws"], 1)

    def test_counts_losses_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["losses"], 1)

    def test_calculates_points_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["points"], 7)

    def test_counts_goals_for_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["goals_for"], 4)

    def test_counts_goals_against_correctly(self):
        form = calculate_recent_form(self.matches)

        self.assertEqual(form["Arsenal"]["goals_against"], 3)

    def test_recent_match_limit_is_respected(self):
        form = calculate_recent_form(
            self.matches,
            recent_matches=2,
        )

        self.assertEqual(form["Arsenal"]["matches"], 2)

    def test_empty_matches_return_empty_form(self):
        form = calculate_recent_form([])

        self.assertEqual(form, {})

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            calculate_recent_form(None)

    def test_invalid_recent_match_count_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_recent_form(
                self.matches,
                recent_matches=0,
            )


if __name__ == "__main__":
    unittest.main()
