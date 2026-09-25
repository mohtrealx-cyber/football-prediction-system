from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_runner import run_daily_pipeline
from pipeline.daily_time_guard import filter_upcoming_fixtures


NO_BET_RESULT = {
    "status": "NO_BET",
    "reason": "insufficient qualifying selections",
    "tickets": [],
}


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def _build_no_bet_result() -> dict:
    return {
        "status": NO_BET_RESULT["status"],
        "reason": NO_BET_RESULT["reason"],
        "tickets": [],
    }


def build_daily_result(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> dict:
    """
    Build the daily pipeline result with execution metadata.

    An empty portfolio is converted into an explicit NO_BET
    result rather than being treated as a ticket or selection.

    The result contains:

        as_of
        fixtures_received
        upcoming_fixtures
        portfolio
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

    if portfolio == []:
        portfolio = _build_no_bet_result()

    return {
        "as_of": as_of,
        "fixtures_received": len(fixtures),
        "upcoming_fixtures": len(upcoming),
        "portfolio": portfolio,
    }
