from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ============================================================================
# PORTFOLIO CONFIGURATION
# ============================================================================

TICKET_SPECS = {
    "SAFE": {
        "stake_percent": 40.0,
        "preferred_matches": 3,
        "max_matches": 4,
        "metric": "score",
    },
    "BALANCED": {
        "stake_percent": 30.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "score",
    },
    "AGGRESSIVE": {
        "stake_percent": 20.0,
        "preferred_matches": 5,
        "max_matches": 6,
        "metric": "score",
    },
    "VALUE": {
        "stake_percent": 10.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "value_edge",
    },
}

TICKET_ORDER = (
    "SAFE",
    "BALANCED",
    "AGGRESSIVE",
    "VALUE",
)

MIN_SELECTIONS = 3
MAX_MATCH_USAGE = 2
DIVERSITY_PENALTY = 6.0


# ============================================================================
# CANDIDATE VALIDATION
# ============================================================================
#
# IMPORTANT:
# "selection" is NOT required here.
#
# Your older portfolio tests/candidates do not necessarily contain it.
# The actual Selection dataclass requires:
#
#   match_id
#   match
#   market
#   odds
#   confidence
#   value_edge
#
# The candidate "selection" field belongs to newer daily market candidates
# and is therefore supported when present, but it is not part of the minimum
# portfolio candidate contract.
#
# These are the fields the portfolio engine actually requires.
# ============================================================================

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


def _validate_candidate(candidate: dict) -> None:
    """Validate one portfolio candidate."""

    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")

    missing = [
        field
        for field in REQUIRED_CANDIDATE_FIELDS
        if field not in candidate
    ]

    if missing:
        raise ValueError(
            "candidate is missing required field(s): "
            + ", ".join(missing)
        )


def _validate_candidates(candidates: Sequence[dict]) -> None:
    """Validate the complete candidate collection."""

    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================================
# NUMERIC HELPERS
# ============================================================================

def _safe_float(value: Any, field_name: str) -> float:
    """Convert a value to a finite float."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be a numeric value"
        ) from None

    if not math.isfinite(number):
        raise ValueError(
            f"{field_name} must be finite"
        )

    return number


# ============================================================================
# FIELD RESOLUTION
# ============================================================================

def _resolve_match_id(candidate: dict) -> str:
    """Return the candidate match ID."""

    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError("candidate match_id cannot be missing")

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError("candidate match_id cannot be empty")

    return match_id


def _resolve_market(candidate: dict) -> str:
    """Return the candidate market."""

    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the odds used by Selection.

    Supported candidate formats:

    1. Numeric odds:

        "odds": 1.80

    2. Full odds dictionary:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    3. Explicit selected odds:

        "selected_odds": 1.80
    """

    # Newer daily-real candidates explicitly provide selected_odds.
    if "selected_odds" in candidate:
        selected_odds = candidate.get("selected_odds")

        if selected_odds is not None:
            odds = _safe_float(
                selected_odds,
                "selected_odds",
            )

            if odds <= 1.0:
                raise ValueError(
                    "selected_odds must be greater than 1.0"
                )

            return odds

    raw_odds = candidate.get("odds")

    # ------------------------------------------------------------------------
    # Numeric odds
    # ------------------------------------------------------------------------

    if not isinstance(raw_odds, dict):
        odds = _safe_float(
            raw_odds,
            "odds",
        )

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    # ------------------------------------------------------------------------
    # Dictionary odds
    # ------------------------------------------------------------------------

    market = _resolve_market(candidate)

    # Direct market key.
    if market in raw_odds:
        odds = _safe_float(
            raw_odds[market],
            "odds",
        )

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    # Compatibility aliases.
    market_aliases = {
        "home_win": (
            "HOME",
            "1",
            "home",
        ),
        "draw": (
            "DRAW",
            "X",
            "draw",
        ),
        "away_win": (
            "AWAY",
            "2",
            "away",
        ),
        "over_2_5": (
            "OVER_2_5",
            "OVER 2.5",
            "OVER",
        ),
        "under_2_5": (
            "UNDER_2_5",
            "UNDER 2.5",
            "UNDER",
        ),
        "btts_yes": (
            "BTTS_YES",
            "BTTS YES",
            "YES",
        ),
        "btts_no": (
            "BTTS_NO",
            "BTTS NO",
            "NO",
        ),
    }

    for alias in market_aliases.get(market, ()):
        if alias in raw_odds:
            odds = _safe_float(
                raw_odds[alias],
                "odds",
            )

            if odds <= 1.0:
                raise ValueError(
                    "odds must be greater than 1.0"
                )

            return odds

    # Legacy markets such as 1X/X2/12 may be used directly as keys.
    if market in raw_odds:
        odds = _safe_float(
            raw_odds[market],
            "odds",
        )

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    raise ValueError(
        f"no odds found for market: {market}"
    )


