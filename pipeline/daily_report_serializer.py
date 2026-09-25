from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from typing import Any

from pipeline.daily_report_validator import validate_daily_report


def _serialize_value(value: Any) -> Any:
    """
    Convert supported Python values into JSON-compatible values.

    Supported:
    - None
    - bool
    - int
    - float
    - str
    - datetime
    - date
    - dataclass instances
    - dictionaries
    - lists
    - tuples
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _serialize_value(
                getattr(value, field.name)
            )
            for field in fields(value)
        }

    if isinstance(value, dict):
        serialized = {}

        for key, item in value.items():
            if not isinstance(
                key,
                (str, int, float, bool),
            ) and key is not None:
                raise TypeError(
                    "dictionary keys must be JSON-compatible"
                )

            serialized_key = (
                str(key)
                if not isinstance(key, str)
                else key
            )

            serialized[serialized_key] = _serialize_value(
                item
            )

        return serialized

    if isinstance(value, (list, tuple)):
        return [
            _serialize_value(item)
            for item in value
        ]

    raise TypeError(
        f"unsupported value type: {type(value).__name__}"
    )


def serialize_daily_report(report: dict) -> dict:
    """
    Validate and convert a daily football report into a
    JSON-compatible dictionary.

    The original report is never modified.
    """

    if not isinstance(report, dict):
        raise TypeError(
            "daily report must be a dictionary"
        )

    validate_daily_report(report)

    serialized = _serialize_value(report)

    if not isinstance(serialized, dict):
        raise TypeError(
            "serialized daily report must be a dictionary"
        )

    return serialized
