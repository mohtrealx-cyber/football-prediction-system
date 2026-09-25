from __future__ import annotations

from typing import List

from tickets.builder import Ticket
from portfolio.engine import build_market_portfolio as _build_market_portfolio


def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Public market-portfolio entry point.

    Delegates to the modern market-aware implementation in portfolio.engine.
    """
    return _build_market_portfolio(candidates)
