from __future__ import annotations

from collections import Counter
from typing import Any

from tickets.builder import Selection, Ticket


MAX_MATCH_USAGE = 2
DIVERSITY_PENALTY = 6.0


MARKET_SELECTIONS = {
    "home_win": "HOME",
    "draw": "DRAW",
    "away_win": "AWAY",
    "over_2_5": "OVER_2_5",
    "under_2_5": "UNDER_2_5",
    "btts_yes": "BTTS_YES",
    "btts_no": "BTTS_NO",
}


TICKET_PROFILES = {
    "SAFE": {
        "stake_percent": 40.0,
        "preferred_count": 3,
        "max_count": 4,
        "metric": "score",
    },
    "BALANCED": {
        "stake_percent": 30.0,
        "preferred_count": 4,
        "max_count": 5,
        "metric": "score",
    },
    "AGGRESSIVE": {
        "stake_percent": 20.0,
        "preferred_count": 5,
        "max_count": 6,
        "metric": "score",
    },
    "VALUE": {
        "stake_percent": 10.0,
        "preferred_count": 4,
        "max_count": 5,
        "metric": "value_edge",
    },
}


def _validate_candidates(
    candidates: Any,
) -> None:
    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )


def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """
    Convert a candidate dictionary into a Selection object.

    Supports both:
    1. Older candidates where odds is numeric and selection may be absent.
    2. Daily-real candidates where:
       - odds = complete market odds dictionary
       - selected_odds = numeric price for the selected market
       - selection = explicit selection label
    """

    required_fields = (
        "match_id",
        "home_team",
        "away_team",
        "market",
        "odds",
        "score",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in candidate
    ]

    if missing_fields:
        raise ValueError(
            f"Candidate is missing fields: {missing_fields}"
        )

    market = candidate["market"]

    # New daily-real candidates already provide "selection".
    # Older portfolio candidates may not, so derive it from
    # the market name.
    selection_value = candidate.get(
        "selection"
    )

    if selection_value is None:
        selection_value = MARKET_SELECTIONS.get(
            market
        )

    if selection_value is None:
        raise ValueError(
            f"Unknown market and no selection provided: {market}"
        )

    # Prefer the explicitly selected market price.
    odds_value = candidate.get(
        "selected_odds"
    )

    if odds_value is None:
        odds_value = candidate.get(
            "odds"
        )

    # Daily-real candidates preserve all market odds inside
    # the "odds" dictionary.
    if isinstance(
        odds_value,
        dict,
    ):
        if market not in odds_value:
            raise ValueError(
                "Candidate odds are missing market: "
                f"{market}"
            )

        odds_value = odds_value[market]

    if not isinstance(
        odds_value,
        (int, float),
    ):
        raise TypeError(
            "Candidate selected odds must be numeric"
        )

    return Selection(
        match_id=candidate["match_id"],
        home_team=candidate["home_team"],
        away_team=candidate["away_team"],
        market=market,
        selection=selection_value,
        odds=float(odds_value),
        score=float(
            candidate["score"]
        ),
    )


def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    value = candidate.get(
        metric,
        0.0,
    )

    if not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(
            f"candidate {metric} must be numeric"
        )

    return float(value)


def _selection_match_id(
    selection: Selection,
) -> str:
    return str(
        selection.match_id
    )


def _candidate_selection_name(
    candidate: dict,
) -> str:
    """
    Return the candidate selection name.

    Uses explicit "selection" when available.
    Otherwise derives it from the market.
    """

    selection_value = candidate.get(
        "selection"
    )

    if selection_value is not None:
        return str(
            selection_value
        )

    market = candidate.get(
        "market",
        "",
    )

    return str(
        MARKET_SELECTIONS.get(
            market,
            "",
        )
    )


