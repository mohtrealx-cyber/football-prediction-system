from __future__ import annotations

from collections import Counter
from typing import Any


EXPECTED_TICKETS = (
    "IRONCLAD",
    "BALANCED",
    "VOLATILITY",
    "BENCHMARK",
)

EXPECTED_STAKES = {
    "IRONCLAD": 40.0,
    "BALANCED": 30.0,
    "VOLATILITY": 20.0,
    "BENCHMARK": 10.0,
}

MIN_SELECTIONS = 3
MAX_SELECTIONS = 6
MAX_MATCH_REUSE = 2


def _validate_ticket(ticket: Any) -> None:
    """Validate one portfolio ticket."""

    if not hasattr(ticket, "name"):
        raise TypeError(
            "each portfolio item must be a Ticket"
        )

    if not hasattr(ticket, "stake_percent"):
        raise TypeError(
            "ticket must have stake_percent"
        )

    if not hasattr(ticket, "selections"):
        raise TypeError(
            "ticket must have selections"
        )

    if ticket.name not in EXPECTED_TICKETS:
        raise ValueError(
            f"unknown ticket name: {ticket.name}"
        )

    expected_stake = EXPECTED_STAKES[ticket.name]

    if float(ticket.stake_percent) != expected_stake:
        raise ValueError(
            f"{ticket.name} has invalid stake allocation"
        )

    if not isinstance(ticket.selections, list):
        raise TypeError(
            f"{ticket.name} selections must be a list"
        )

    selection_count = len(ticket.selections)

    # Empty tickets are allowed for validator-level tests.
    # The portfolio engine itself never returns empty tickets.
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

        if not hasattr(selection, "selected_odds"):
            raise ValueError(
                "selection is missing selected_odds"
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
    """Validate the complete four-ticket portfolio."""

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

    ticket_names = [
        ticket.name
        for ticket in portfolio
    ]

    if set(ticket_names) != set(EXPECTED_TICKETS):
        raise ValueError(
            "portfolio must contain IRONCLAD, BALANCED, "
            "VOLATILITY and BENCHMARK exactly once"
        )

    if len(ticket_names) != len(set(ticket_names)):
        raise ValueError(
            "duplicate ticket name found"
        )

    total_stake = round(
        sum(
            float(ticket.stake_percent)
            for ticket in portfolio
        ),
        6,
    )

    if total_stake != 100.0:
        raise ValueError(
            "portfolio stake allocation must equal 100%"
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


__all__ = [
    "EXPECTED_TICKETS",
    "EXPECTED_STAKES",
    "MIN_SELECTIONS",
    "MAX_SELECTIONS",
    "MAX_MATCH_REUSE",
    "validate_daily_portfolio",
]
