from typing import Dict, List

from tickets.builder import Selection, Ticket


MAX_MATCH_USAGE = 2


TICKET_PROFILES = (
    {
        "name": "SAFE",
        "stake": 40.0,
        "minimum": 3,
        "preferred": 3,
        "maximum": 4,
        "metric": "score",
    },
    {
        "name": "BALANCED",
        "stake": 30.0,
        "minimum": 3,
        "preferred": 4,
        "maximum": 5,
        "metric": "score",
    },
    {
        "name": "AGGRESSIVE",
        "stake": 20.0,
        "minimum": 3,
        "preferred": 5,
        "maximum": 6,
        "metric": "score",
    },
    {
        "name": "VALUE",
        "stake": 10.0,
        "minimum": 3,
        "preferred": 4,
        "maximum": 5,
        "metric": "value_edge",
    },
)


def _candidate_to_selection(candidate: Dict) -> Selection:
    required = {
        "match_id",
        "home_team",
        "away_team",
        "market",
        "odds",
        "model_probability",
        "value_edge",
    }

    missing = required - candidate.keys()

    if missing:
        raise ValueError(
            f"Candidate is missing fields: {sorted(missing)}"
        )

    return Selection(
        match_id=candidate["match_id"],
        match=(
            f'{candidate["home_team"]} '
            f'vs {candidate["away_team"]}'
        ),
        market=candidate["market"],
        odds=candidate["odds"],
        confidence=candidate["model_probability"] * 100,
        value_edge=candidate["value_edge"],
    )


def _rank_candidate(
    candidate: Dict,
    metric: str,
    usage_count: int,
) -> float:
    """
    Calculate a temporary ranking score.

    Reusing a match costs points so the four
    tickets become more different.
    """

    if metric == "score":
        base_score = candidate.get("score", 0.0)

    elif metric == "value_edge":
        base_score = candidate.get("value_edge", 0.0) * 5.0

    else:
        raise ValueError(
            f"Unsupported ranking metric: {metric}"
        )

    diversity_penalty = usage_count * 6.0

    return base_score - diversity_penalty


def _choose_candidates(
    candidates: List[Dict],
    metric: str,
    usage: Dict[str, int],
    minimum: int,
    preferred: int,
    maximum: int,
) -> List[Dict]:
    """
    Choose candidates while limiting repeated matches.

    A match can appear in at most two tickets.
    """

    ranked = []

    for candidate in candidates:
        match_id = candidate["match_id"]

        if usage.get(match_id, 0) >= MAX_MATCH_USAGE:
            continue

        ranking = _rank_candidate(
            candidate,
            metric,
            usage.get(match_id, 0),
        )

        ranked.append(
            (ranking, candidate)
        )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    chosen = []

    for _, candidate in ranked:
        chosen.append(candidate)

        if len(chosen) >= preferred:
            break

    # If the preferred size cannot be reached,
    # try the minimum before giving up.
    if len(chosen) < minimum:
        return []

    return chosen[:maximum]


def build_smart_portfolio(
    candidates: List[Dict],
) -> List[Ticket]:
    """
    Build four different tickets.

    Rules:
    - 40% / 30% / 20% / 10%
    - Minimum 3 selections per ticket
    - Maximum 6 selections
    - A match can appear in at most 2 tickets
    - No forced weak selection
    """

    if not candidates:
        return []

    # Validate candidates and remove duplicate match IDs.
    cleaned = []
    seen_matches = set()

    for candidate in candidates:

        selection = _candidate_to_selection(candidate)
        selection.validate()

        match_id = candidate["match_id"]

        if match_id in seen_matches:
            continue

        seen_matches.add(match_id)
        cleaned.append(candidate)

    usage: Dict[str, int] = {}
    tickets: List[Ticket] = []

    for profile in TICKET_PROFILES:

        chosen = _choose_candidates(
            candidates=cleaned,
            metric=profile["metric"],
            usage=usage,
            minimum=profile["minimum"],
            preferred=profile["preferred"],
            maximum=profile["maximum"],
        )

        if len(chosen) < profile["minimum"]:
            # Do not force a ticket.
            continue

        selections = [
            _candidate_to_selection(candidate)
            for candidate in chosen
        ]

        for candidate in chosen:
            match_id = candidate["match_id"]
            usage[match_id] = usage.get(match_id, 0) + 1

        tickets.append(
            Ticket(
                name=profile["name"],
                stake_percent=profile["stake"],
                selections=selections,
            )
        )

    return tickets
