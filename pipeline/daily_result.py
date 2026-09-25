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


def _is_no_bet_portfolio(portfolio: Any) -> bool:
    if portfolio == []:
        return True

    if isinstance(portfolio, dict):
        return portfolio.get("status") == "NO_BET"

    return False


def build_daily_result(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> dict:
    """
    Build the daily pipeline result with execution metadata
    and an explicit top-level execution status.

    Status values:

        READY
            A usable non-empty portfolio was produced.

        NO_BET
            No qualifying selections are available, or the
            portfolio explicitly reports a NO_BET state.

    The portfolio itself is preserved unchanged when it already
    contains an explicit NO_BET result.
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
        status = "NO_BET"
    elif _is_no_bet_portfolio(portfolio):
        status = "NO_BET"
    else:
        status = "READY"

    return {
        "status": status,
        "as_of": as_of,
        "fixtures_received": len(fixtures),
        "upcoming_fixtures": len(upcoming),
        "portfolio": portfolio,
    }
