import unittest
from datetime import datetime, timezone

from backtesting.multi_market_rolling import rolling_backtest_all_markets
from data.historical_models import HistoricalMatch
from markets.engine import get_supported_markets


class RollingMultiMarketBacktestTests(unittest.TestCase):

    def setUp(self):
        utc = timezone.utc

        self.matches = [
            HistoricalMatch(
                match_id="M1",
                home_team="Team A",
                away_team="Team B",
                league="Test League",
                kickoff=datetime(2026, 1, 1, 15, 0, tzinfo=utc),
                home_goals=2,
                away_goals=0,
                odds={
                    "home_win": 1.50,
                    "draw": 3.50,
                    "away_win": 6.00,
                    "over_2_5": 1.80,
                    "under_2_5": 2.00,
                    "btts_yes": 1.70,
                    "btts_no": 2.10,
                },
            ),
            HistoricalMatch(
                match_id="M2",
                home_team="Team C",
                away_team="Team D",
                league="Test League",
                kickoff=datetime(2026, 1, 2, 15, 0, tzinfo=utc),
                home_goals=1,
                away_goals=1,
                odds={
                    "home_win": 2.00,
                    "draw": 3.20,
                    "away_win": 3.50,
                    "over_2_5": 2.00,
                    "under_2_5": 1.80,
                    "btts_yes": 1.75,
                    "btts_no": 2.00,
                },
            ),
            HistoricalMatch(
                match_id="M3",
                home_team="Team A",
                away_team="Team C",
                league="Test League",
                kickoff=datetime(2026, 1, 3, 15, 0, tzinfo=utc),
                home_goals=0,
                away_goals=2,
                odds={
                    "home_win": 2.40,
                    "draw": 3.10,
                    "away_win": 2.80,
                    "over_2_5": 2.10,
                    "under_2_5": 1.70,
                    "btts_yes": 1.90,
                    "btts_no": 1.85,
                },
            ),
            HistoricalMatch(
                match_id="M4",
                home_team="Team B",
                away_team="Team D",
                league="Test League",
                kickoff=datetime(2026, 1, 4, 15, 0, tzinfo=utc),
                home_goals=3,
                away_goals=1,
                odds={
                    "home_win": 1.70,
                    "draw": 3.60,
                    "away_win": 4.80,
                    "over_2_5": 1.75,
                    "under_2_5": 2.05,
                    "btts_yes": 1.65,
                    "btts_no": 2.15,
                },
            ),
            HistoricalMatch(
                match_id="M5",
                home_team="Team C",
                away_team="Team A",
                league="Test League",
                kickoff=datetime(2026, 1, 5, 15, 0, tzinfo=utc),
                home_goals=2,
                away_goals=2,
                odds={
                    "home_win": 2.30,
                    "draw": 3.30,
                    "away_win": 2.90,
                    "over_2_5": 1.65,
                    "under_2_5": 2.15,
                    "btts_yes": 1.60,
                    "btts_no": 2.20,
                },
            ),
            HistoricalMatch(
                match_id="M6",
                home_team="Team D",
                away_team="Team B",
                league="Test League",
                kickoff=datetime(2026, 1, 6, 15, 0, tzinfo=utc),
                home_goals=0,
                away_goals=1,
                odds={
                    "home_win": 3.20,
                    "draw": 3.10,
                    "away_win": 2.10,
                    "over_2_5": 1.90,
                    "under_2_5": 1.90,
                    "btts_yes": 2.00,
                    "btts_no": 1.75,
                },
            ),
        ]

    def test_returns_dictionary(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        self.assertIsInstance(result, dict)

    def test_all_supported_markets_are_present(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        self.assertEqual(
            set(result.keys()),
            set(get_supported_markets()),
        )

    def test_all_seven_markets_are_present(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        expected_markets = {
            "home_win",
            "draw",
            "away_win",
            "over_2_5",
            "under_2_5",
            "btts_yes",
            "btts_no",
        }

        self.assertEqual(
            set(result.keys()),
            expected_markets,
        )

    def test_each_market_returns_a_list(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            self.assertIsInstance(result[market], list)

    def test_first_match_is_skipped_for_every_market(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            match_ids = [
                item["match_id"]
                for item in result[market]
            ]

            self.assertNotIn("M1", match_ids)

    def test_each_market_uses_rolling_history(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            self.assertEqual(len(result[market]), 5)

    def test_results_are_chronological_for_every_market(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            kickoffs = [
                item["kickoff"]
                for item in result[market]
            ]

            self.assertEqual(
                kickoffs,
                sorted(kickoffs),
            )

    def test_market_name_is_preserved(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                self.assertEqual(
                    item["market"],
                    market,
                )

    def test_stake_is_applied_to_every_market_result(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=25.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                self.assertEqual(
                    item["stake"],
                    25.0,
                )

    def test_results_contain_required_fields(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        required_fields = {
            "match_id",
            "home_team",
            "away_team",
            "league",
            "kickoff",
            "market",
            "model_probability",
            "odds",
            "stake",
            "won",
            "return_amount",
            "profit_loss",
            "history_matches",
            "history_cutoff",
            "history_last_match_id",
        }

        for market in get_supported_markets():
            for item in result[market]:
                self.assertTrue(
                    required_fields.issubset(item.keys())
                )

    def test_future_matches_are_not_used(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                self.assertLess(
                    item["history_cutoff"],
                    item["kickoff"],
                )

    def test_history_count_grows_over_time(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            history_counts = [
                item["history_matches"]
                for item in result[market]
            ]

            self.assertEqual(
                history_counts,
                [1, 2, 3, 4, 5],
            )

    def test_history_last_match_is_before_target(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        kickoff_by_id = {
            match.match_id: match.kickoff
            for match in self.matches
        }

        for market in get_supported_markets():
            for item in result[market]:
                last_history_id = item["history_last_match_id"]

                self.assertLess(
                    kickoff_by_id[last_history_id],
                    item["kickoff"],
                )

    def test_model_probability_is_valid(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                probability = item["model_probability"]

                self.assertGreaterEqual(
                    probability,
                    0.0,
                )

                self.assertLessEqual(
                    probability,
                    1.0,
                )

    def test_odds_are_greater_than_one(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                self.assertGreater(
                    item["odds"],
                    1.0,
                )

    def test_settlement_result_is_boolean(self):
        result = rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        for market in get_supported_markets():
            for item in result[market]:
                self.assertIsInstance(
                    item["won"],
                    bool,
                )

    def test_input_list_is_not_modified(self):
        original_ids = [
            match.match_id
            for match in self.matches
        ]

        rolling_backtest_all_markets(
            self.matches,
            stake=10.0,
        )

        after_ids = [
            match.match_id
            for match in self.matches
        ]

        self.assertEqual(
            after_ids,
            original_ids,
        )

    def test_non_list_matches_are_rejected(self):
        with self.assertRaises(TypeError):
            rolling_backtest_all_markets(
                "not a list",
                stake=10.0,
            )

    def test_invalid_match_item_is_rejected(self):
        with self.assertRaises(TypeError):
            rolling_backtest_all_markets(
                [self.matches[0], "invalid"],
                stake=10.0,
            )

    def test_invalid_stake_is_rejected(self):
        with self.assertRaises(ValueError):
            rolling_backtest_all_markets(
                self.matches,
                stake=0,
            )

    def test_non_numeric_stake_is_rejected(self):
        with self.assertRaises(TypeError):
            rolling_backtest_all_markets(
                self.matches,
                stake="10",
            )


if __name__ == "__main__":
    unittest.main()
