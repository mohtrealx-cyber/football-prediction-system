import unittest
from datetime import datetime, timezone

from backtesting.ticket_engine import backtest_ticket
from data.historical_models import HistoricalMatch


class TicketBacktestTests(unittest.TestCase):

    def make_match(
        self,
        match_id,
        home_team,
        away_team,
        home_goals,
        away_goals,
    ):
        return HistoricalMatch(
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            league="Test League",
            kickoff=datetime(
                2026,
                1,
                1,
                15,
                0,
                tzinfo=timezone.utc,
            ),
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

    def make_three_selections(self):
        return [
            {
                "match": self.make_match(
                    "MATCH-001",
                    "Home A",
                    "Away A",
                    2,
                    0,
                ),
                "market": "home_win",
                "odds": 2.00,
            },
            {
                "match": self.make_match(
                    "MATCH-002",
                    "Home B",
                    "Away B",
                    2,
                    1,
                ),
                "market": "over_2_5",
                "odds": 1.90,
            },
            {
                "match": self.make_match(
                    "MATCH-003",
                    "Home C",
                    "Away C",
                    1,
                    1,
                ),
                "market": "draw",
                "odds": 3.20,
            },
        ]

    def test_returns_dictionary(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertIsInstance(result, dict)

    def test_three_selection_ticket_is_accepted(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertEqual(result["selection_count"], 3)

    def test_all_winning_selections_make_ticket_win(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertTrue(result["won"])

    def test_one_losing_selection_makes_ticket_lose(self):
        selections = self.make_three_selections()

        selections[1]["match"] = self.make_match(
            "MATCH-002",
            "Home B",
            "Away B",
            1,
            0,
        )

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertFalse(result["won"])

    def test_combined_odds_are_multiplied(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        expected = 2.00 * 1.90 * 3.20

        self.assertAlmostEqual(
            result["combined_odds"],
            expected,
        )

    def test_stake_is_preserved(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            250.0,
        )

        self.assertEqual(
            result["stake"],
            250.0,
        )

    def test_winning_return_is_calculated(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        expected_return = 100.0 * (2.00 * 1.90 * 3.20)

        self.assertAlmostEqual(
            result["return_amount"],
            expected_return,
        )

    def test_winning_profit_is_calculated(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        expected_return = 100.0 * (2.00 * 1.90 * 3.20)
        expected_profit = expected_return - 100.0

        self.assertAlmostEqual(
            result["profit_loss"],
            expected_profit,
        )

    def test_losing_return_is_zero(self):
        selections = self.make_three_selections()

        selections[0]["match"] = self.make_match(
            "MATCH-001",
            "Home A",
            "Away A",
            0,
            2,
        )

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertAlmostEqual(
            result["return_amount"],
            0.0,
        )

    def test_losing_profit_equals_negative_stake(self):
        selections = self.make_three_selections()

        selections[0]["match"] = self.make_match(
            "MATCH-001",
            "Home A",
            "Away A",
            0,
            2,
        )

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertAlmostEqual(
            result["profit_loss"],
            -100.0,
        )

    def test_selection_results_are_returned(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        self.assertEqual(
            len(result["selections"]),
            3,
        )

    def test_selection_results_contain_market(self):
        selections = self.make_three_selections()

        result = backtest_ticket(
            selections,
            100.0,
        )

        markets = [
            selection["market"]
            for selection in result["selections"]
        ]

        self.assertIn("home_win", markets)
        self.assertIn("over_2_5", markets)
        self.assertIn("draw", markets)

    def test_non_list_selections_are_rejected(self):
        with self.assertRaises(TypeError):
            backtest_ticket(
                "not a list",
                100.0,
            )

    def test_invalid_stake_is_rejected(self):
        selections = self.make_three_selections()

        with self.assertRaises(ValueError):
            backtest_ticket(
                selections,
                0,
            )

    def test_fewer_than_three_selections_are_rejected(self):
        selections = self.make_three_selections()[:2]

        with self.assertRaises(ValueError):
            backtest_ticket(
                selections,
                100.0,
            )

    def test_duplicate_match_is_rejected(self):
        selections = self.make_three_selections()

        selections[1]["match"] = selections[0]["match"]

        with self.assertRaises(ValueError):
            backtest_ticket(
                selections,
                100.0,
            )


if __name__ == "__main__":
    unittest.main()