def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve confidence for tickets.builder.Selection.

    Priority:

    1. explicit confidence
    2. model_probability * 100
    3. score

    Selection.validate() requires 0 <= confidence <= 100.
    """

    if "confidence" in candidate:
        confidence = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        probability = _safe_float(
            candidate["model_probability"],
            "model_probability",
        )

        confidence = probability * 100.0

    else:
        confidence = _safe_float(
            candidate["score"],
            "score",
        )

    # Keep within Selection's required range.
    confidence = max(
        0.0,
        min(100.0, confidence),
    )

    return confidence


def _resolve_value_edge(candidate: dict) -> float:
    """Resolve and validate value edge."""

    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        raise ValueError(
            "value_edge cannot be negative"
        )

    return value_edge


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match string required by Selection.

    Supported forms:

    1. candidate["match"]
    2. candidate["home_team"] + candidate["away_team"]
    3. candidate["match_id"]
    """

    # Newer candidate format.
    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    # Daily-real candidate format.
    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    # Older tests may not contain team names.
    return _resolve_match_id(candidate)


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert one candidate into the exact Selection structure supported by
    tickets/builder.py.

    Selection accepts ONLY:

        match_id
        match
        market
        odds
        confidence
        value_edge
    """

    _validate_candidate(candidate)

    selection = Selection(
        match_id=_resolve_match_id(candidate),
        match=_resolve_match(candidate),
        market=_resolve_market(candidate),
        odds=_resolve_candidate_odds(candidate),
        confidence=_resolve_confidence(candidate),
        value_edge=_resolve_value_edge(candidate),
    )

    # Use the actual validation method provided by Selection.
    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    """Return the metric used for ticket ranking."""

    if metric == "score":
        return _safe_float(
            candidate["score"],
            "score",
        )

    if metric == "value_edge":
        return _safe_float(
            candidate["value_edge"],
            "value_edge",
        )

    raise ValueError(
        f"unsupported ranking metric: {metric}"
    )


def _legacy_selection_key(candidate: dict) -> str:
    """
    Compatibility helper for older market names.

    This does not become part of Selection because Selection has no
    'selection' field.
    """

    if "selection" in candidate:
        value = candidate.get("selection")

        if value is not None:
            return str(value).strip().upper()

    market = str(candidate.get("market", "")).strip().upper()

    # Legacy market compatibility.
    legacy_mapping = {
        "1": "HOME",
        "X": "DRAW",
        "2": "AWAY",
        "1X": "HOME_OR_DRAW",
        "X2": "DRAW_OR_AWAY",
        "12": "HOME_OR_AWAY",
    }

    return legacy_mapping.get(
        market,
        market,
    )


def _rank_candidates_for_ticket(
    candidates: Sequence[dict],
    ticket_name: str,
    usage_counts: Dict[str, int] | None = None,
) -> List[dict]:
    """
    Rank candidates for a ticket.

    Matches already used in another ticket receive a diversity penalty.

    A match used twice cannot enter another ticket.
    """

    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    if usage_counts is None:
        usage_counts = {}

    spec = TICKET_SPECS[ticket_name]
    metric = spec["metric"]

    ranked = []

    for candidate in candidates:
        _validate_candidate(candidate)

        match_id = _resolve_match_id(candidate)

        usage_count = usage_counts.get(
            match_id,
            0,
        )

        # Maximum two-ticket reuse.
        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_score = (
            base_metric
            - usage_count * DIVERSITY_PENALTY
        )

        # Keep legacy selection computation for compatibility with old
        # candidate shapes without making it mandatory.
        selection_key = _legacy_selection_key(candidate)

        ranked.append(
            {
                "adjusted_score": adjusted_score,
                "base_metric": base_metric,
                "selection_key": selection_key,
                "candidate": candidate,
            }
        )

    # Highest adjusted score first.
    #
    # Base metric is used as the second sort criterion so that two candidates
    # with the same adjusted score remain deterministic.
    ranked.sort(
        key=lambda item: (
            item["adjusted_score"],
            item["base_metric"],
        ),
        reverse=True,
    )

    return [
        item["candidate"]
        for item in ranked
    ]


# ============================================================================
# SINGLE TICKET BUILDING
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    If fewer than three unique selections are available, no ticket is
    returned. Weak selections are not fabricated merely to reach three.
    """

    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    spec = TICKET_SPECS[ticket_name]

    selections: List[Selection] = []
    seen_match_ids = set()

    for candidate in candidates:
        _validate_candidate(candidate)

        match_id = _resolve_match_id(candidate)

        # Never duplicate a match within a ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(candidate)

        selections.append(selection)
        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Do not force weak/incomplete tickets.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================================
# MAIN PORTFOLIO BUILDER
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket portfolio.

    Ticket allocation:

        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Rules:

        - 3 selections minimum when a ticket is created
        - ticket-specific maximum selections
        - no duplicate match inside a ticket
        - maximum two-ticket match reuse
        - no forced weak ticket
        - input candidates are not mutated
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    # Strictly validate the candidate interface before doing any work.
    _validate_candidates(candidates)

    # Never mutate the caller's list/dictionaries.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Counts how many tickets have already used each match.
    usage_counts: Dict[str, int] = {}

    for ticket_name in TICKET_ORDER:
        ranked_candidates = _rank_candidates_for_ticket(
            available,
            ticket_name,
            usage_counts,
        )

        ticket = _build_ticket(
            ticket_name,
            ranked_candidates,
        )

        # Empty ticket is allowed internally.
        # This prevents us from fabricating selections.
        if ticket is None:
            continue

        portfolio.append(ticket)

        # Update cross-ticket match usage.
        for selection in ticket.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(match_id, 0) + 1
            )

    return portfolio


# ============================================================================
# PUBLIC COMPATIBILITY FUNCTIONS
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Primary legacy/public portfolio entry point.

    Older tests and portfolio.market_portfolio import this function.
    """
    return build_market_portfolio(candidates)


def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Additional compatibility alias.
    """
    return build_market_portfolio(candidates)
