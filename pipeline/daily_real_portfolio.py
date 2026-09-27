from __future__ import annotations

from typing import Any

from data.historical_models import HistoricalMatch
from data.models import Match
from pipeline.daily_real import build_daily_real_candidates
from portfolio.daily_validator import validate_daily_portfolio
from portfolio.market_portfolio import build_market_portfolio


def build_daily_real_portfolio(
    fixtures: list[Match],
    history: list[HistoricalMatch],
) -> Any:
    if not isinstance(fixtures, list):
        raise TypeError(
            "fixtures must be a list"
        )

    if not isinstance(history, list):
        raise TypeError(
            "history must be a list"
        )

    candidates = build_daily_real_candidates(
        fixtures,
        history,
    )

    # Only qualified candidates are eligible
    # for portfolio construction.
    qualified_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("qualified") is True
    ]

    portfolio = build_market_portfolio(
        qualified_candidates,
    )

    # An empty portfolio is an intentional no-bet state.
    # It must reach daily_result.py so it can be converted
    # into the explicit NO_BET result.
    if portfolio == []:
        return portfolio

    validate_daily_portfolio(
        portfolio
    )

    return portfolio
