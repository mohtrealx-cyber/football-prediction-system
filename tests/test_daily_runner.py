from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_runner import run_daily_pipeline


class DailyRunnerTests(unittest.TestCase):

    def make_fixtures(self):
        return [
            "fixture-1",
            "fixture-2",
        ]

    def make_history(self):
        return [
            "history-1",
            "history-2",
        ]

    def test_runner_calls_guarded_daily_portfolio(self):
        fixtures = self.make_fixtures()
        history = self.make_history()

        as_of = datetime(
            2026,
            9,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        )

        expected_result = [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

        with patch(
            "pipeline.daily_runner.build_guarded_daily_portfolio",
            return_value=expected_result,
        ) as portfolio_builder:

            result = run_daily_pipeline(
                fixtures,
                history,
                as_of,
            )

        portfolio_builder.assert_called_once_with(
            fixtures,
            history,
            as_of,
        )

        self.assertEqual(
            result,
            expected_result,
        )

    def test_runner_returns_portfolio_unchanged(self):
        fixtures = self.make_fixtures()
        history = self.make_history()

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        expected_result = {
            "result": "daily portfolio",
        }

        with patch(
            "pipeline.daily_runner.build_guarded_daily_portfolio",
            return_value=expected_result,
        ):

            result = run_daily_pipeline(
                fixtures,
                history,
                as_of,
            )

        self.assertIs(
            result,
            expected_result,
        )

    def test_guarded_pipeline_failure_is_propagated(self):
        fixtures = self.make_fixtures()
        history = self.make_history()

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with patch(
            "pipeline.daily_runner.build_guarded_daily_portfolio",
            side_effect=ValueError(
                "guarded pipeline failed"
            ),
        ):

            with self.assertRaises(ValueError):
                run_daily_pipeline(
                    fixtures,
                    history,
                    as_of,
                )

    def test_non_list_fixtures_are_rejected(self):
        history = self.make_history()

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            run_daily_pipeline(
                "not a list",
                history,
                as_of,
            )

    def test_non_list_history_is_rejected(self):
        fixtures = self.make_fixtures()

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(TypeError):
            run_daily_pipeline(
                fixtures,
                "not a list",
                as_of,
            )

    def test_non_datetime_as_of_is_rejected(self):
        fixtures = self.make_fixtures()
        history = self.make_history()

        with self.assertRaises(TypeError):
            run_daily_pipeline(
                fixtures,
                history,
                "2026-09-25T15:00:00Z",
            )

    def test_naive_as_of_is_rejected(self):
        fixtures = self.make_fixtures()
        history = self.make_history()

        as_of = datetime(
            2026,
            9,
            25,
            15,
            0,
        )

        with self.assertRaises(ValueError):
            run_daily_pipeline(
                fixtures,
                history,
                as_of,
            )


if __name__ == "__main__":
    unittest.main()
