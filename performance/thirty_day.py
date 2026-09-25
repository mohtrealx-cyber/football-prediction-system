from typing import Any

from performance.period import calculate_period_performance


TARGET_DAYS = 30


def calculate_30_day_performance(
    daily_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(daily_results, list):
        raise TypeError("daily_results must be a list")

    if len(daily_results) > TARGET_DAYS:
        raise ValueError("daily_results cannot contain more than 30 days")

    period_performance = calculate_period_performance(daily_results)

    elapsed_days = len(daily_results)
    days_remaining = TARGET_DAYS - elapsed_days
    complete = elapsed_days == TARGET_DAYS

    return {
        "target_days": TARGET_DAYS,
        "elapsed_days": elapsed_days,
        "days_remaining": days_remaining,
        "complete": complete,
        "total_tickets": period_performance["total_tickets"],
        "wins": period_performance["wins"],
        "losses": period_performance["losses"],
        "total_stake": period_performance["total_stake"],
        "total_return": period_performance["total_return"],
        "total_profit_loss": period_performance["total_profit_loss"],
        "roi": period_performance["roi"],
    }
