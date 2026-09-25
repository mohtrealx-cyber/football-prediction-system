from __future__ import annotations

from collections import Counter
from typing import Any


EXPECTED_TICKETS = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)

EXPECTED_STAKES = {
    "SAFE": 40.0,
    "BALANCED": 30.0,
    "AGGRESSIVE": 20.0,
    "VALUE": 10.0,
}

MIN_SELECTIONS = 3
MAX_SELECTIONS = 6
MAX_MATCH_REUSE = 2


def _validate_ticket(ticket: Any) -> None:
    if not hasattr(ticket, "name"):
        raise TypeError("each portfolio item must be a Ticket")

    if not hasattr(ticket, "stake_percent"):
        raise TypeError("ticket must have stake_percent")

    if not hasattr(ticket, "selections"):
        raise TypeError("ticket must have selections")

    if ticket.name not in EXPECTED_TICKETS:
        raise ValueError(
            f"unknown ticket name: {ticket.name}"
        )

    expected_stake = EXPECTED_STAKES[ticket.name]

    if ticket.stake_percent != expected_stake:
        raise ValueError(
            f"{ticket.name} has invalid stake allocation"
        )

    if not isinstance(ticket.selections, list):
        raise TypeError(
            f"{ticket.name} selections must be a list"
        )

    selection_count = len(ticket.selections)

    if selection_count == 0:
        return

    if selection_count < MIN_SELECTIONS:
        raise ValueError(
            f"{ticket.name} has fewer than "
            f"{MIN_SELECTIONS} selections"
        )

    if selection_count > MAX_SELECTIONS:
        raise ValueError(
            f"{ticket.name} has more than "
            f"{MAX_SELECTIONS} selections"
        )

    match_ids = []

    for selection in ticket.selections:
        if not hasattr(selection, "match_id"):
            raise TypeError(
                "each selection must have match_id"
            )

        if hasattr(selection, "qualified"):
            if selection.qualified is not True:
                raise ValueError(
                    "unqualified selection found in portfolio"
                )

        match_ids.append(selection.match_id)

    if len(match_ids) != len(set(match_ids)):
        raise ValueError(
            f"{ticket.name} contains a duplicate match"
        )


def validate_daily_portfolio(
    portfolio: list[Any],
) -> bool:
    if not isinstance(portfolio, list):
        raise TypeError(
            "portfolio must be a list"
        )

    if len(portfolio) != len(EXPECTED_TICKETS):
        raise ValueError(
            "portfolio must contain exactly four tickets"
        )

    for ticket in portfolio:
        _validate_ticket(ticket)

    ticket_names = [ticket.name for ticket in portfolio]

    if set(ticket_names) != set(EXPECTED_TICKETS):
        raise ValueError(
            "portfolio must contain SAFE, BALANCED, "
            "AGGRESSIVE and VALUE exactly once"
        )

    if len(ticket_names) != len(set(ticket_names)):
        raise ValueError(
            "duplicate ticket name found"
        )

    match_usage = Counter()

    for ticket in portfolio:
        for selection in ticket.selections:
            match_usage[selection.match_id] += 1

    for match_id, usage_count in match_usage.items():
        if usage_count > MAX_MATCH_REUSE:
            raise ValueError(
                f"match {match_id} appears in "
                f"{usage_count} tickets; maximum is "
                f"{MAX_MATCH_REUSE}"
            )

    return True
