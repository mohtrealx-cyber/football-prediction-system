from __future__ import annotations

import unittest
from datetime import datetime, timezone

from pipeline.daily_report_validator import (
    validate_daily_report,
)


class DailyReportValidatorTests(unittest.TestCase):

    def make_ready_report(self):
        return {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "READY",
            "as_of": datetime(
                2026,
                9,
                25,
                15,
                0,
                tzinfo=timezone.utc,
            ),
            "fixtures_received": 10,
            "upcoming_fixtures": 7,
            "portfolio": [
                "SAFE",
                "BALANCED",
                "AGGRESSIVE",
                "VALUE",
            ],
        }

    def test_valid_ready_report_passes(self):
        self.assertTrue(
            validate_daily_report(
                self.make_ready_report()
            )
        )

    def test_valid_no_bet_report_passes(self):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": datetime(
                2026,
                9,
                25,
                15,
                0,
                tzinfo=timezone.utc,
            ),
            "fixtures_received": 5,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        self.assertTrue(
            validate_daily_report(
                report
            )
        )

    def test_non_dictionary_report_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_daily_report(
                []
            )

    def test_missing_report_type_is_rejected(self):
        report = self.make_ready_report()

        del report["report_type"]

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_invalid_report_type_is_rejected(self):
        report = self.make_ready_report()

        report["report_type"] = "OTHER_REPORT"

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_missing_daily_result_field_is_rejected(self):
        report = self.make_ready_report()

        del report["status"]

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_naive_as_of_is_rejected(self):
        report = self.make_ready_report()

        report["as_of"] = datetime(
            2026,
            9,
            25,
            15,
            0,
        )

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_negative_fixture_count_is_rejected(self):
        report = self.make_ready_report()

        report["fixtures_received"] = -1

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_upcoming_cannot_exceed_received(self):
        report = self.make_ready_report()

        report["fixtures_received"] = 2
        report["upcoming_fixtures"] = 3

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_invalid_status_is_rejected(self):
        report = self.make_ready_report()

        report["status"] = "UNKNOWN"

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_ready_cannot_contain_no_bet_portfolio(self):
        report = self.make_ready_report()

        report["portfolio"] = {
            "status": "NO_BET",
            "reason": "insufficient qualifying selections",
            "tickets": [],
        }

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )

    def test_no_bet_cannot_contain_ready_portfolio(self):
        report = self.make_ready_report()

        report["status"] = "NO_BET"

        with self.assertRaises(ValueError):
            validate_daily_report(
                report
            )


if __name__ == "__main__":
    unittest.main()
