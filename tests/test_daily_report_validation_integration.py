import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_report import build_daily_report


class DailyReportValidationIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.fixtures = []
        self.history = []
        self.as_of = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_validator_is_called_with_constructed_report(
        self,
        mock_build_result,
        mock_validate,
    ):
        daily_result = {
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

        mock_build_result.return_value = daily_result

        report = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        expected_report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            **daily_result,
        }

        mock_validate.assert_called_once_with(expected_report)
        self.assertEqual(report, expected_report)

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_validation_failure_is_propagated(
        self,
        mock_build_result,
        mock_validate,
    ):
        daily_result = {
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

        mock_build_result.return_value = daily_result
        mock_validate.side_effect = ValueError("invalid daily report")

        with self.assertRaises(ValueError):
            build_daily_report(
                self.fixtures,
                self.history,
                self.as_of,
            )

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_validation_happens_after_report_construction(
        self,
        mock_build_result,
        mock_validate,
    ):
        daily_result = {
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

        mock_build_result.return_value = daily_result

        call_order = []

        def build_result(*args, **kwargs):
            call_order.append("build")
            return daily_result

        def validate_report(report):
            call_order.append("validate")

        mock_build_result.side_effect = build_result
        mock_validate.side_effect = validate_report

        build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertEqual(call_order, ["build", "validate"])

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_report_data_is_preserved(
        self,
        mock_build_result,
        mock_validate,
    ):
        daily_result = {
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 5,
            "upcoming_fixtures": 3,
            "portfolio": [
                "ticket-data"
            ],
        }

        mock_build_result.return_value = daily_result

        report = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        self.assertEqual(
            report["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )
        self.assertEqual(report["status"], "READY")
        self.assertEqual(report["as_of"], self.as_of)
        self.assertEqual(report["fixtures_received"], 5)
        self.assertEqual(report["upcoming_fixtures"], 3)
        self.assertEqual(report["portfolio"], ["ticket-data"])

        mock_validate.assert_called_once_with(report)


if __name__ == "__main__":
    unittest.main()
