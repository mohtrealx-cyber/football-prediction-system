from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_result import build_daily_result


class DailyResultTests(unittest.TestCase):

    def test_result_contains_execution_metadata(self):
        fixtures = [
            "fixture-1",
            "fixture-2",
            "fixture-3",
        ]

        history = [
            "history-1",
        ]

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        expected_portfolio = [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[
                "fixture-1",
                "fixture-3",
            ],
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=expected_portfolio,
        ):

            result = build_daily_result(
                fixtures,
                history,
                as_of,
            )

        self.assertEqual(
            result["as_of"],
            as_of,
        )

        self.assertEqual(
            result["fixtures_received"],
            3,
        )

        self.assertEqual(
            result["upcoming_fixtures"],
            2,
        )

        self.assertIs(
            result["portfolio"],
            expected_portfolio,
        )

    def test_portfolio_is_preserved_unchanged(self):
        fixtures = [
            "fixture-1",
        ]

        history = [
            "history-1",
        ]

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        expected_portfolio = {
            "portfolio": "value",
        }

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=fixtures,
        ), patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=expected_portfolio,
        ):

            result = build_daily_result(
                fixtures,
                history,
                as_of,
            )

        self.assertIs(
            result["portfolio"],
            expected_portfolio,
        )

    def test_empty_fixture_list_is_supported(self):
        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        expected_portfolio = []

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

        self.assertIs(
            result["portfolio"],
            expected_portfolio,
        )

    def test_filter_is_called_with_original_fixtures(self):
        fixtures = [
            "fixture-1",
            "fixture-2",
        ]

        history = []

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with patch(
            "pipeline.daily_result.filter_upcoming_fixtures",
            return_value=[],
        ) as time_guard, patch(
            "pipeline.daily_result.run_daily_pipeline",
            return_value=[],
        ):

            build_daily_result(
                fixtures,
                history,
                as_of,
            )

        time_guard.assert_called_once_with(
            fixtures,
            as_of,
        )

    def test_non_list_fixtures_are_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            build_daily_result(
                "not a list",
                [],
                as_of,
            )

    def test_non_list_history_is_rejected(self):
        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            build_daily_result(
                [],
                "not a list",
                as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        with self.assertRaises(TypeError):
            build_daily_result(
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
            build_daily_result(
                [],
                [],
                as_of,
            )


if __name__ == "__main__":
    unittest.main()
