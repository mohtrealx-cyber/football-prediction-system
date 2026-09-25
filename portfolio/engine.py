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


def _candidate_selection_name(
    candidate: dict,
) -> str:
    """
    Resolve a selection name for deterministic sorting.

    Newer candidates normally contain "selection".

    Older candidates may omit "selection", so the known
    market mapping is used. Unknown legacy markets fall back
    to the market name itself.
    """

    selection_value = candidate.get(
        "selection"
    )

    if selection_value is not None:
        return str(
            selection_value
        )

    market = str(
        candidate.get(
            "market",
            "",
        )
    )

    return str(
        MARKET_SELECTIONS.get(
            market,
            market,
        )
    )


def _resolve_candidate_odds(
    candidate: dict,
) -> float:
    """
    Resolve the numeric odds for the selected market.

    Supports both candidate formats.

    Daily-real:
        odds = {
            "home_win": 1.80,
            ...
        }
        selected_odds = 1.80

    Older candidates:
        odds = 1.80
    """

    odds_value = candidate.get(
        "selected_odds"
    )

    if odds_value is None:
        odds_value = candidate.get(
            "odds"
        )

    if isinstance(
        odds_value,
        dict,
    ):
        market = candidate["market"]

        if market not in odds_value:
            raise ValueError(
                "Candidate odds are missing market: "
                f"{market}"
            )

        odds_value = odds_value[
            market
        ]

    if not isinstance(
        odds_value,
        (int, float),
    ):
        raise TypeError(
            "Candidate selected odds must be numeric"
        )

    return float(
        odds_value
    )


def _resolve_confidence(
    candidate: dict,
) -> float:
    """
    Resolve Selection.confidence.

    Priority:
    1. Explicit candidate confidence.
    2. model_probability converted from 0-1 to 0-100.
    3. Candidate score as a legacy fallback.
    """

    confidence = candidate.get(
        "confidence"
    )

    if confidence is None:
        model_probability = candidate.get(
            "model_probability"
        )

        if isinstance(
            model_probability,
            (int, float),
        ):
            confidence = (
                float(model_probability)
                * 100.0
            )

        else:
            confidence = candidate.get(
                "score",
                0.0,
            )

    if not isinstance(
        confidence,
        (int, float),
    ):
        raise TypeError(
            "Candidate confidence must be numeric"
        )

    confidence = float(
        confidence
    )

    if confidence < 0.0:
        confidence = 0.0

    if confidence > 100.0:
        confidence = 100.0

    return confidence


def _resolve_value_edge(
    candidate: dict,
) -> float:
    """
    Resolve Selection.value_edge.

    Daily-real candidates provide value_edge directly.

    Older candidates that do not provide it use 0.0.
    """

    value_edge = candidate.get(
        "value_edge",
        0.0,
    )

    if not isinstance(
        value_edge,
        (int, float),
    ):
        raise TypeError(
            "Candidate value_edge must be numeric"
        )

    value_edge = float(
        value_edge
    )

    # Selection.validate() requires value_edge >= 0.
    if value_edge < 0.0:
        value_edge = 0.0

    return value_edge


def _resolve_match(
    candidate: dict,
) -> str:
    """
    Build the human-readable match string required by Selection.
    """

    home_team = candidate.get(
        "home_team"
    )

    away_team = candidate.get(
        "away_team"
    )

    if not isinstance(
        home_team,
        str,
    ) or not home_team.strip():
        raise ValueError(
            "Candidate home_team cannot be empty"
        )

    if not isinstance(
        away_team,
        str,
    ) or not away_team.strip():
        raise ValueError(
            "Candidate away_team cannot be empty"
        )

    return (
        f"{home_team.strip()} vs "
        f"{away_team.strip()}"
    )


def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """
    Convert a candidate dictionary into the project's
    actual Selection dataclass.

    Selection requires:

        match_id
        match
        market
        odds
        confidence
        value_edge

    The candidate may contain additional fields such as:

        home_team
        away_team
        selection
        score
        model_probability
        selected_odds

    Those are used to construct the required Selection fields.
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

    odds_value = _resolve_candidate_odds(
        candidate
    )

    confidence = _resolve_confidence(
        candidate
    )

    value_edge = _resolve_value_edge(
        candidate
    )

    match = _resolve_match(
        candidate
    )

    selection = Selection(
        match_id=str(
            candidate["match_id"]
        ),
        match=match,
        market=str(
            candidate["market"]
        ),
        odds=odds_value,
        confidence=confidence,
        value_edge=value_edge,
    )

    selection.validate()

    return selection


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

    return float(
        value
    )


def _selection_match_id(
    selection: Selection,
) -> str:
    return str(
        selection.match_id
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

        # Prevent duplicate matches inside one ticket.
        if match_id in used_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(
            selection
        )

        used_match_ids.add(
            match_id
        )

        if len(selections) >= max_count:
            break

    # Never force an incomplete ticket.
    if len(selections) < 3:
        return []

    # Use the configured preferred ticket size.
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

    ticket.validate_tickets(
        [ticket]
    ) if hasattr(
        ticket,
        "validate_tickets",
    ) else None

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
            # Do not force a ticket.
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
