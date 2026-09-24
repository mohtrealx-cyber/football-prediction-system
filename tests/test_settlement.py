import unittest
from datetime import datetime, timezone

from backtesting.settlement import settle_market
from data.historical_models import HistoricalMatch


class SettlementTests(unittest.TestCase):

    def make_match(self, home_goals, away_goals):
        return HistoricalMatch(
            match_id="TEST-001",
            home_team="Home FC",
            away_team="Away FC",
            league="Test League",
            kickoff=datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc),
            home_goals=home_goals,
            away_goals=away_goals,
            odds={
                "home_win": 2.00,
                "draw": 3.20,
                "away_win": 3.50,
                "over_2_5": 1.90,
                "under_2_5": 1.90,
                "btts_yes": 1.80,
                "btts_no": 2.00,
            },
        )

    def test_home_win_is_winner(self):
        match = self.make_match(2, 1)

        result = settle_market(match, "home_win")

        self.assertTrue(result)

    def test_draw_is_winner(self):
        match = self.make_match(1, 1)

        result = settle_market(match, "draw")

        self.assertTrue(result)

    def test_away_win_is_winner(self):
        match = self.make_match(1, 2)

        result = settle_market(match, "away_win")

        self.assertTrue(result)

    def test_over_2_5_is_winner(self):
        match = self.make_match(2, 1)

        result = settle_market(match, "over_2_5")

        self.assertTrue(result)

    def test_under_2_5_is_winner(self):
        match = self.make_match(1, 1)

        result = settle_market(match, "under_2_5")

        self.assertTrue(result)

    def test_btts_yes_is_winner(self):
        match = self.make_match(2, 1)

        result = settle_market(match, "btts_yes")

        self.assertTrue(result)

    def test_btts_no_is_winner(self):
        match = self.make_match(2, 0)

        result = settle_market(match, "btts_no")

        self.assertTrue(result)

    def test_home_win_is_false_when_away_wins(self):
        match = self.make_match(0, 2)

        result = settle_market(match, "home_win")

        self.assertFalse(result)

    def test_draw_is_false_when_match_is_not_draw(self):
        match = self.make_match(2, 1)

        result = settle_market(match, "draw")

        self.assertFalse(result)

    def test_away_win_is_false_when_home_wins(self):
        match = self.make_match(2, 0)

        result = settle_market(match, "away_win")

        self.assertFalse(result)

    def test_over_2_5_is_false_for_two_goals(self):
        match = self.make_match(1, 1)

        result = settle_market(match, "over_2_5")

        self.assertFalse(result)

    def test_under_2_5_is_false_for_three_goals(self):
        match = self.make_match(2, 1)

        result = settle_market(match, "under_2_5")

        self.assertFalse(result)

    def test_btts_yes_is_false_when_one_team_scores_zero(self):
        match = self.make_match(2, 0)

        result = settle_market(match, "btts_yes")

        self.assertFalse(result)

    def test_btts_no_is_false_when_both_teams_score(self):
        match = self.make_match(1, 1)

        result = settle_market(match, "btts_no")

        self.assertFalse(result)

    def test_invalid_market_is_rejected(self):
        match = self.make_match(1, 0)

        with self.assertRaises(ValueError):
            settle_market(match, "invalid_market")

    def test_invalid_match_is_rejected(self):
        with self.assertRaises(TypeError):
            settle_market("not a match", "home_win")


if __name__ == "__main__":
    unittest.main()
