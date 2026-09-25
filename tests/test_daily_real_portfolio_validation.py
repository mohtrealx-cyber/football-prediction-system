from __future__ import annotations

import unittest
from unittest.mock import patch

from pipeline.daily_real_portfolio import (
    build_daily_real_portfolio,
)


class DailyRealPortfolioValidationTests(unittest.TestCase):

    def make_non_empty_portfolio(self):
        return [
            "SAFE",
            "BALANCED",
            "AGGRESSIVE",
            "VALUE",
        ]

    def test_validator_is_called_on_built_portfolio(self):
        expected_portfolio = (
            self.make_non_empty_portfolio()
        )

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=["candidate"],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as mock_validator:

            portfolio = (
                build_daily_real_portfolio(
                    [],
                    [],
                )
            )

        mock_validator.assert_called_once_with(
            portfolio
        )

        self.assertIs(
            portfolio,
            expected_portfolio,
        )

    def test_validator_failure_is_propagated(self):
        expected_portfolio = (
            self.make_non_empty_portfolio()
        )

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=["candidate"],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            side_effect=ValueError(
                "invalid daily portfolio"
            ),
        ) as mock_validator:

            with self.assertRaises(ValueError):
                build_daily_real_portfolio(
                    [],
                    [],
                )

        mock_validator.assert_called_once_with(
            expected_portfolio
        )

    def test_validated_portfolio_is_returned_unchanged(self):
        expected_portfolio = (
            self.make_non_empty_portfolio()
        )

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=["candidate"],
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as mock_validator:

            portfolio = (
                build_daily_real_portfolio(
                    [],
                    [],
                )
            )

        mock_validator.assert_called_once_with(
            expected_portfolio
        )

        self.assertIs(
            portfolio,
            expected_portfolio
        )


if __name__ == "__main__":
    unittest.main()
