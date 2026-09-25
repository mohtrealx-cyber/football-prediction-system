import unittest
from datetime import datetime, timedelta, timezone

from data.historical_models import HistoricalMatch
from backtesting.rolling import rolling_backtest


class RollingBacktestTests(unittest.TestCase):

    def make_match(
        self,
        match_id,
        home,
        away,
        days,
        home_goals,
        away_goals,
        home_odds=1.80,
    ):
        return HistoricalMatch(
            match_id=match_id,
            home_team=home,
            away_team=away,
            league="Test League",
            kickoff=datetime(
                2026,
                1,
                1,
                15,
                0,
                tzinfo=timezone.utc,
            ) + timedelta(days=days),
            home_goals=home_goals,
            away_goals=away_goals,
            odds={
                "home_win": home_odds,
                "draw": 3.50,
                "away_win": 4.50,
            },
        )

    def setUp(self):
        self.matches = [
            self.make_match(
                "M1", "A", "B", 0, 2, 0
            ),
            self.make_match(
                "M2", "B", "C", 1, 1, 1
            ),
            self.make_match(
                "M3", "C", "A", 2, 0, 2
            ),
            self.make_match(
                "M4", "A", "C", 3, 2, 1
            ),
            self.make_match(
                "M5", "C", "B", 4, 0, 1
            ),
            self.make_match(
                "M6", "B", "A", 5, 1, 0
            ),
        ]

    def test_returns_list(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        self.assertIsInstance(result, list)

    def test_matches_are_processed_chronologically(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        kickoff_times = [
            item["kickoff"]
            for item in result
        ]

        self.assertEqual(
            kickoff_times,
            sorted(kickoff_times),
        )

    def test_first_match_is_skipped_when_no_history_exists(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        match_ids = [
            item["match_id"]
            for item in result
        ]

        self.assertNotIn("M1", match_ids)

    def test_previous_matches_are_used_for_prediction(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        first_result = result[0]

        self.assertEqual(first_result["match_id"], "M2")
        self.assertGreaterEqual(
            first_result["history_matches"],
            1,
        )

    def test_future_matches_are_not_used(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertLess(
                item["history_cutoff"],
                item["kickoff"],
            )

    def test_target_match_is_not_in_its_own_history(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertNotEqual(
                item["match_id"],
                item["history_last_match_id"],
            )

    def test_prediction_probability_is_returned(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertIn(
                "model_probability",
                item,
            )

            self.assertGreaterEqual(
                item["model_probability"],
                0.0,
            )

            self.assertLessEqual(
                item["model_probability"],
                1.0,
            )

    def test_odds_are_preserved(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertIn("odds", item)
            self.assertGreater(item["odds"], 1.0)

    def test_results_are_settled(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertIn("won", item)
            self.assertIsInstance(item["won"], bool)

    def test_profit_and_return_are_calculated(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
        )

        for item in result:
            self.assertIn(
                "return_amount",
                item,
            )

            self.assertIn(
                "profit_loss",
                item,
            )

    def test_stake_is_preserved(self):
        result = rolling_backtest(
            self.matches,
            market="home_win",
            stake=10.0,
        )

        for item in result:
            self.assertEqual(
                item["stake"],
                10.0,
            )

    def test_invalid_market_is_rejected(self):
        with self.assertRaises(ValueError):
            rolling_backtest(
                self.matches,
                market="invalid_market",
            )

    def test_invalid_stake_is_rejected(self):
        with self.assertRaises(ValueError):
            rolling_backtest(
                self.matches,
                market="home_win",
                stake=0,
            )

    def test_non_list_matches_are_rejected(self):
        with self.assertRaises(TypeError):
            rolling_backtest(
                "not a list",
                market="home_win",
            )


if __name__ == "__main__":
    unittest.main()
