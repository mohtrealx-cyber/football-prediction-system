import math


REQUIRED_FIELDS = {
    "stake",
    "won",
    "return_amount",
    "profit_loss",
}


def calculate_performance(results: list) -> dict:
    """
    Calculate aggregate performance metrics from backtest results.

    The stake values are simulated backtest stakes only.
    This function does not manage a real bankroll.
    """

    if not isinstance(results, list):
        raise TypeError("results must be a list")

    # Empty result set.
    if not results:
        return {
            "total_tickets": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "total_stake": 0.0,
            "total_return": 0.0,
            "total_profit_loss": 0.0,
            "roi": 0.0,
            "max_drawdown": 0.0,
        }

    total_tickets = len(results)
    wins = 0
    losses = 0
    total_stake = 0.0
    total_return = 0.0
    total_profit_loss = 0.0

    cumulative_profit = 0.0
    peak_profit = 0.0
    max_drawdown = 0.0

    for result in results:

        if not isinstance(result, dict):
            raise TypeError(
                "Every result must be a dictionary"
            )

        missing_fields = REQUIRED_FIELDS - result.keys()

        if missing_fields:
            raise ValueError(
                f"Result is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        stake = result["stake"]
        return_amount = result["return_amount"]
        profit_loss = result["profit_loss"]
        won = result["won"]

        # Validate stake.
        if isinstance(stake, bool):
            raise ValueError("stake must be numeric")

        if not isinstance(stake, (int, float)):
            raise ValueError("stake must be numeric")

        if not math.isfinite(stake):
            raise ValueError("stake must be finite")

        if stake <= 0:
            raise ValueError(
                "stake must be greater than zero"
            )

        # Validate return amount.
        if isinstance(return_amount, bool):
            raise ValueError("return_amount must be numeric")

        if not isinstance(return_amount, (int, float)):
            raise ValueError(
                "return_amount must be numeric"
            )

        if not math.isfinite(return_amount):
            raise ValueError(
                "return_amount must be finite"
            )

        if return_amount < 0:
            raise ValueError(
                "return_amount cannot be negative"
            )

        # Validate profit/loss.
        if isinstance(profit_loss, bool):
            raise ValueError("profit_loss must be numeric")

        if not isinstance(profit_loss, (int, float)):
            raise ValueError(
                "profit_loss must be numeric"
            )

        if not math.isfinite(profit_loss):
            raise ValueError(
                "profit_loss must be finite"
            )

        # Validate won flag.
        if not isinstance(won, bool):
            raise ValueError("won must be a boolean")

        if won:
            wins += 1
        else:
            losses += 1

        total_stake += stake
        total_return += return_amount
        total_profit_loss += profit_loss

        # Track cumulative profit for drawdown.
        cumulative_profit += profit_loss

        if cumulative_profit > peak_profit:
            peak_profit = cumulative_profit

        drawdown = peak_profit - cumulative_profit

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    win_rate = wins / total_tickets

    if total_stake > 0:
        roi = total_profit_loss / total_stake
    else:
        roi = 0.0

    return {
        "total_tickets": total_tickets,
        "wins": wins,
        "losses": losses,
        "win_rate": float(win_rate),
        "total_stake": float(total_stake),
        "total_return": float(total_return),
        "total_profit_loss": float(total_profit_loss),
        "roi": float(roi),
        "max_drawdown": float(max_drawdown),
    }
