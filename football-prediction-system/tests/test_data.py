import unittest
from datetime import datetime

from data.loader import validate_matches
from data.models import Match


class MatchDataTests(unittest.TestCase):

    def setUp(self):
        self.valid_match = Match(
            match_id="M001",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="scheduled",
            odds={
                "home": 1.80,
                "draw": 3.50,
                "away": 4.20,
            },
        )

    def test_valid_match_is_accepted(self):
        matches = validate_matches([self.valid_match])

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].home_team, "Arsenal")

    def test_empty_match_id_is_rejected(self):
        match = Match(
            match_id="",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="scheduled",
            odds={"home": 1.80},
        )

        with self.assertRaises(ValueError):
            validate_matches([match])

    def test_empty_team_is_rejected(self):
        match = Match(
            match_id="M002",
            home_team="",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="scheduled",
            odds={"home": 1.80},
        )

        with self.assertRaises(ValueError):
            validate_matches([match])

    def test_invalid_status_is_rejected(self):
        match = Match(
            match_id="M003",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="unknown",
            odds={"home": 1.80},
        )

        with self.assertRaises(ValueError):
            validate_matches([match])

    def test_invalid_odds_are_rejected(self):
        match = Match(
            match_id="M004",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="scheduled",
            odds={"home": 1.00},
        )

        with self.assertRaises(ValueError):
            validate_matches([match])

    def test_empty_odds_are_rejected(self):
        match = Match(
            match_id="M005",
            home_team="Arsenal",
            away_team="Chelsea",
            league="Premier League",
            kickoff=datetime(2026, 9, 24, 20, 0),
            status="scheduled",
            odds={},
        )

        with self.assertRaises(ValueError):
            validate_matches([match])

    def test_multiple_matches_can_be_loaded(self):
        second_match = Match(
            match_id="M002",
            home_team="Liverpool",
            away_team="Everton",
            league="Premier League",
            kickoff=datetime(2026, 9, 25, 19, 30),
            status="scheduled",
            odds={
                "home": 1.60,
                "draw": 3.80,
                "away": 5.20,
            },
        )

        matches = validate_matches(
            [self.valid_match, second_match]
        )

        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[1].away_team, "Everton")


if __name__ == "__main__":
    unittest.main()
