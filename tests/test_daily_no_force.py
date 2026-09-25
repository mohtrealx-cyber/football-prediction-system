from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_result import build_daily_result


class DailyNoForceTests(unittest.TestCase):

    def make_as_of(self):
        return datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

    def test_no_force_when_zero_candidates_exist(self):
        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value={
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
            },
        ):

            result = build_daily_result(
                [],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

    def test_no_force_when_too_few_selections_exist(self):
        fixtures = [
            "fixture-1",
            "fixture-2",
        ]

        expected_portfolio = {
            "status": "NO_BET",
            "reason": "insufficient qualifying selections",
        }

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=fixtures,
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=expected_portfolio,
        ):

            result = build_daily_result(
                fixtures,
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["portfolio"],
            expected_portfolio,
        )

    def test_runner_result_is_not_replaced_by_fallback(self):
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

        self.assertIs(
            result["portfolio"],
            expected_portfolio,
        )

    def test_no_bet_reason_is_preserved(self):
        expected_portfolio = {
            "status": "NO_BET",
            "reason": "no qualifying selections",
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
            result["portfolio"]["reason"],
            "no qualifying selections",
        )


if __name__ == "__main__":
    unittest.main()
