from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pipeline.daily_real_portfolio import (
    build_daily_real_portfolio,
)


class InsufficientDailyPortfolioTests(unittest.TestCase):

    def make_fixture(self):
        return object()

    def make_history(self):
        return object()

    def test_empty_portfolio_is_returned_without_validation(self):
        fixtures = [self.make_fixture()]
        history = [self.make_history()]

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=[],
        ) as candidate_builder, patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=[],
        ) as portfolio_builder, patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
        ) as validator:

            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        self.assertEqual(
            result,
            [],
        )

        candidate_builder.assert_called_once_with(
            fixtures,
            history,
        )

        portfolio_builder.assert_called_once_with(
            [],
        )

        validator.assert_not_called()

    def test_non_empty_portfolio_is_still_validated(self):
        fixtures = [self.make_fixture()]
        history = [self.make_history()]

        portfolio = [
            "ticket-1",
            "ticket-2",
            "ticket-3",
            "ticket-4",
        ]

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=["candidate"],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as validator:

            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        self.assertIs(
            result,
            portfolio,
        )

        validator.assert_called_once_with(
            portfolio,
        )

    def test_validation_failure_for_non_empty_portfolio_is_propagated(self):
        fixtures = [self.make_fixture()]
        history = [self.make_history()]

        invalid_portfolio = [
            "invalid-ticket",
        ]

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=["candidate"],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=invalid_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            side_effect=ValueError(
                "invalid portfolio"
            ),
        ):

            with self.assertRaises(ValueError):
                build_daily_real_portfolio(
                    fixtures,
                    history,
                )

    def test_empty_candidates_can_produce_no_portfolio(self):
        fixtures = [self.make_fixture()]
        history = [self.make_history()]

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=[],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=[],
        ):

            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        self.assertEqual(
            result,
            [],
        )

    def test_input_lists_are_not_modified(self):
        fixtures = [
            self.make_fixture(),
            self.make_fixture(),
        ]

        history = [
            self.make_history(),
        ]

        original_fixtures = list(fixtures)
        original_history = list(history)

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=[],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=[],
        ):

            build_daily_real_portfolio(
                fixtures,
                history,
            )

        self.assertEqual(
            fixtures,
            original_fixtures,
        )

        self.assertEqual(
            history,
            original_history,
        )


if __name__ == "__main__":
    unittest.main()
