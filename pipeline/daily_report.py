from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_result import build_daily_result


REPORT_TYPE = "DAILY_FOOTBALL_REPORT"


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def build_daily_report(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> dict:
    """
    Convert a validated daily result into a stable reporting
    payload.

    The underlying daily result is preserved, while the report
    receives a fixed report_type field.
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

    daily_result = build_daily_result(
        fixtures,
        history,
        as_of,
    )

    return {
        "report_type": REPORT_TYPE,
        **daily_result,
    }
