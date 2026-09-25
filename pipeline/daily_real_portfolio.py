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
        raise TypeError("fixtures must be a list")

    if not isinstance(history, list):
        raise TypeError("history must be a list")

    candidates = build_daily_real_candidates(
        fixtures,
        history,
    )

    portfolio = build_market_portfolio(
        candidates,
    )

    validate_daily_portfolio(
        portfolio
    )

    return portfolio
