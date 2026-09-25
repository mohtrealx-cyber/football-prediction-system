from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_report import build_daily_report
from pipeline.daily_report_serializer import serialize_daily_report


def _validate_as_of(as_of: Any) -> None:
    if not isinstance(as_of, datetime):
        raise TypeError(
            "as_of must be a datetime"
        )

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError(
            "as_of must be timezone-aware"
        )


def build_daily_report_output(
    fixtures: list,
    history: list,
    as_of: datetime,
) -> dict:
    """
    Build the daily football report and convert it into a
    JSON-compatible dictionary.

    Processing order:
        1. Validate inputs.
        2. Build the validated daily report.
        3. Serialize the report.
        4. Return the serialized output.

    The original inputs and report are not modified.
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

    report = build_daily_report(
        fixtures,
        history,
        as_of,
    )

    serialized_report = serialize_daily_report(
        report
    )

    return serialized_report
