from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_real_portfolio import build_daily_real_portfolio
from pipeline.daily_time_guard import filter_upcoming_fixtures


def build_guarded_daily_portfolio(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> Any:
    """
    Build a daily portfolio using only fixtures that have
    not kicked off yet.

    Processing order:

        fixtures + as_of
            ↓
        time guard
            ↓
        daily real portfolio
            ↓
        validated portfolio
    """
    if not isinstance(fixtures, list):
        raise TypeError(
            "fixtures must be a list"
        )

    if not isinstance(history, list):
        raise TypeError(
            "history must be a list"
        )

    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    upcoming_fixtures = filter_upcoming_fixtures(
        fixtures,
        as_of,
    )

    return build_daily_real_portfolio(
        upcoming_fixtures,
        history,
    )
