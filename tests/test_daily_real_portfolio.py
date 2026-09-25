from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from data.historical_models import HistoricalMatch
from data.models import Match
from portfolio.market_portfolio import build_market_portfolio
from pipeline.daily_real_portfolio import build_daily_real_portfolio


class DailyRealPortfolioTests(unittest.TestCase):
    def make_fixture(
        self,
        match_id: str = "m1",
        home_team: str = "Alpha",
        away_team: str = "Beta",
        hour: int = 15,
    ) -> Match:
        return Match(
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            league="Test League",
            kickoff=datetime(
                2026,
                9,
                25,
                hour,
                0,
                tzinfo=timezone.utc,
            ),
            status="scheduled",
            odds={
                "home_win": 1.80,
                "draw": 3.50,
                "away_win": 4.50,
            },
        )

    def make_history(self) -> list[HistoricalMatch]:
        return [
            HistoricalMatch(
                match_id="h1",
                home_team="Alpha",
                away_team="Beta",
                league="Test League",
                kickoff=datetime(
                    2026,
                    9,
                    20,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                home_goals=2,
                away_goals=0,
                odds={
                    "home_win": 1.90,
                    "draw": 3.40,
                    "away_win": 4.20,
                },
            )
        ]

    def make_candidates(self) -> list[dict]:
        return [
            {
                "match_id": f"m{i}",
                "home_team": f"Home{i}",
                "away_team": f"Away{i}",
                "league": "Test League",
                "market": "home_win",
                "selection": "HOME",
                "qualified": True,
                "model_probability": 0.70,
                "odds": {
                    "home_win": 1.80,
                },
                "selected_odds": 1.80,
                "implied_probability": 1 / 1.80,
                "expected_value": 0.26,
                "value_edge": 14.44,
                "score": 58.0,
            }
            for i in range(1, 13)
        ]

    def test_returns_portfolio(self):
        fixtures = [self.make_fixture()]
        history = self.make_history()

        expected_portfolio = {
            "ticket_count": 4,
            "tickets": [],
            "total_stake_percentage": 100.0,
        }

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=self.make_candidates(),
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as validator:
            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        validator.assert_called_once_with(
            expected_portfolio
        )

        self.assertEqual(
            result,
            expected_portfolio,
        )

    def test_daily_candidates_are_passed_to_portfolio_builder(self):
        fixtures = [self.make_fixture()]
        history = self.make_history()

        candidates = self.make_candidates()

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=candidates,
        ) as candidate_builder, patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value={"ticket_count": 4},
        ) as portfolio_builder, patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as validator:
            build_daily_real_portfolio(
                fixtures,
                history,
            )

        candidate_builder.assert_called_once_with(
            fixtures,
            history,
        )

        portfolio_builder.assert_called_once_with(
            candidates,
        )

        validator.assert_called_once_with(
            {"ticket_count": 4}
        )

    def test_fixture_and_history_are_not_modified(self):
        fixtures = [self.make_fixture()]
        history = self.make_history()

        original_fixtures = list(fixtures)
        original_history = list(history)

        expected_portfolio = {
            "ticket_count": 4
        }

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=self.make_candidates(),
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
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

    def test_empty_candidates_are_passed_to_portfolio_builder(self):
        fixtures = [self.make_fixture()]
        history = self.make_history()

        expected_portfolio = {
            "ticket_count": 0
        }

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=[],
        ) as candidate_builder, patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ) as portfolio_builder, patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as validator:
            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        candidate_builder.assert_called_once_with(
            fixtures,
            history,
        )

        portfolio_builder.assert_called_once_with(
            [],
        )

        validator.assert_called_once_with(
            expected_portfolio
        )

        self.assertEqual(
            result["ticket_count"],
            0,
        )

    def test_empty_fixture_list_is_supported(self):
        fixtures = []
        history = self.make_history()

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=[],
        ) as candidate_builder, patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=[],
        ) as portfolio_builder, patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
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
            [],
            history,
        )

        portfolio_builder.assert_called_once_with(
            [],
        )

        validator.assert_called_once_with(
            []
        )

    def test_non_list_fixtures_are_rejected(self):
        history = self.make_history()

        with self.assertRaises(TypeError):
            build_daily_real_portfolio(
                "not a list",
                history,
            )

    def test_non_list_history_is_rejected(self):
        fixtures = [self.make_fixture()]

        with self.assertRaises(TypeError):
            build_daily_real_portfolio(
                fixtures,
                "not a list",
            )

    def test_four_ticket_portfolio_is_preserved(self):
        fixtures = [self.make_fixture()]
        history = self.make_history()

        expected_portfolio = {
            "ticket_count": 4,
            "total_stake_percentage": 100.0,
            "tickets": [
                {
                    "name": "SAFE",
                    "stake_percent": 40.0,
                },
                {
                    "name": "BALANCED",
                    "stake_percent": 30.0,
                },
                {
                    "name": "AGGRESSIVE",
                    "stake_percent": 20.0,
                },
                {
                    "name": "VALUE",
                    "stake_percent": 10.0,
                },
            ],
        }

        with patch(
            "pipeline.daily_real_portfolio.build_daily_real_candidates",
            return_value=self.make_candidates(),
        ), patch(
            "pipeline.daily_real_portfolio.build_market_portfolio",
            return_value=expected_portfolio,
        ), patch(
            "pipeline.daily_real_portfolio.validate_daily_portfolio",
            return_value=True,
        ) as validator:
            result = build_daily_real_portfolio(
                fixtures,
                history,
            )

        validator.assert_called_once_with(
            expected_portfolio
        )

        self.assertEqual(
            result,
            expected_portfolio,
        )

        self.assertEqual(
            result["ticket_count"],
            4,
        )

        self.assertEqual(
            result["total_stake_percentage"],
            100.0,
        )

        self.assertEqual(
            len(result["tickets"]),
            4,
        )

    def test_existing_portfolio_builder_interface_remains_available(self):
        candidates = self.make_candidates()

        # This test documents that V4.2 connects to the existing
        # market portfolio layer instead of creating a second
        # portfolio implementation.
        self.assertTrue(
            callable(build_market_portfolio)
        )

        self.assertIsInstance(
            candidates,
            list,
        )


if __name__ == "__main__":
    unittest.main()
