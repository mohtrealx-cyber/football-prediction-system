import math

from backtesting.ticket_engine import backtest_ticket


REQUIRED_FIELDS = {
    "ticket_name",
    "selections",
    "stake",
}

EXPECTED_TICKET_COUNT = 4


def backtest_four_tickets(tickets: list) -> dict:
    """
    Backtest the four daily tickets and combine their results
    into one portfolio-level result.
    """

    if not isinstance(tickets, list):
        raise TypeError("tickets must be a list")

    if len(tickets) != EXPECTED_TICKET_COUNT:
        raise ValueError("Exactly four tickets are required")

    seen_names = set()

    total_tickets = 0
    wins = 0
    losses = 0
    total_stake = 0.0
    total_return = 0.0
    total_profit_loss = 0.0

    ticket_breakdown = {}

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise TypeError("Every ticket must be a dictionary")

        missing_fields = REQUIRED_FIELDS - ticket.keys()

        if missing_fields:
            raise ValueError(
                f"Ticket is missing required fields: {sorted(missing_fields)}"
            )

        ticket_name = ticket["ticket_name"]

        if not isinstance(ticket_name, str):
            raise ValueError("ticket_name must be a string")

        if not ticket_name:
            raise ValueError("ticket_name cannot be empty")

        if ticket_name in seen_names:
            raise ValueError(f"Duplicate ticket name: {ticket_name}")

        seen_names.add(ticket_name)

        selections = ticket["selections"]

        if not isinstance(selections, list):
            raise TypeError("selections must be a list")

        stake = ticket["stake"]

        if isinstance(stake, bool) or not isinstance(stake, (int, float)):
            raise ValueError("stake must be numeric")

        if not math.isfinite(stake):
            raise ValueError("stake must be finite")

        if stake <= 0:
            raise ValueError("stake must be greater than zero")

        result = backtest_ticket(
            selections=selections,
            stake=float(stake),
        )

        total_tickets += 1

        if result["won"]:
            wins += 1
        else:
            losses += 1

        total_stake += result["stake"]
        total_return += result["return_amount"]
        total_profit_loss += result["profit_loss"]

        ticket_breakdown[ticket_name] = {
            "won": result["won"],
            "stake": result["stake"],
            "return_amount": result["return_amount"],
            "profit_loss": result["profit_loss"],
            "combined_odds": result["combined_odds"],
            "selection_count": result["selection_count"],
            "selections": result["selections"],
        }

    roi = (
        total_profit_loss / total_stake
        if total_stake > 0
        else 0.0
    )

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
