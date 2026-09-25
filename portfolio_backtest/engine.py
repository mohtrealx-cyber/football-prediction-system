import math


REQUIRED_FIELDS = {
    "ticket_name",
    "won",
    "stake",
    "return_amount",
    "profit_loss",
}

REQUIRED_TICKET_NAMES = {
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
}


def evaluate_portfolio(tickets: list) -> dict:
    """
    Evaluate the combined performance of a four-ticket portfolio.

    This uses simulated backtest stakes only.
    It does not manage a real bankroll.
    """

    if not isinstance(tickets, list):
        raise TypeError("tickets must be a list")

    if not tickets:
        return {
            "total_tickets": 0,
            "wins": 0,
            "losses": 0,
            "total_stake": 0.0,
            "total_return": 0.0,
            "total_profit_loss": 0.0,
            "roi": 0.0,
            "ticket_breakdown": {},
        }

    seen_names = set()

    total_tickets = len(tickets)
    wins = 0
    losses = 0
    total_stake = 0.0
    total_return = 0.0
    total_profit_loss = 0.0

    ticket_breakdown = {}

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise TypeError(
                "Every ticket must be a dictionary"
            )

        missing_fields = REQUIRED_FIELDS - ticket.keys()

        if missing_fields:
            raise ValueError(
                f"Ticket is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        ticket_name = ticket["ticket_name"]

        if not isinstance(ticket_name, str):
            raise ValueError(
                "ticket_name must be a string"
            )

        if not ticket_name:
            raise ValueError(
                "ticket_name cannot be empty"
            )

        if ticket_name in seen_names:
            raise ValueError(
                f"Duplicate ticket name: {ticket_name}"
            )

        seen_names.add(ticket_name)

        stake = ticket["stake"]
        return_amount = ticket["return_amount"]
        profit_loss = ticket["profit_loss"]
        won = ticket["won"]

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

        if isinstance(return_amount, bool):
            raise ValueError(
                "return_amount must be numeric"
            )

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

        if isinstance(profit_loss, bool):
            raise ValueError(
                "profit_loss must be numeric"
            )

        if not isinstance(profit_loss, (int, float)):
            raise ValueError(
                "profit_loss must be numeric"
            )

        if not math.isfinite(profit_loss):
            raise ValueError(
                "profit_loss must be finite"
            )

        if not isinstance(won, bool):
            raise ValueError(
                "won must be a boolean"
            )

        if won:
            wins += 1
        else:
            losses += 1

        total_stake += stake
        total_return += return_amount
        total_profit_loss += profit_loss

        ticket_breakdown[ticket_name] = {
            "won": won,
            "stake": float(stake),
            "return_amount": float(return_amount),
            "profit_loss": float(profit_loss),
        }

    if total_stake > 0:
        roi = total_profit_loss / total_stake
    else:
        roi = 0.0

    return {
        "total_tickets": total_tickets,
        "wins": wins,
        "losses": losses,
        "total_stake": float(total_stake),
        "total_return": float(total_return),
        "total_profit_loss": float(total_profit_loss),
        "roi": float(roi),
        "ticket_breakdown": ticket_breakdown,
    }
