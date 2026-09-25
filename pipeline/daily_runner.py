from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.guarded_daily_portfolio import (
    build_guarded_daily_portfolio,
)


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def run_daily_pipeline(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> Any:
    """
    Single public entry point for the daily prediction pipeline.

    The runner delegates portfolio construction to the guarded
    daily portfolio pipeline and returns its result unchanged.
    """
    if not isinstance(fixtures, list):
        raise TypeError(
            "fixtures must be a list"
        )

    if not isinstance(history, list):
        raise TypeError(
            "history must be a list"
        )

    _validate_as_of(as_of)

    return build_guarded_daily_portfolio(
        fixtures,
        history,
        as_of,
    )
