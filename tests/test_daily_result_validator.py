from __future__ import annotations

import unittest
from datetime import datetime, timezone

from pipeline.daily_result_validator import (
    validate_daily_result,
)


class DailyResultValidatorTests(unittest.TestCase):

    def make_valid_result(self):
        return {
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

    def test_valid_ready_result_passes(self):
        result = self.make_valid_result()

        self.assertTrue(
            validate_daily_result(
                result
            )
        )

    def test_valid_no_bet_result_passes(self):
        result = {
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
            validate_daily_result(
                result
            )
        )

    def test_missing_status_is_rejected(self):
        result = self.make_valid_result()
        del result["status"]

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_unknown_status_is_rejected(self):
        result = self.make_valid_result()
        result["status"] = "UNKNOWN"

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_missing_as_of_is_rejected(self):
        result = self.make_valid_result()
        del result["as_of"]

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_naive_as_of_is_rejected(self):
        result = self.make_valid_result()

        result["as_of"] = datetime(
            2026,
            9,
            25,
            15,
            0,
        )

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_missing_fixture_count_is_rejected(self):
        result = self.make_valid_result()
        del result["fixtures_received"]

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_negative_fixture_count_is_rejected(self):
        result = self.make_valid_result()
        result["fixtures_received"] = -1

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_missing_upcoming_count_is_rejected(self):
        result = self.make_valid_result()
        del result["upcoming_fixtures"]

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_negative_upcoming_count_is_rejected(self):
        result = self.make_valid_result()
        result["upcoming_fixtures"] = -1

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_upcoming_cannot_exceed_received(self):
        result = self.make_valid_result()

        result["fixtures_received"] = 3
        result["upcoming_fixtures"] = 5

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_missing_portfolio_is_rejected(self):
        result = self.make_valid_result()
        del result["portfolio"]

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_non_dictionary_result_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_daily_result(
                []
            )

    def test_boolean_fixture_count_is_rejected(self):
        result = self.make_valid_result()

        result["fixtures_received"] = True

        with self.assertRaises(TypeError):
            validate_daily_result(
                result
            )

    def test_boolean_upcoming_count_is_rejected(self):
        result = self.make_valid_result()

        result["upcoming_fixtures"] = False

        with self.assertRaises(TypeError):
            validate_daily_result(
                result
            )

    def test_no_bet_must_have_no_bet_portfolio(self):
        result = self.make_valid_result()

        result["status"] = "NO_BET"

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )

    def test_ready_must_not_have_no_bet_portfolio(self):
        result = self.make_valid_result()

        result["portfolio"] = {
            "status": "NO_BET",
            "reason": "insufficient qualifying selections",
            "tickets": [],
        }

        with self.assertRaises(ValueError):
            validate_daily_result(
                result
            )


if __name__ == "__main__":
    unittest.main()
