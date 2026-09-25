import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_report import (
    REPORT_TYPE,
    build_daily_report,
)


class DailyReportContractTests(unittest.TestCase):

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
    @patch("pipeline.daily_report.validate_daily_report")
    def test_report_type_is_fixed(
        self,
        mock_validate,
        mock_build_result,
    ):
        mock_build_result.return_value = {
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
            REPORT_TYPE,
            "DAILY_FOOTBALL_REPORT",
        )

    @patch("pipeline.daily_report.build_daily_result")
    @patch("pipeline.daily_report.validate_daily_report")
    def test_report_contains_all_daily_result_fields(
        self,
        mock_validate,
        mock_build_result,
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

        mock_build_result.return_value = daily_result

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        for field in daily_result:
            self.assertIn(
                field,
                result,
            )

        self.assertIn(
            "report_type",
            result,
        )

    @patch("pipeline.daily_report.build_daily_result")
    @patch("pipeline.daily_report.validate_daily_report")
    def test_report_type_does_not_overwrite_daily_result_data(
        self,
        mock_validate,
        mock_build_result,
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

        mock_build_result.return_value = daily_result

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
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
            5,
        )
        self.assertEqual(
            result["upcoming_fixtures"],
            3,
        )
        self.assertEqual(
            result["portfolio"],
            [
                "ticket-data",
            ],
        )

    @patch("pipeline.daily_report.build_daily_result")
    @patch("pipeline.daily_report.validate_daily_report")
    def test_validator_receives_complete_report(
        self,
        mock_validate,
        mock_build_result,
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

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        mock_validate.assert_called_once_with(
            result
        )

        self.assertEqual(
            mock_validate.call_count,
            1,
        )

    @patch("pipeline.daily_report.build_daily_result")
    @patch("pipeline.daily_report.validate_daily_report")
    def test_report_is_a_new_dictionary(
        self,
        mock_validate,
        mock_build_result,
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
    @patch("pipeline.daily_report.validate_daily_report")
    def test_inputs_are_passed_to_daily_result_unchanged(
        self,
        mock_validate,
        mock_build_result,
    ):
        mock_build_result.return_value = {
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

        build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        mock_build_result.assert_called_once_with(
            self.fixtures,
            self.history,
            self.as_of,
        )


if __name__ == "__main__":
    unittest.main()
