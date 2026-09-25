from __future__ import annotations

from typing import Any

from data.historical_models import HistoricalMatch
from data.models import Match
from pipeline.daily_real import build_daily_real_candidates
from portfolio.market_portfolio import build_market_portfolio


def build_daily_real_portfolio(
    fixtures: list[Match],
    history: list[HistoricalMatch],
) -> Any:
    """
    Build the daily real-data candidate set and pass it into
    the existing market portfolio builder.

    The function intentionally does not duplicate portfolio logic.
    """
    if not isinstance(fixtures, list):
        raise TypeError("fixtures must be a list")

    if not isinstance(history, list):
        raise TypeError("history must be a list")

    candidates = build_daily_real_candidates(
        fixtures,
        history,
    )

    return build_market_portfolio(
        candidates,
    )
