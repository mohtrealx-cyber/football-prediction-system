from datetime import datetime, timezone
from unittest.mock import patch

import unittest

from pipeline.daily_report import build_daily_report


class DailyReportTests(unittest.TestCase):

    def setUp(self):
        self.fixtures = []
        self.history = []
        self.as_of = datetime(
            2026,
            9,
            25,
            12,
            0,
            tzinfo=timezone.utc,
        )

    @patch("pipeline.daily_report.build_daily_result")
    def test_ready_result_is_converted_to_report(
        self,
        mock_build_daily_result,
    ):
        daily_result = {
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 10,
            "upcoming_fixtures": 7,
            "portfolio": [
                "ticket-data",
            ],
        }

        mock_build_daily_result.return_value = daily_result

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
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
            self.as_of,
        )
        self.assertEqual(
            result["fixtures_received"],
            10,
        )
        self.assertEqual(
            result["upcoming_fixtures"],
            7,
        )
        self.assertEqual(
            result["portfolio"],
            ["ticket-data"],
        )

    @patch("pipeline.daily_report.build_daily_result")
    def test_no_bet_result_is_preserved(
        self,
        mock_build_daily_result,
    ):
        daily_result = {
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 10,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        mock_build_daily_result.return_value = daily_result

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
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
            result["as_of"],
            self.as_of,
        )
        self.assertEqual(
            result["fixtures_received"],
            10,
        )
        self.assertEqual(
            result["upcoming_fixtures"],
            0,
        )
        self.assertEqual(
            result["portfolio"],
            {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        )

    @patch("pipeline.daily_report.build_daily_result")
    def test_daily_result_is_not_modified(
        self,
        mock_build_daily_result,
    ):
        daily_result = {
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 5,
            "upcoming_fixtures": 3,
            "portfolio": [
                "ticket-data",
            ],
        }

        original_daily_result = {
            key: value.copy() if isinstance(value, dict) else list(value)
            if isinstance(value, list)
            else value
            for key, value in daily_result.items()
        }

        mock_build_daily_result.return_value = daily_result

        build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertEqual(
            daily_result,
            original_daily_result,
        )

    @patch("pipeline.daily_report.build_daily_result")
    def test_report_returns_new_dictionary(
        self,
        mock_build_daily_result,
    ):
        daily_result = {
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 5,
            "upcoming_fixtures": 3,
            "portfolio": [
                "ticket-data",
            ],
        }

        mock_build_daily_result.return_value = daily_result

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertIsInstance(
            result,
            dict,
        )
        self.assertIsNot(
            result,
            daily_result,
        )

    @patch("pipeline.daily_report.build_daily_result")
    def test_build_daily_result_failure_is_propagated(
        self,
        mock_build_daily_result,
    ):
        mock_build_daily_result.side_effect = ValueError(
            "daily result failed"
        )

        with self.assertRaises(ValueError):
            build_daily_report(
                self.fixtures,
                self.history,
                self.as_of,
            )

    def test_non_list_fixtures_are_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                "not-a-list",
                self.history,
                self.as_of,
            )

    def test_non_list_history_are_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                self.fixtures,
                "not-a-list",
                self.as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report(
                self.fixtures,
                self.history,
                "not-a-datetime",
            )

    def test_naive_as_of_is_rejected(self):
        naive_as_of = datetime(
            2026,
            9,
            25,
            12,
            0,
        )

        with self.assertRaises(ValueError):
            build_daily_report(
                self.fixtures,
                self.history,
                naive_as_of,
            )


if __name__ == "__main__":
    unittest.main()
