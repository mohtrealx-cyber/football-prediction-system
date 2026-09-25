from typing import Any

from performance.period import calculate_period_performance


REQUIRED_FIELDS = (
    "date",
    "total_tickets",
    "wins",
    "losses",
    "total_stake",
    "total_return",
    "total_profit_loss",
)


def build_performance_history(
    daily_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(daily_results, list):
        raise TypeError("daily_results must be a list")

    history = []
    seen_dates = set()

    cumulative_tickets = 0
    cumulative_wins = 0
    cumulative_losses = 0
    cumulative_stake = 0.0
    cumulative_return = 0.0
    cumulative_profit_loss = 0.0

    for day_number, daily_result in enumerate(daily_results, start=1):
        if not isinstance(daily_result, dict):
            raise ValueError("each daily result must be a dictionary")

        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in daily_result
        ]

        if missing_fields:
            raise ValueError(
                f"daily result is missing required fields: {missing_fields}"
            )

        date = daily_result["date"]

        if date in seen_dates:
            raise ValueError(f"duplicate date: {date}")

        seen_dates.add(date)

        try:
            total_tickets = int(daily_result["total_tickets"])
            wins = int(daily_result["wins"])
            losses = int(daily_result["losses"])
            total_stake = float(daily_result["total_stake"])
            total_return = float(daily_result["total_return"])
            total_profit_loss = float(
                daily_result["total_profit_loss"]
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "daily performance values must be numeric"
            ) from exc

        if total_tickets < 0:
            raise ValueError("total_tickets cannot be negative")

        if wins < 0 or losses < 0:
            raise ValueError("wins and losses cannot be negative")

        if total_stake < 0:
            raise ValueError("total_stake cannot be negative")

        if total_return < 0:
            raise ValueError("total_return cannot be negative")

        cumulative_tickets += total_tickets
        cumulative_wins += wins
        cumulative_losses += losses
        cumulative_stake += total_stake
        cumulative_return += total_return
        cumulative_profit_loss += total_profit_loss

        cumulative_roi = (
            cumulative_profit_loss / cumulative_stake
            if cumulative_stake > 0
            else 0.0
        )

        history.append(
            {
                "day": day_number,
                "date": date,
                "cumulative_tickets": cumulative_tickets,
                "cumulative_wins": cumulative_wins,
                "cumulative_losses": cumulative_losses,
                "cumulative_stake": cumulative_stake,
                "cumulative_return": cumulative_return,
                "cumulative_profit_loss": cumulative_profit_loss,
                "cumulative_roi": cumulative_roi,
            }
        )

    return history
