import unittest
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch


class TestHistoricalMatch(unittest.TestCase):

    def setUp(self):
        self.valid_match = HistoricalMatch(
            match_id="HIST-001",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(
                2026,
                9,
                20,
                15,
                0,
                tzinfo=timezone.utc,
            ),
            home_goals=2,
            away_goals=1,
            odds={
                "home_win": 2.00,
                "draw": 3.40,
                "away_win": 3.80,
            },
        )

    def test_valid_historical_match_is_accepted(self):
        self.assertEqual(
            self.valid_match.match_id,
            "HIST-001",
        )

    def test_match_data_is_stored(self):
        self.assertEqual(
            self.valid_match.home_team,
            "Arsenal",
        )
        self.assertEqual(
            self.valid_match.away_team,
            "Chelsea",
        )
        self.assertEqual(
            self.valid_match.league,
            "Premier League",
        )

    def test_score_is_stored(self):
        self.assertEqual(
            self.valid_match.home_goals,
            2,
        )
        self.assertEqual(
            self.valid_match.away_goals,
            1,
        )

    def test_odds_are_stored(self):
        self.assertEqual(
            self.valid_match.odds["home_win"],
            2.00,
        )

    def test_naive_kickoff_is_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalMatch(
                match_id="HIST-002",
                home_team="Team A",
                away_team="Team B",
                league="League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                ),
                home_goals=1,
                away_goals=0,
                odds={"home_win": 2.0},
            )

    def test_negative_home_goals_are_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalMatch(
                match_id="HIST-003",
                home_team="Team A",
                away_team="Team B",
                league="League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals=-1,
                away_goals=0,
                odds={"home_win": 2.0},
            )

    def test_negative_away_goals_are_rejected(self):
        with self.assertRaises(ValueError):
            HistoricalMatch(
                match_id="HIST-004",
                home_team="Team A",
                away_team="Team B",
                league="League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals=0,
                away_goals=-1,
                odds={"home_win": 2.0},
            )

    def test_invalid_home_goals_type_is_rejected(self):
        with self.assertRaises(TypeError):
            HistoricalMatch(
                match_id="HIST-005",
                home_team="Team A",
                away_team="Team B",
                league="League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals="2",
                away_goals=1,
                odds={"home_win": 2.0},
            )

    def test_invalid_odds_type_is_rejected(self):
        with self.assertRaises(TypeError):
            HistoricalMatch(
                match_id="HIST-006",
                home_team="Team A",
                away_team="Team B",
                league="League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals=2,
                away_goals=1,
                odds=None,
            )


if __name__ == "__main__":
    unittest.main()