def _rank_candidates_for_ticket(
    candidates: list[dict],
    ticket_name: str,
    match_usage: Counter,
) -> list[dict]:
    profile = TICKET_PROFILES[
        ticket_name
    ]

    metric = profile[
        "metric"
    ]

    ranked = []

    for candidate in candidates:
        match_id = str(
            candidate["match_id"]
        )

        usage_count = match_usage.get(
            match_id,
            0,
        )

        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_score = _candidate_metric(
            candidate,
            metric,
        )

        diversity_penalty = (
            usage_count
            * DIVERSITY_PENALTY
        )

        adjusted_score = (
            base_score
            - diversity_penalty
        )

        ranked.append(
            (
                adjusted_score,
                base_score,
                candidate,
            )
        )

    ranked.sort(
        key=lambda item: (
            -item[0],
            -item[1],
            str(
                item[2]["match_id"]
            ),
            str(
                item[2].get(
                    "market",
                    "",
                )
            ),
            _candidate_selection_name(
                item[2]
            ),
        )
    )

    return [
        item[2]
        for item in ranked
    ]


def _select_for_ticket(
    candidates: list[dict],
    ticket_name: str,
    match_usage: Counter,
) -> list[Selection]:
    profile = TICKET_PROFILES[
        ticket_name
    ]

    preferred_count = profile[
        "preferred_count"
    ]

    max_count = profile[
        "max_count"
    ]

    ranked_candidates = (
        _rank_candidates_for_ticket(
            candidates=candidates,
            ticket_name=ticket_name,
            match_usage=match_usage,
        )
    )

    selections: list[Selection] = []

    used_match_ids: set[str] = set()

    for candidate in ranked_candidates:
        match_id = str(
            candidate["match_id"]
        )

        # No duplicate match inside one ticket.
        if match_id in used_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selection.validate()

        selections.append(
            selection
        )

        used_match_ids.add(
            match_id
        )

        if len(selections) >= max_count:
            break

    # Never force weak selections.
    # A ticket requires at least three matches.
    if len(selections) < 3:
        return []

    # Prefer the configured ticket size when enough
    # independent matches are available.
    if len(selections) > preferred_count:
        selections = selections[
            :preferred_count
        ]

    return selections


def _build_ticket(
    ticket_name: str,
    selections: list[Selection],
) -> Ticket:
    profile = TICKET_PROFILES[
        ticket_name
    ]

    ticket = Ticket(
        name=ticket_name,
        stake_percent=profile[
            "stake_percent"
        ],
        selections=selections,
    )

    ticket.validate()

    return ticket


def build_smart_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Build the four-ticket football portfolio.

    Rules:
    - SAFE: 40%
    - BALANCED: 30%
    - AGGRESSIVE: 20%
    - VALUE: 10%
    - minimum 3 selections per ticket
    - maximum 6 selections per ticket
    - no duplicate match inside a ticket
    - maximum match reuse across portfolio: 2
    - never force a ticket with fewer than 3 selections
    """

    _validate_candidates(
        candidates
    )

    if not candidates:
        return []

    working_candidates = []

    for candidate in candidates:
        if not isinstance(
            candidate,
            dict,
        ):
            raise TypeError(
                "each candidate must be a dictionary"
            )

        # Explicitly unqualified candidates are excluded.
        if candidate.get(
            "qualified"
        ) is False:
            continue

        working_candidates.append(
            dict(candidate)
        )

    if not working_candidates:
        return []

    portfolio: list[Ticket] = []

    match_usage: Counter = Counter()

    for ticket_name in (
        "SAFE",
        "BALANCED",
        "AGGRESSIVE",
        "VALUE",
    ):
        selections = _select_for_ticket(
            candidates=working_candidates,
            ticket_name=ticket_name,
            match_usage=match_usage,
        )

        if len(selections) < 3:
            # No forced ticket.
            continue

        ticket = _build_ticket(
            ticket_name=ticket_name,
            selections=selections,
        )

        portfolio.append(
            ticket
        )

        for selection in selections:
            match_usage[
                _selection_match_id(
                    selection
                )
            ] += 1

    return portfolio


__all__ = [
    "MAX_MATCH_USAGE",
    "DIVERSITY_PENALTY",
    "TICKET_PROFILES",
    "build_smart_portfolio",
]
