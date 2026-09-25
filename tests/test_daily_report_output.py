import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_report_output import (
    build_daily_report_output,
)


class DailyReportOutputTests(unittest.TestCase):

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

    @patch("pipeline.daily_report_output.serialize_daily_report")
    @patch("pipeline.daily_report_output.build_daily_report")
    def test_build_daily_report_is_called(
        self,
        mock_build_daily_report,
        mock_serialize_daily_report,
    ):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        serialized = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": "2026-09-25T12:00:00+00:00",
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        mock_build_daily_report.return_value = report
        mock_serialize_daily_report.return_value = serialized

        result = build_daily_report_output(
            self.fixtures,
            self.history,
            self.as_of,
        )

        mock_build_daily_report.assert_called_once_with(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertEqual(
            result,
            serialized,
        )

    @patch("pipeline.daily_report_output.serialize_daily_report")
    @patch("pipeline.daily_report_output.build_daily_report")
    def test_serializer_receives_daily_report(
        self,
        mock_build_daily_report,
        mock_serialize_daily_report,
    ):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        serialized = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": "2026-09-25T12:00:00+00:00",
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        mock_build_daily_report.return_value = report
        mock_serialize_daily_report.return_value = serialized

        result = build_daily_report_output(
            self.fixtures,
            self.history,
            self.as_of,
        )

        mock_serialize_daily_report.assert_called_once_with(
            report,
        )

        self.assertEqual(
            result,
            serialized,
        )

    @patch("pipeline.daily_report_output.serialize_daily_report")
    @patch("pipeline.daily_report_output.build_daily_report")
    def test_serialized_result_is_returned_unchanged(
        self,
        mock_build_daily_report,
        mock_serialize_daily_report,
    ):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        serialized = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": "2026-09-25T12:00:00+00:00",
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        mock_build_daily_report.return_value = report
        mock_serialize_daily_report.return_value = serialized

        result = build_daily_report_output(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertIs(
            result,
            serialized,
        )

    @patch("pipeline.daily_report_output.serialize_daily_report")
    @patch("pipeline.daily_report_output.build_daily_report")
    def test_build_daily_report_failure_is_propagated(
        self,
        mock_build_daily_report,
        mock_serialize_daily_report,
    ):
        mock_build_daily_report.side_effect = ValueError(
            "daily report failed"
        )

        with self.assertRaises(ValueError):
            build_daily_report_output(
                self.fixtures,
                self.history,
                self.as_of,
            )

        mock_serialize_daily_report.assert_not_called()

    @patch("pipeline.daily_report_output.serialize_daily_report")
    @patch("pipeline.daily_report_output.build_daily_report")
    def test_serialization_failure_is_propagated(
        self,
        mock_build_daily_report,
        mock_serialize_daily_report,
    ):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        mock_build_daily_report.return_value = report
        mock_serialize_daily_report.side_effect = TypeError(
            "serialization failed"
        )

        with self.assertRaises(TypeError):
            build_daily_report_output(
                self.fixtures,
                self.history,
                self.as_of,
            )

    def test_non_list_fixtures_are_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                "not-a-list",
                self.history,
                self.as_of,
            )

    def test_non_list_history_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
                self.fixtures,
                "not-a-list",
                self.as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_report_output(
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
            build_daily_report_output(
                self.fixtures,
                self.history,
                naive_as_of,
            )


if __name__ == "__main__":
    unittest.main()
