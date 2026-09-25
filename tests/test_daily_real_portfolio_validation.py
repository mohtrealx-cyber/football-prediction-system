import unittest
from unittest.mock import patch

import pipeline.daily_real_portfolio as daily_real_portfolio


class DailyRealPortfolioValidationTests(unittest.TestCase):

    def test_validator_is_called_on_built_portfolio(self):
        with patch.object(
            daily_real_portfolio,
            "validate_daily_portfolio",
            create=True,
        ) as mock_validator:

            mock_validator.return_value = True

            portfolio = (
                daily_real_portfolio.build_daily_real_portfolio(
                    [],
                    [],
                )
            )

            mock_validator.assert_called_once_with(
                portfolio
            )

    def test_validator_failure_is_propagated(self):
        with patch.object(
            daily_real_portfolio,
            "validate_daily_portfolio",
            create=True,
        ) as mock_validator:

            mock_validator.side_effect = ValueError(
                "invalid daily portfolio"
            )

            with self.assertRaises(ValueError):
                daily_real_portfolio.build_daily_real_portfolio(
                    [],
                    [],
                )

            mock_validator.assert_called_once()

    def test_validated_portfolio_is_returned_unchanged(self):
        with patch.object(
            daily_real_portfolio,
            "validate_daily_portfolio",
            create=True,
        ) as mock_validator:

            mock_validator.return_value = True

            portfolio = (
                daily_real_portfolio.build_daily_real_portfolio(
                    [],
                    [],
                )
            )

            self.assertIsNotNone(
                portfolio
            )

            mock_validator.assert_called_once_with(
                portfolio
            )


if __name__ == "__main__":
    unittest.main()
