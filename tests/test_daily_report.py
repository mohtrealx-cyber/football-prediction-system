from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_report import build_daily_report


class DailyReportTests(unittest.TestCase):

    def make_as_of(self):
        return datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

    def test_ready_result_is_converted_to_report(self):
        daily_result = {
            "status": "READY",
            "as_of": self.make_as_of(),
            "fixtures_received": 10,
            "upcoming_fixtures": 7,
            "portfolio": [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        }

        with patch(
            "pipeline.daily_report.build_daily_result",
            return_value=daily_result,
        ) as builder:

            result = build_daily_report(
                ["fixture-1"],
                ["history-1"],
                self.make_as_of(),
            )

        builder.assert_called_once_with(
            ["fixture-1"],
            ["history-1"],
            self.make_as_of(),
        )

        self.assertEqual(
            result["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )

        self.assertEqual(
            result["status"],
            "READY",
        )

        self.assertEqual(
            result["as_of"],
            daily_result["as_of"],
        )

        self.assertEqual(
            result["fixtures_received"],
            10,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            7,
        )

        self.assertIs(
            result["portfolio"],
            daily_result["portfolio"],
        )

    def test_no_bet_result_is_preserved(self):
        daily_result = {
            "status": "NO_BET",
            "as_of": self.make_as_of(),
            "fixtures_received": 5,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        with patch(
            "pipeline.daily_report.build_daily_result",
            return_value=daily_result,
        ):

            result = build_daily_report(
                [],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            result["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["status"],
            "NO_BET",
        )

        self.assertEqual(
            result["portfolio"]["reason"],
            "insufficient qualifying selections",
        )

    def test_daily_result_is_not_modified(self):
        daily_result = {
            "status": "READY",
            "as_of": self.make_as_of(),
            "fixtures_received": 3,
            "upcoming_fixtures": 2,
            "portfolio": [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        }

        with patch(
            "pipeline.daily_report.build_daily_result",
            return_value=daily_result,
        ):

            original = dict(daily_result)

            build_daily_report(
                [],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            daily_result,
            original,
        )

        self.assertNotIn(
            "report_type",
            daily_result,
        )

    def test_report_returns_new_dictionary(self):
        daily_result = {
            "status": "READY",
            "as_of": self.make_as_of(),
            "fixtures_received": 1,
            "upcoming_fixtures": 1,
            "portfolio": [],
        }

        with patch(
            "pipeline.daily_report.build_daily_result",
            return_value=daily_result,
        ):

            result = build_daily_report(
                [],
                [],
                self.make_as_of(),
            )

        self.assertIsNot(
            result,
            daily_result,
        )

    def test_non_list_fixtures_are_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                "not a list",
                [],
                self.make_as_of(),
            )

    def test_non_list_history_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                [],
                "not a list",
                self.make_as_of(),
            )

    def test_non_datetime_as_of_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                [],
                [],
                "not a datetime",
            )

    def test_naive_as_of_is_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
        )

        with self.assertRaises(ValueError):
            build_daily_report(
                [],
                [],
                as_of,
            )

    def test_build_daily_result_failure_is_propagated(self):
        with patch(
            "pipeline.daily_report.build_daily_result",
            side_effect=ValueError(
                "invalid daily result"
            ),
        ):

            with self.assertRaises(ValueError):
                build_daily_report(
                    [],
                    [],
                    self.make_as_of(),
                )


if __name__ == "__main__":
    unittest.main()
