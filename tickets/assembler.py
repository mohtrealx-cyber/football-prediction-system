from typing import Dict, List

from .builder import Selection, Ticket, TicketBuilder


def build_four_tickets(
    candidates: List[Dict],
    min_matches: int = 3,
    max_matches: int = 6,
) -> List[Ticket]:
    """
    Convert ranked candidate dictionaries into Selection objects
    and build the four ticket types.

    Each candidate must contain:
        match_id
        home_team
        away_team
        market
        odds
        model_probability
        value_edge
    """

    selections: List[Selection] = []

    for candidate in candidates:
        required_fields = {
            "match_id",
            "home_team",
            "away_team",
            "market",
            "odds",
            "model_probability",
            "value_edge",
        }

        missing = required_fields - candidate.keys()

        if missing:
            raise ValueError(
                f"Candidate is missing fields: {sorted(missing)}"
            )

        confidence = candidate["model_probability"] * 100

        selections.append(
            Selection(
                match_id=candidate["match_id"],
                match=(
                    f'{candidate["home_team"]} '
                    f'vs {candidate["away_team"]}'
                ),
                market=candidate["market"],
                odds=candidate["odds"],
                confidence=confidence,
                value_edge=candidate["value_edge"],
            )
        )

    builder = TicketBuilder(
        min_matches=min_matches,
        max_matches=max_matches,
    )

    tickets = builder.build(selections)

    return tickets
