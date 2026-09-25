import unittest
from datetime import datetime, timezone

from backtesting.engine import backtest_selection
from data.historical_models import HistoricalMatch


class BacktestSelectionTests(unittest.TestCase):

    def make_match(self, home_goals, away_goals):
        return HistoricalMatch(
            match_id="TEST-001",
            home_team="Home FC",
            away_team="Away FC",
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

    def test_returns_dictionary(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertIsInstance(result, dict)

    def test_winning_selection_is_marked_true(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertTrue(result["won"])

    def test_losing_selection_is_marked_false(self):
        match = self.make_match(0, 2)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertFalse(result["won"])

    def test_market_is_preserved(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertEqual(result["market"], "home_win")

    def test_odds_are_preserved(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertEqual(result["odds"], 2.00)

    def test_stake_is_preserved(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertEqual(result["stake"], 100.0)

    def test_match_id_is_preserved(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertEqual(result["match_id"], "TEST-001")

    def test_winning_return_is_calculated_correctly(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertAlmostEqual(
            result["return_amount"],
            200.0,
        )

    def test_winning_profit_is_calculated_correctly(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertAlmostEqual(
            result["profit_loss"],
            100.0,
        )

    def test_losing_return_is_zero(self):
        match = self.make_match(0, 2)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertAlmostEqual(
            result["return_amount"],
            0.0,
        )

    def test_losing_profit_equals_negative_stake(self):
        match = self.make_match(0, 2)

        result = backtest_selection(
            match,
            "home_win",
            2.00,
            100.0,
        )

        self.assertAlmostEqual(
            result["profit_loss"],
            -100.0,
        )

    def test_draw_market_can_be_backtested(self):
        match = self.make_match(1, 1)

        result = backtest_selection(
            match,
            "draw",
            3.20,
            50.0,
        )

        self.assertTrue(result["won"])
        self.assertAlmostEqual(
            result["return_amount"],
            160.0,
        )
        self.assertAlmostEqual(
            result["profit_loss"],
            110.0,
        )

    def test_over_2_5_can_be_backtested(self):
        match = self.make_match(2, 1)

        result = backtest_selection(
            match,
            "over_2_5",
            1.90,
            100.0,
        )

        self.assertTrue(result["won"])

    def test_btts_no_can_be_backtested(self):
        match = self.make_match(2, 0)

        result = backtest_selection(
            match,
            "btts_no",
            2.00,
            100.0,
        )

        self.assertTrue(result["won"])

    def test_invalid_match_is_rejected(self):
        with self.assertRaises(TypeError):
            backtest_selection(
                "not a match",
                "home_win",
                2.00,
                100.0,
            )

    def test_invalid_market_is_rejected(self):
        match = self.make_match(2, 1)

        with self.assertRaises(ValueError):
            backtest_selection(
                match,
                "invalid_market",
                2.00,
                100.0,
            )

    def test_invalid_odds_are_rejected(self):
        match = self.make_match(2, 1)

        with self.assertRaises(ValueError):
            backtest_selection(
                match,
                "home_win",
                1.0,
                100.0,
            )

    def test_non_numeric_odds_are_rejected(self):
        match = self.make_match(2, 1)

        with self.assertRaises(ValueError):
            backtest_selection(
                match,
                "home_win",
                "2.00",
                100.0,
            )

    def test_invalid_stake_is_rejected(self):
        match = self.make_match(2, 1)

        with self.assertRaises(ValueError):
            backtest_selection(
                match,
                "home_win",
                2.00,
                0,
            )

    def test_non_numeric_stake_is_rejected(self):
        match = self.make_match(2, 1)

        with self.assertRaises(ValueError):
            backtest_selection(
                match,
                "home_win",
                2.00,
                "100",
            )


if __name__ == "__main__":
    unittest.main()
