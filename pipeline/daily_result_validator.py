from __future__ import annotations

from datetime import datetime
from typing import Any


REQUIRED_FIELDS = (
    "status",
    "as_of",
    "fixtures_received",
    "upcoming_fixtures",
    "portfolio",
)

ALLOWED_STATUSES = {
    "READY",
    "NO_BET",
}


def _validate_required_fields(result: dict) -> None:
    missing = [
        field
        for field in REQUIRED_FIELDS
        if field not in result
    ]

    if missing:
        raise ValueError(
            "missing required daily result field(s): "
            + ", ".join(missing)
        )


def _validate_status(status: Any) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "status must be READY or NO_BET"
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


def _validate_count(
    value: Any,
    field_name: str,
) -> None:
    if isinstance(value, bool):
        raise TypeError(
            f"{field_name} must be an integer"
        )

    if not isinstance(value, int):
        raise TypeError(
            f"{field_name} must be an integer"
        )

    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative"
        )


def _validate_counts(
    fixtures_received: int,
    upcoming_fixtures: int,
) -> None:
    _validate_count(
        fixtures_received,
        "fixtures_received",
    )

    _validate_count(
        upcoming_fixtures,
        "upcoming_fixtures",
    )

    if upcoming_fixtures > fixtures_received:
        raise ValueError(
            "upcoming_fixtures cannot exceed "
            "fixtures_received"
        )


def _validate_portfolio(
    status: str,
    portfolio: Any,
) -> None:
    if status == "NO_BET":
        if not isinstance(portfolio, dict):
            raise ValueError(
                "NO_BET portfolio must be a dictionary"
            )

        if portfolio.get("status") != "NO_BET":
            raise ValueError(
                "NO_BET result must contain a "
                "NO_BET portfolio"
            )

        return

    if isinstance(portfolio, dict):
        if portfolio.get("status") == "NO_BET":
            raise ValueError(
                "READY result cannot contain a "
                "NO_BET portfolio"
            )

        return

    if isinstance(portfolio, list):
        if not portfolio:
            raise ValueError(
                "READY result cannot contain an empty "
                "portfolio"
            )

        return

    if portfolio is None:
        raise ValueError(
            "READY result must contain a portfolio"
        )


def validate_daily_result(
    result: dict,
) -> bool:
    """
    Validate the structure and consistency of a daily
    pipeline result.

    Required fields:

        status
        as_of
        fixtures_received
        upcoming_fixtures
        portfolio

    Supported statuses:

        READY
        NO_BET
    """
    if not isinstance(result, dict):
        raise TypeError(
            "daily result must be a dictionary"
        )

    _validate_required_fields(
        result
    )

    status = result["status"]

    _validate_status(
        status
    )

    _validate_as_of(
        result["as_of"]
    )

    _validate_counts(
        result["fixtures_received"],
        result["upcoming_fixtures"],
    )

    _validate_portfolio(
        status,
        result["portfolio"],
    )

    return True
