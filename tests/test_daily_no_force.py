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

    def test_empty_pipeline_portfolio_becomes_no_bet(self):
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
            result["portfolio"]["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["reason"],
            "insufficient qualifying selections",
        )

        self.assertEqual(
            result["portfolio"]["tickets"],
            [],
        )

    def test_empty_pipeline_portfolio_does_not_become_fake_ticket(self):
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
            result["portfolio"]["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["tickets"],
            [],
        )

    def test_existing_no_bet_result_is_preserved(self):
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

    def test_non_empty_portfolio_is_preserved(self):
        expected_portfolio = [
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
            return_value=expected_portfolio,
        ):

            result = build_daily_result(
                ["fixture-1"],
                [],
                self.make_as_of(),
            )

        self.assertIs(
            result["portfolio"],
            expected_portfolio,
        )

    def test_no_bet_reason_is_exact(self):
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
            result["portfolio"]["reason"],
            "insufficient qualifying selections",
        )

    def test_daily_metadata_is_preserved_for_no_bet(self):
        as_of = self.make_as_of()

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
                as_of,
            )

        self.assertEqual(
            result["as_of"],
            as_of,
        )

        self.assertEqual(
            result["fixtures_received"],
            0,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
