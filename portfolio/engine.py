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
            "candidate missing required fields: "
            f"{sorted(missing)}"
        )

    try:
        selected_odds = float(candidate["selected_odds"])
        model_probability = float(candidate["model_probability"])
        value_edge = float(candidate["value_edge"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "candidate numeric fields are invalid"
        ) from exc

    if selected_odds <= 1.0:
        raise ValueError(
            "candidate selected_odds must be greater than 1.0"
        )

    if not 0.0 <= model_probability <= 1.0:
        raise ValueError(
            "candidate model_probability must be between 0 and 1"
        )

    if value_edge < 0.0:
        raise ValueError(
            "candidate value_edge cannot be negative"
        )


def _validate_candidates(
    candidates: list[dict],
) -> None:
    """Validate the candidate collection."""

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================
# CANDIDATE CONVERSION
# ============================================================

def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """Convert one market candidate into a Ticket Selection."""

    return Selection(
        match_id=str(candidate["match_id"]),
        match=(
            f"{candidate['home_team']} "
            f"vs "
            f"{candidate['away_team']}"
        ),
        market=str(
            candidate.get(
                "selection",
                candidate["market"],
            )
        ),
        odds=float(candidate["selected_odds"]),
        confidence=(
            float(candidate["model_probability"]) * 100.0
        ),
        value_edge=float(candidate["value_edge"]),
    )


# ============================================================
# SORTING
# ============================================================

def _sort_candidates(
    candidates: list[dict],
    metric: str,
) -> list[dict]:
    """Sort candidates according to the ticket objective."""

    if metric == "confidence":
        return sorted(
            candidates,
            key=lambda item: (
                float(item["model_probability"]),
                float(item["value_edge"]),
                float(item["selected_odds"]),
                float(item.get("score", 0.0)),
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
                float(item.get("score", 0.0)),
            ),
            reverse=True,
        )

    if metric == "score":
        return sorted(
            candidates,
            key=lambda item: (
                float(item.get("score", 0.0)),
                float(item["model_probability"]),
                float(item["value_edge"]),
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
    """Return candidates satisfying the ticket rule."""

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
# UNIQUE MATCH SELECTION
# ============================================================

def _select_unique_matches(
    candidates: list[dict],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Select candidates without repeating a match inside a ticket.

    blocked_matches prevents reuse across protected tickets.
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
# FALLBACK
# ============================================================

def _fill_ticket(
    selected: list[dict],
    all_candidates: list[dict],
    maximum: int,
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Fill a ticket with the best remaining candidates.

    This never manufactures a selection.
    """

    if blocked_matches is None:
        blocked_matches = set()

    selected_ids = {
        str(candidate["match_id"])
        for candidate in selected
    }

    result = list(selected)

    for candidate in all_candidates:
        if len(result) >= maximum:
            break

        match_id = str(candidate["match_id"])

        if match_id in selected_ids:
            continue

        if match_id in blocked_matches:
            continue

        result.append(candidate)
        selected_ids.add(match_id)

    return result


# ============================================================
# BUILD ONE TICKET
# ============================================================

def _build_ticket(
    name: str,
    stake_percent: float,
    candidates: list[dict],
    blocked_matches: set[str] | None = None,
) -> Ticket | None:
    """Build one ticket."""

    if blocked_matches is None:
        blocked_matches = set()

    rules = TICKET_RULES[name]

    eligible = _eligible_candidates(
        candidates=candidates,
        metric=rules["metric"],
        threshold=rules["threshold"],
    )

    ordered_eligible = _sort_candidates(
        eligible,
        rules["metric"],
    )

    selected = _select_unique_matches(
        candidates=ordered_eligible,
        maximum=MAX_SELECTIONS,
        blocked_matches=blocked_matches,
    )

    # Controlled fallback.
    if len(selected) < MIN_SELECTIONS:
        ordered_fallback = _sort_candidates(
            candidates,
            rules["metric"],
        )

        selected = _fill_ticket(
            selected=selected,
            all_candidates=ordered_fallback,
            maximum=MAX_SELECTIONS,
            blocked_matches=blocked_matches,
        )

    if len(selected) < MIN_SELECTIONS:
        return None

    selections = [
        _candidate_to_selection(candidate)
        for candidate in selected
    ]

    return Ticket(
        name=name,
        stake_percent=stake_percent,
        selections=selections,
    )


# ============================================================
# PUBLIC MODERN PORTFOLIO ENGINE
# ============================================================

def build_market_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Build the modern four-ticket portfolio.

    Allocation:

        IRONCLAD   40%
        BALANCED   30%
        VOLATILITY 20%
        BENCHMARK  10%

    Every ticket requires 3-6 selections.

    A match cannot appear more than once inside a ticket.

    IRONCLAD and BENCHMARK are deliberately separated.
    """

    _validate_candidates(candidates)

    if len(candidates) < MIN_SELECTIONS:
        return []

    # Remove exact duplicate candidate records.
    unique_candidates: list[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for candidate in candidates:
        key = (
            str(candidate["match_id"]),
            str(candidate["market"]),
        )

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_candidates.append(candidate)

    # Highest quality candidates first.
    ordered = _sort_candidates(
        unique_candidates,
        "score",
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
    # --------------------------------------------------------

    benchmark = _build_ticket(
        name="BENCHMARK",
        stake_percent=10.0,
        candidates=ordered,
        blocked_matches=ironclad_matches,
    )

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

    # Atomic portfolio.
    if len(tickets) != 4:
        return []

    # Allocation must equal 100%.
    total_stake = round(
        sum(
            ticket.stake_percent
            for ticket in tickets
        ),
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


# ============================================================
# LEGACY COMPATIBILITY API
# ============================================================

LEGACY_NAMES = {
    "IRONCLAD": "SAFE",
    "BALANCED": "BALANCED",
    "VOLATILITY": "AGGRESSIVE",
    "BENCHMARK": "VALUE",
}


def build_smart_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Legacy compatibility wrapper.

    Older tests and callers use:

        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    The modern engine remains:

        IRONCLAD   40%
        BALANCED   30%
        VOLATILITY 20%
        BENCHMARK  10%

    Only the public ticket names are translated here.
    """

    tickets = build_market_portfolio(candidates)

    if not tickets:
        return []

    for ticket in tickets:
        ticket.name = LEGACY_NAMES[ticket.name]

    return tickets


__all__ = [
    "TICKET_SPECS",
    "TICKET_RULES",
    "MIN_SELECTIONS",
    "MAX_SELECTIONS",
    "build_market_portfolio",
    "build_smart_portfolio",
]
