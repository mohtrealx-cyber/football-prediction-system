import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_report import build_daily_report


class DailyReportSerializationTests(unittest.TestCase):

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

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_ready_report_is_json_serializable(
        self,
        mock_build_result,
        mock_validate,
    ):
        mock_build_result.return_value = {
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 5,
            "upcoming_fixtures": 3,
            "portfolio": [
                {
                    "ticket": "SAFE",
                    "stake_percent": 40.0,
                    "matches": [
                        {
                            "match_id": "m1",
                            "selection": "HOME",
                            "odds": 1.80,
                        }
                    ],
                }
            ],
        }

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        serialized = json.dumps(
            result,
            default=str,
        )

        self.assertIsInstance(
            serialized,
            str,
        )

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_no_bet_report_is_json_serializable(
        self,
        mock_build_result,
        mock_validate,
    ):
        mock_build_result.return_value = {
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

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        serialized = json.dumps(
            result,
            default=str,
        )

        self.assertIsInstance(
            serialized,
            str,
        )

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_report_round_trip_preserves_core_fields(
        self,
        mock_build_result,
        mock_validate,
    ):
        mock_build_result.return_value = {
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

        result = build_daily_report(
            self.fixtures,
            self.history,
            self.as_of,
        )

        serialized = json.dumps(
            result,
            default=str,
        )

        restored = json.loads(
            serialized,
        )

        self.assertEqual(
            restored["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )
        self.assertEqual(
            restored["status"],
            "NO_BET",
        )
        self.assertEqual(
            restored["fixtures_received"],
            10,
        )
        self.assertEqual(
            restored["upcoming_fixtures"],
            0,
        )

    @patch("pipeline.daily_report.validate_daily_report")
    @patch("pipeline.daily_report.build_daily_result")
    def test_report_validation_occurs_before_serialization(
        self,
        mock_build_result,
        mock_validate,
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

        mock_validate.assert_called_once_with(
            result
        )

        json.dumps(
            result,
            default=str,
        )

        self.assertEqual(
            mock_validate.call_count,
            1,
        )


if __name__ == "__main__":
    unittest.main()
