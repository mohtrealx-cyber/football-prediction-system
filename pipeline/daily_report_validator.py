from __future__ import annotations

from datetime import datetime
from typing import Any

from pipeline.daily_result_validator import (
    validate_daily_result,
)


REPORT_TYPE = "DAILY_FOOTBALL_REPORT"


def validate_daily_report(
    report: dict,
) -> bool:
    """
    Validate a daily football report.

    The report must contain a fixed report_type and must also
    satisfy the underlying daily-result contract.
    """
    if not isinstance(report, dict):
        raise TypeError(
            "daily report must be a dictionary"
        )

    if "report_type" not in report:
        raise ValueError(
            "missing required report field: report_type"
        )

    if report["report_type"] != REPORT_TYPE:
        raise ValueError(
            "report_type must be DAILY_FOOTBALL_REPORT"
        )

    validate_daily_result(
        report
    )

    return True
