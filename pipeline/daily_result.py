from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_runner import run_daily_pipeline
from pipeline.daily_time_guard import filter_upcoming_fixtures


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def build_daily_result(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> dict:
    """
    Build the daily pipeline result with execution metadata.

    The result contains:

        as_of
        fixtures_received
        upcoming_fixtures
        portfolio

    The portfolio itself is produced by the existing guarded
    daily runner and is returned unchanged.
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

    upcoming = filter_upcoming_fixtures(
        fixtures,
        as_of,
    )

    portfolio = run_daily_pipeline(
        fixtures,
        history,
        as_of,
    )

    return {
        "as_of": as_of,
        "fixtures_received": len(fixtures),
        "upcoming_fixtures": len(upcoming),
        "portfolio": portfolio,
    }
