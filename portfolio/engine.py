from __future__ import annotations

from typing import Any

from tickets.builder import Selection, Ticket


# ============================================================
# PORTFOLIO CONFIGURATION
# ============================================================

TICKET_SPECS = (
    ("IRONCLAD", 40.0),
    ("BALANCED", 30.0),
    ("VOLATILITY", 20.0),
    ("BENCHMARK", 10.0),
)

MIN_SELECTIONS = 3
MAX_SELECTIONS = 6


# Minimum confidence/value requirements.
#
# These are intentionally different for each portfolio layer.
# IRONCLAD is the most selective.
TICKET_RULES = {
    "IRONCLAD": {
        "metric": "confidence",
        "threshold": 70.0,
    },
    "BALANCED": {
        "metric": "confidence",
        "threshold": 55.0,
    },
    "VOLATILITY": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
    "BENCHMARK": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
}


# ============================================================
# VALIDATION
# ============================================================

def _validate_candidate(candidate: Any) -> None:
    """Validate one market candidate."""

    if not isinstance(candidate, dict):
        raise TypeError("each candidate must be a dictionary")

    required = {
        "match_id",
        "home_team",
        "away_team",
        "market",
        "selected_odds",
        "model_probability",
        "value_edge",
    }

    missing = required - candidate.keys()

    if missing:
        raise ValueError(
            f"candidate missing required fields: {sorted(missing)}"
        )

    match_id = candidate["match_id"]

    if not isinstance(match_id, str) or not match_id.strip():
        raise ValueError(
            "candidate match_id must be a non-empty string"
        )

    odds = candidate["selected_odds"]

    if not isinstance(odds, (int, float)):
        raise TypeError(
            "candidate selected_odds must be numeric"
        )

    if odds <= 1.0:
        raise ValueError(
            "candidate selected_odds must be greater than 1.0"
        )

    probability = candidate["model_probability"]

    if not isinstance(probability, (int, float)):
        raise TypeError(
            "candidate model_probability must be numeric"
        )

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "candidate model_probability must be between 0 and 1"
        )

    value_edge = candidate["value_edge"]

    if not isinstance(value_edge, (int, float)):
        raise TypeError(
            "candidate value_edge must be numeric"
        )


# ============================================================
# CONVERSION
# ============================================================

def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """Convert a market candidate into a Ticket Selection."""

    return Selection(
        match_id=str(candidate["match_id"]),
        match=(
            f"{candidate['home_team']} "
            f"vs "
            f"{candidate['away_team']}"
        ),
        market=str(candidate["selection"]),
        odds=float(candidate["selected_odds"]),
        confidence=float(
            candidate["model_probability"] * 100.0
        ),
        value_edge=float(candidate["value_edge"]),
    )


# ============================================================
# SCORING
# ============================================================

def _sort_candidates(
    candidates: list[dict],
    metric: str,
) -> list[dict]:
    """
    Sort candidates according to portfolio objective.

    Confidence portfolios prioritize probability.
    Value portfolios prioritize value edge.
    """

    if metric == "confidence":
        return sorted(
            candidates,
            key=lambda item: (
                float(item["model_probability"]),
                float(item["value_edge"]),
                float(item["selected_odds"]),
            ),
            reverse=True,
        )

    if metric == "value_edge":
        return sorted(
            candidates,
            key=lambda item: (
                float(item["value_edge"]),
                float(item["model_probability"]),
                float(item["selected_odds"]),
            ),
            reverse=True,
        )

    raise ValueError(
        f"Unsupported portfolio metric: {metric}"
    )


# ============================================================
# ELIGIBILITY
# ============================================================

def _eligible_candidates(
    candidates: list[dict],
    metric: str,
    threshold: float,
) -> list[dict]:
    """Return candidates satisfying a ticket rule."""

    if metric == "confidence":
        return [
            candidate
            for candidate in candidates
            if (
                float(candidate["model_probability"]) * 100.0
                >= threshold
            )
        ]

    if metric == "value_edge":
        return [
            candidate
            for candidate in candidates
            if float(candidate["value_edge"]) >= threshold
        ]

    raise ValueError(
        f"Unsupported portfolio metric: {metric}"
    )


# ============================================================
# MATCH CONFLICT HANDLING
# ============================================================

