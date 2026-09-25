from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from data.models import Match
from pipeline.guarded_daily_portfolio import (
    build_guarded_daily_portfolio,
)


class GuardedDailyPortfolioTests(unittest.TestCase):

    def make_fixture(
        self,
        match_id: str,
        hour: int,
        status: str = "scheduled",
    ) -> Match:
        return Match(
            match_id=match_id,
            home_team=f"Home{match_id}",
            away_team=f"Away{match_id}",
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                25,
                hour,
                0,
                tzinfo=timezone.utc,
            ),
            status=status,
            odds={
                "home_win": 1.80,
                "draw": 3.50,
                "away_win": 4.50,
            },
        )

    def test_only_upcoming_fixtures_are_passed_forward(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("past", 13),
            self.make_fixture("exact", 14),
            self.make_fixture("future", 15),
        ]

        expected_portfolio = ["portfolio"]

        filtered_fixtures = [
            fixtures[2],
        ]

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            return_value=filtered_fixtures,
        ) as time_guard, patch(
            "pipeline.guarded_daily_portfolio.build_daily_real_portfolio",
            return_value=expected_portfolio,
        ) as portfolio_builder:

            result = build_guarded_daily_portfolio(
                fixtures,
                [],
                as_of,
            )

        time_guard.assert_called_once_with(
            fixtures,
            as_of,
        )

        portfolio_builder.assert_called_once_with(
            filtered_fixtures,
            [],
        )

        self.assertEqual(
            result,
            expected_portfolio,
        )

    def test_time_guard_is_called_before_portfolio_builder(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
        ]

        call_order = []

        def fake_guard(
            incoming_fixtures,
            incoming_as_of,
        ):
            call_order.append("guard")

            self.assertIs(
                incoming_fixtures,
                fixtures,
            )

            self.assertEqual(
                incoming_as_of,
                as_of,
            )

            return fixtures

        def fake_builder(
            incoming_fixtures,
            incoming_history,
        ):
            call_order.append("builder")

            self.assertIs(
                incoming_fixtures,
                fixtures,
            )

            return ["portfolio"]

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            side_effect=fake_guard,
        ), patch(
            "pipeline.guarded_daily_portfolio.build_daily_real_portfolio",
            side_effect=fake_builder,
        ):
            result = build_guarded_daily_portfolio(
                fixtures,
                [],
                as_of,
            )

        self.assertEqual(
            result,
            ["portfolio"],
        )

        self.assertEqual(
            call_order,
            [
                "guard",
                "builder",
            ],
        )

    def test_time_guard_failure_is_propagated(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
        ]

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            side_effect=ValueError(
                "invalid as_of"
            ),
        ):

            with self.assertRaises(ValueError):
                build_guarded_daily_portfolio(
                    fixtures,
                    [],
                    as_of,
                )

    def test_portfolio_builder_failure_is_propagated(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
        ]

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            return_value=fixtures,
        ), patch(
            "pipeline.guarded_daily_portfolio.build_daily_real_portfolio",
            side_effect=ValueError(
                "portfolio failed"
            ),
        ):

            with self.assertRaises(ValueError):
                build_guarded_daily_portfolio(
                    fixtures,
                    [],
                    as_of,
                )

    def test_input_fixture_list_is_not_modified(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
            self.make_fixture("m2", 16),
        ]

        original = list(fixtures)

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            return_value=fixtures,
        ), patch(
            "pipeline.guarded_daily_portfolio.build_daily_real_portfolio",
            return_value=[],
        ):
            build_guarded_daily_portfolio(
                fixtures,
                [],
                as_of,
            )

        self.assertEqual(
            fixtures,
            original,
        )

    def test_input_history_list_is_not_modified(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
        ]

        history = [
            "history-1",
            "history-2",
        ]

        original = list(history)

        with patch(
            "pipeline.guarded_daily_portfolio.filter_upcoming_fixtures",
            return_value=fixtures,
        ), patch(
            "pipeline.guarded_daily_portfolio.build_daily_real_portfolio",
            return_value=[],
        ) as builder:

            build_guarded_daily_portfolio(
                fixtures,
                history,
                as_of,
            )

        builder.assert_called_once_with(
            fixtures,
            history,
        )

        self.assertEqual(
            history,
            original,
        )

    def test_non_list_fixtures_are_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            build_guarded_daily_portfolio(
                "not a list",
                [],
                as_of,
            )

    def test_non_list_history_is_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        fixtures = [
            self.make_fixture("m1", 15),
        ]

        with self.assertRaises(TypeError):
            build_guarded_daily_portfolio(
                fixtures,
                "not a list",
                as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        fixtures = [
            self.make_fixture("m1", 15),
        ]

        with self.assertRaises(TypeError):
            build_guarded_daily_portfolio(
                fixtures,
                [],
                "2026-09-25T14:00:00Z",
            )

    def test_naive_as_of_is_rejected(self):
        fixtures = [
            self.make_fixture("m1", 15),
        ]

        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
        )

        with self.assertRaises(ValueError):
            build_guarded_daily_portfolio(
                fixtures,
                [],
                as_of,
            )


if __name__ == "__main__":
    unittest.main()
