import json
import unittest
from datetime import datetime, timedelta, timezone

from data.historical_models import HistoricalMatch
from data.models import Match
from pipeline.daily_report_output import build_daily_report_output


MARKETS = (
    "home_win",
    "draw",
    "away_win",
    "over_2_5",
    "under_2_5",
    "btts_yes",
    "btts_no",
)


class FinalDailySystemTests(unittest.TestCase):

    def setUp(self):
        self.as_of = datetime(
            2026,
            9,
            25,
            10,
            0,
            tzinfo=timezone.utc,
        )

    def _history(self):
        base_time = datetime(
            2026,
            9,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        )

        historical_pairs = [
            ("TeamA", "TeamB"),
            ("TeamC", "TeamD"),
            ("TeamE", "TeamF"),
            ("TeamG", "TeamH"),
            ("TeamI", "TeamJ"),
            ("TeamK", "TeamL"),
            ("TeamA", "TeamC"),
            ("TeamD", "TeamE"),
            ("TeamF", "TeamG"),
            ("TeamH", "TeamI"),
            ("TeamJ", "TeamK"),
            ("TeamL", "TeamA"),
        ]

        results = [
            (2, 0),
            (1, 1),
            (2, 1),
            (1, 0),
            (3, 1),
            (1, 2),
            (2, 0),
            (0, 0),
            (2, 1),
            (1, 1),
            (3, 0),
            (0, 2),
        ]

        history = []

        for index, (
            (home_team, away_team),
            (home_goals, away_goals),
        ) in enumerate(zip(historical_pairs, results)):

            history.append(
                HistoricalMatch(
                    match_id=f"h{index + 1}",
                    home_team=home_team,
                    away_team=away_team,
                    league="TEST_LEAGUE",
                    kickoff=base_time + timedelta(hours=index * 6),
                    home_goals=home_goals,
                    away_goals=away_goals,
                    odds={},
                )
            )

        return history

    def _fixtures(self):
        fixture_pairs = [
            ("TeamA", "TeamB"),
            ("TeamC", "TeamD"),
            ("TeamE", "TeamF"),
            ("TeamG", "TeamH"),
            ("TeamI", "TeamJ"),
            ("TeamK", "TeamL"),
            ("TeamA", "TeamC"),
            ("TeamD", "TeamE"),
            ("TeamF", "TeamG"),
            ("TeamH", "TeamI"),
            ("TeamJ", "TeamK"),
            ("TeamL", "TeamA"),
        ]

        fixtures = []

        for index, (home_team, away_team) in enumerate(fixture_pairs):

            odds = {
                market: 10.0
                for market in MARKETS
            }

            fixtures.append(
                Match(
                    match_id=f"m{index + 1}",
                    home_team=home_team,
                    away_team=away_team,
                    league="TEST_LEAGUE",
                    kickoff=(
                        datetime(
                            2026,
                            9,
                            25,
                            12,
                            0,
                            tzinfo=timezone.utc,
                        )
                        + timedelta(hours=index)
                    ),
                    status="scheduled",
                    odds=odds,
                )
            )

        return fixtures

    def test_complete_daily_system_returns_report(self):
        fixtures = self._fixtures()
        history = self._history()

        result = build_daily_report_output(
            fixtures,
            history,
            self.as_of,
        )

        self.assertIsInstance(result, dict)

        self.assertEqual(
            result["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )

        self.assertIn(
            result["status"],
            {
                "READY",
                "NO_BET",
            },
        )

    def test_complete_daily_system_is_json_serializable(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        serialized = json.dumps(result)

        self.assertIsInstance(
            serialized,
            str,
        )

    def test_daily_metadata_is_correct(self):
        fixtures = self._fixtures()

        result = build_daily_report_output(
            fixtures,
            self._history(),
            self.as_of,
        )

        self.assertEqual(
            result["fixtures_received"],
            12,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            12,
        )

    def test_ready_portfolio_has_four_tickets(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        self.assertIsInstance(
            portfolio,
            list,
        )

        self.assertEqual(
            len(portfolio),
            4,
        )

        ticket_names = {
            ticket["name"]
            for ticket in portfolio
        }

        self.assertEqual(
            ticket_names,
            {
                "IRONCLAD",
                "BALANCED",
                "VOLATILITY",
                "BENCHMARK",
            },
        )

    def test_ready_portfolio_has_valid_stakes(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        expected_stakes = {
            "IRONCLAD": 40.0,
            "BALANCED": 30.0,
            "VOLATILITY": 20.0,
            "BENCHMARK": 10.0,
        }

        actual_stakes = {
            ticket["name"]: ticket["stake_percent"]
            for ticket in portfolio
        }

        self.assertEqual(
            actual_stakes,
            expected_stakes,
        )

    def test_ready_portfolio_contains_valid_ticket_structure(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        for ticket in portfolio:
            self.assertIn(
                "name",
                ticket,
            )

            self.assertIn(
                "stake_percent",
                ticket,
            )

            self.assertIn(
                "selections",
                ticket,
            )

            self.assertIn(
                ticket["name"],
                {
                    "IRONCLAD",
                    "BALANCED",
                    "VOLATILITY",
                    "BENCHMARK",
                },
            )

            self.assertIsInstance(
                ticket["stake_percent"],
                (int, float),
            )

            self.assertIsInstance(
                ticket["selections"],
                list,
            )

    def test_ready_portfolio_stakes_total_100_percent(self):
        result = build_daily_report_output(
            self._fixtures(),
            self._history(),
            self.as_of,
        )

        if result["status"] == "NO_BET":
            self.skipTest(
                "No qualifying portfolio was produced."
            )

        portfolio = result["portfolio"]

        total_stake = sum(
            ticket["stake_percent"]
            for ticket in portfolio
        )

        self.assertEqual(
            total_stake,
            100.0,
        )

    def test_empty_inputs_produce_no_bet(self):
        result = build_daily_report_output(
            [],
            [],
            self.as_of,
        )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["fixtures_received"],
            0,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            0,
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

    def test_inputs_are_not_modified(self):
        fixtures = self._fixtures()
        history = self._history()

        original_fixture_ids = [
            fixture.match_id
            for fixture in fixtures
        ]

        original_history_ids = [
            match.match_id
            for match in history
        ]

        build_daily_report_output(
            fixtures,
            history,
            self.as_of,
        )

        self.assertEqual(
            [
                fixture.match_id
                for fixture in fixtures
            ],
            original_fixture_ids,
        )

        self.assertEqual(
            [
                match.match_id
                for match in history
            ],
            original_history_ids,
        )

    def test_naive_as_of_is_rejected(self):
        naive_as_of = datetime(
            2026,
            9,
            25,
            10,
            0,
        )

        with self.assertRaises(ValueError):
            build_daily_report_output(
                self._fixtures(),
                self._history(),
                naive_as_of,
            )

    def test_invalid_fixture_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                "not-a-list",
                self._history(),
                self.as_of,
            )

    def test_invalid_history_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                self._fixtures(),
                "not-a-list",
                self.as_of,
            )


if __name__ == "__main__":
    unittest.main()
