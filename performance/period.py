from typing import Any


REQUIRED_FIELDS = (
    "date",
    "total_tickets",
    "wins",
    "losses",
    "total_stake",
    "total_return",
    "total_profit_loss",
)


def calculate_period_performance(daily_results: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(daily_results, list):
        raise TypeError("daily_results must be a list")

    total_days = len(daily_results)

    total_tickets = 0
    wins = 0
    losses = 0
    total_stake = 0.0
    total_return = 0.0
    total_profit_loss = 0.0
    profitable_days = 0
    losing_days = 0

    for daily_result in daily_results:
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

        try:
            daily_tickets = int(daily_result["total_tickets"])
            daily_wins = int(daily_result["wins"])
            daily_losses = int(daily_result["losses"])
            daily_stake = float(daily_result["total_stake"])
            daily_return = float(daily_result["total_return"])
            daily_profit_loss = float(daily_result["total_profit_loss"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "daily performance values must be numeric"
            ) from exc

        if daily_tickets < 0:
            raise ValueError("total_tickets cannot be negative")

        if daily_wins < 0 or daily_losses < 0:
            raise ValueError("wins and losses cannot be negative")

        if daily_stake < 0:
            raise ValueError("total_stake cannot be negative")

        if daily_return < 0:
            raise ValueError("total_return cannot be negative")

        total_tickets += daily_tickets
        wins += daily_wins
        losses += daily_losses
        total_stake += daily_stake
        total_return += daily_return
        total_profit_loss += daily_profit_loss

        if daily_profit_loss > 0:
            profitable_days += 1
        elif daily_profit_loss < 0:
            losing_days += 1

    roi = (
        total_profit_loss / total_stake
        if total_stake > 0
        else 0.0
    )

    return {
        "total_days": total_days,
        "total_tickets": total_tickets,
        "wins": wins,
        "losses": losses,
        "total_stake": total_stake,
        "total_return": total_return,
        "total_profit_loss": total_profit_loss,
        "roi": roi,
        "profitable_days": profitable_days,
        "losing_days": losing_days,
    }
