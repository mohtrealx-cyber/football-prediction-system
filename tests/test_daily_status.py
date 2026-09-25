from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_result import build_daily_result


class DailyStatusTests(unittest.TestCase):

    def make_as_of(self):
        return datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

    def test_non_empty_portfolio_has_ready_status(self):
        portfolio = [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=["fixture-1"],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=portfolio,
        ):

            result = build_daily_result(
                ["fixture-1"],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["status"],
            "READY",
        )

        self.assertIs(
            result["portfolio"],
            portfolio,
        )

    def test_empty_portfolio_has_no_bet_status(self):
        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=[],
        ):

            result = build_daily_result(
                [],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

    def test_no_bet_portfolio_status_is_consistent(self):
        expected_portfolio = {
            "status": "NO_BET",
            "reason": "insufficient qualifying selections",
            "tickets": [],
        }

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=expected_portfolio,
        ):

            result = build_daily_result(
                [],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

    def test_ready_result_keeps_execution_metadata(self):
        portfolio = [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

        fixtures = [
            "fixture-1",
            "fixture-2",
        ]

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=["fixture-2"],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=portfolio,
        ):

            result = build_daily_result(
                fixtures,
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["status"],
            "READY",
        )

        self.assertEqual(
            result["fixtures_received"],
            2,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            1,
        )

    def test_unknown_portfolio_status_is_not_invented(self):
        portfolio = {
            "status": "CUSTOM",
            "data": "test",
        }

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=["fixture-1"],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=portfolio,
        ):

            result = build_daily_result(
                ["fixture-1"],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["status"],
            "READY",
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "CUSTOM",
        )


if __name__ == "__main__":
    unittest.main()
