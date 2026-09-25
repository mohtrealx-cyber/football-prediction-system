from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_result import build_daily_result


class DailyResultValidationIntegrationTests(unittest.TestCase):

    def make_as_of(self):
        return datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

    def test_final_daily_result_is_validated(self):
        portfolio = [
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
            return_value=portfolio,
        ), patch(
            "pipeline.daily_result.validate_daily_result",
            create=True,
        ) as validator:

            validator.return_value = True

            result = build_daily_result(
                ["fixture-1"],
                [],
                self.make_as_of(),
            )

        validator.assert_called_once_with(
            result
        )

        self.assertEqual(
            result["status"],
            "READY",
        )

    def test_validation_failure_is_propagated(self):
        portfolio = [
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
            return_value=portfolio,
        ), patch(
            "pipeline.daily_result.validate_daily_result",
            create=True,
        ) as validator:

            validator.side_effect = ValueError(
                "invalid daily result"
            )

            with self.assertRaises(ValueError):
                build_daily_result(
                    ["fixture-1"],
                    [],
                    self.make_as_of(),
                )

        validator.assert_called_once()

    def test_no_bet_result_is_also_validated(self):
        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=[],
        ), patch(
            "pipeline.daily_result.validate_daily_result",
            create=True,
        ) as validator:

            validator.return_value = True

            result = build_daily_result(
                [],
                [],
                self.make_as_of(),
            )

        validator.assert_called_once_with(
            result
        )

        self.assertEqual(
            result["status"],
            "NO_BET",
        )

    def test_validation_happens_after_result_is_constructed(self):
        portfolio = [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

        validation_snapshot = {}

        def fake_validator(result):
            validation_snapshot.update(result)
            return True

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=["fixture-1", "fixture-2"],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=portfolio,
        ), patch(
            "pipeline.daily_result.validate_daily_result",
            create=True,
            side_effect=fake_validator,
        ):

            result = build_daily_result(
                ["fixture-1", "fixture-2"],
                [],
                self.make_as_of(),
            )

        self.assertEqual(
            validation_snapshot,
            result,
        )

        self.assertEqual(
            validation_snapshot["fixtures_received"],
            2,
        )

        self.assertEqual(
            validation_snapshot["upcoming_fixtures"],
            2,
        )

    def test_portfolio_remains_unchanged_after_validation(self):
        portfolio = [
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
            return_value=portfolio,
        ), patch(
            "pipeline.daily_result.validate_daily_result",
            create=True,
            return_value=True,
        ):

            result = build_daily_result(
                ["fixture-1"],
                [],
                self.make_as_of(),
            )

        self.assertIs(
            result["portfolio"],
            portfolio,
        )


if __name__ == "__main__":
    unittest.main()