def _select_unique_matches(
    candidates: list[dict],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Select candidates without using the same match twice
    inside one ticket.

    blocked_matches is optional and is primarily used to
    protect the IRONCLAD/BENCHMARK separation.
    """

    if blocked_matches is None:
        blocked_matches = set()

    selected: list[dict] = []
    used_matches: set[str] = set()

    for candidate in candidates:
        match_id = str(candidate["match_id"])

        if match_id in used_matches:
            continue

        if match_id in blocked_matches:
            continue

        selected.append(candidate)
        used_matches.add(match_id)

        if len(selected) >= maximum:
            break

    return selected


# ============================================================
# FALLBACK SELECTION
# ============================================================

def _fill_ticket(
    selected: list[dict],
    all_candidates: list[dict],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Fill a ticket if its strict eligibility rule does not
    provide enough unique matches.

    We relax the threshold only as a construction fallback.
    We never manufacture candidates.
    """

    if blocked_matches is None:
        blocked_matches = set()

    selected_ids = {
        str(candidate["match_id"])
        for candidate in selected
    }

    used_matches = set(selected_ids)

    for candidate in all_candidates:
        match_id = str(candidate["match_id"])

        if match_id in used_matches:
            continue

        if match_id in blocked_matches:
            continue

        selected.append(candidate)
        used_matches.add(match_id)

        if len(selected) >= maximum:
            break

    return selected


# ============================================================
# TICKET BUILDER
# ============================================================

def _build_ticket(
    name: str,
    stake_percent: float,
    candidates: list[dict],
    blocked_matches: set[str] | None = None,
) -> Ticket | None:
    """Build one portfolio ticket."""

    rules = TICKET_RULES[name]

    eligible = _eligible_candidates(
        candidates,
        rules["metric"],
        rules["threshold"],
    )

    eligible = _sort_candidates(
        eligible,
        rules["metric"],
    )

    selected = _select_unique_matches(
        eligible,
        MAX_SELECTIONS,
        blocked_matches,
    )

    # If strict criteria produce fewer than three selections,
    # use the best remaining candidates as a controlled fallback.
    if len(selected) < MIN_SELECTIONS:
        fallback = _sort_candidates(
            candidates,
            rules["metric"],
        )

        selected = _fill_ticket(
            selected,
            fallback,
            MAX_SELECTIONS,
            blocked_matches,
        )

    if len(selected) < MIN_SELECTIONS:
        return None

    selections = [
        _candidate_to_selection(candidate)
        for candidate in selected
    ]

    ticket = Ticket(
        name=name,
        stake_percent=stake_percent,
        selections=selections,
    )

    return ticket


# ============================================================
# PUBLIC PORTFOLIO ENGINE
# ============================================================

def build_market_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Build the four-ticket market portfolio.

    Allocation:

        IRONCLAD    40%
        BALANCED    30%
        VOLATILITY  20%
        BENCHMARK   10%

    The function attempts to construct all four tickets whenever
    there are enough valid candidates.

    Each ticket contains 3-6 unique matches.

    IRONCLAD and BENCHMARK are kept separate so that the largest
    and benchmark allocations do not share the same match.
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    for candidate in candidates:
        _validate_candidate(candidate)

    # Remove exact duplicate market candidates.
    #
    # A match may still have several different markets, which is
    # allowed. The duplicate filter only removes identical
    # candidate records.
    unique_candidates: list[dict] = []
    seen_candidate_keys: set[tuple] = set()

    for candidate in candidates:
        key = (
            str(candidate["match_id"]),
            str(candidate["market"]),
        )

        if key in seen_candidate_keys:
            continue

        seen_candidate_keys.add(key)
        unique_candidates.append(candidate)

    # Highest-quality candidates first.
    ordered = sorted(
        unique_candidates,
        key=lambda item: (
            float(item.get("score", 0.0)),
            float(item["model_probability"]),
            float(item["value_edge"]),
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # IRONCLAD
    # --------------------------------------------------------

    ironclad = _build_ticket(
        name="IRONCLAD",
        stake_percent=40.0,
        candidates=ordered,
    )

    if ironclad is None:
        return []

    ironclad_matches = {
        selection.match_id
        for selection in ironclad.selections
    }

    # --------------------------------------------------------
    # BALANCED
    # --------------------------------------------------------

    balanced = _build_ticket(
        name="BALANCED",
        stake_percent=30.0,
        candidates=ordered,
    )

    # --------------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------------

    volatility = _build_ticket(
        name="VOLATILITY",
        stake_percent=20.0,
        candidates=ordered,
    )

    # --------------------------------------------------------
    # BENCHMARK
    #
    # Do not reuse IRONCLAD matches here.
    # --------------------------------------------------------

    benchmark = _build_ticket(
        name="BENCHMARK",
        stake_percent=10.0,
        candidates=ordered,
        blocked_matches=ironclad_matches,
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    tickets = [
        ticket
        for ticket in (
            ironclad,
            balanced,
            volatility,
            benchmark,
        )
        if ticket is not None
    ]

    # We want the four-ticket portfolio to be atomic.
    #
    # If one ticket cannot be constructed, do not return a
    # misleading partial portfolio.
    if len(tickets) != 4:
        return []

    # Validate allocation.
    total_stake = round(
        sum(ticket.stake_percent for ticket in tickets),
        6,
    )

    if total_stake != 100.0:
        raise AssertionError(
            "Portfolio stake allocation must equal 100%"
        )

    # Validate ticket sizes.
    for ticket in tickets:
        if not (
            MIN_SELECTIONS
            <= len(ticket.selections)
            <= MAX_SELECTIONS
        ):
            raise AssertionError(
                f"{ticket.name} must contain "
                f"{MIN_SELECTIONS}-{MAX_SELECTIONS} selections"
            )

        match_ids = [
            selection.match_id
            for selection in ticket.selections
        ]

        if len(match_ids) != len(set(match_ids)):
            raise AssertionError(
                f"{ticket.name} contains duplicate matches"
            )

    return tickets
