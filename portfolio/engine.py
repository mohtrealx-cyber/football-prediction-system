from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ---------------------------------------------------------------------------
# Portfolio configuration
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Candidate interface
# ---------------------------------------------------------------------------
#
# IMPORTANT:
# "selection" is NOT required here.
#
# Older portfolio tests/callers provide:
#     match_id
#     market
#     odds
#     score
#     value_edge
#
# We derive the Selection value from "market" when "selection" is absent.
#
# This preserves compatibility with both the old candidate interface and
# the newer daily market pipeline.
# ---------------------------------------------------------------------------

REQUIRED_CANDIDATE_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


# ---------------------------------------------------------------------------
# Market -> selection mapping
# ---------------------------------------------------------------------------

MARKET_TO_SELECTION = {
    "home_win": "HOME",
    "draw": "DRAW",
    "away_win": "AWAY",
    "over_2_5": "OVER_2_5",
    "under_2_5": "UNDER_2_5",
    "btts_yes": "BTTS_YES",
    "btts_no": "BTTS_NO",
}


# Legacy aliases used by older tests/callers.
LEGACY_SELECTION_ALIASES = {
    "1": "HOME",
    "X": "DRAW",
    "2": "AWAY",
    "1X": "1X",
    "X2": "X2",
    "12": "12",
}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_candidate(candidate: dict) -> None:
    """
    Validate the required portfolio candidate interface.

    'selection' is intentionally not required because it can be derived
    from the market field for legacy candidates.
    """
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
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(candidate)


def _safe_float(value: Any, field_name: str) -> float:
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


# ---------------------------------------------------------------------------
# Basic candidate fields
# ---------------------------------------------------------------------------

def _resolve_match_id(candidate: dict) -> str:
    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError(
            "candidate match_id cannot be missing"
        )

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError(
            "candidate match_id cannot be empty"
        )

    return match_id


def _resolve_market(candidate: dict) -> str:
    market = candidate.get("market")

    if not isinstance(market, str):
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    market = market.strip()

    if not market:
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market


def _resolve_selection(candidate: dict) -> str:
    """
    Resolve the Selection.selection field.

    Newer candidates may already contain "selection".

    Older candidates only contain "market", so the selection is derived
    from the market name.
    """
    # Newer candidate format.
    if "selection" in candidate:
        selection = candidate["selection"]

        if isinstance(selection, str):
            selection = selection.strip()

            if selection:
                return LEGACY_SELECTION_ALIASES.get(
                    selection,
                    selection,
                )

        elif selection is not None:
            selection = str(selection).strip()

            if selection:
                return LEGACY_SELECTION_ALIASES.get(
                    selection,
                    selection,
                )

    # Legacy candidate format: derive selection from market.
    market = _resolve_market(candidate)

    if market in MARKET_TO_SELECTION:
        return MARKET_TO_SELECTION[market]

    # If market itself is a legacy selection, preserve it.
    if market in LEGACY_SELECTION_ALIASES:
        return LEGACY_SELECTION_ALIASES[market]

    # Safe fallback for a valid non-empty market.
    return market


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match string required by Selection.

    Supported candidate shapes:

        {"match": "Arsenal vs Chelsea"}

    or:

        {
            "home_team": "Arsenal",
            "away_team": "Chelsea"
        }

    or:

        {"match_id": "M1"}
    """
    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if home_team is not None and away_team is not None:
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    return _resolve_match_id(candidate)


# ---------------------------------------------------------------------------
# Odds resolution
# ---------------------------------------------------------------------------

def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the actual numeric odds for the candidate.

    Supported formats:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    "selected_odds" takes priority when present.
    """
    # Newer daily pipeline format.
    if "selected_odds" in candidate:
        selected_odds = candidate["selected_odds"]

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

    # Numeric odds.
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

    # Dictionary odds.
    market = _resolve_market(candidate)

    # Direct market lookup.
    if market in raw_odds:
        odds = _safe_float(
            raw_odds[market],
            "odds",
        )

    else:
        # Common aliases.
        aliases = {
            "home_win": (
                "HOME",
                "1",
            ),
            "draw": (
                "DRAW",
                "X",
            ),
            "away_win": (
                "AWAY",
                "2",
            ),
            "over_2_5": (
                "OVER_2_5",
                "OVER 2.5",
            ),
            "under_2_5": (
                "UNDER_2_5",
                "UNDER 2.5",
            ),
            "btts_yes": (
                "BTTS_YES",
                "BTTS YES",
            ),
            "btts_no": (
                "BTTS_NO",
                "BTTS NO",
            ),
        }

        found_value = None

        for alias in aliases.get(market, ()):
            if alias in raw_odds:
                found_value = raw_odds[alias]
                break

        # Candidate selection lookup.
        if found_value is None:
            candidate_selection = candidate.get("selection")

            if candidate_selection in raw_odds:
                found_value = raw_odds[
                    candidate_selection
                ]

        if found_value is None:
            raise ValueError(
                f"no odds found for market: {market}"
            )

        odds = _safe_float(
            found_value,
            "odds",
        )

    if odds <= 1.0:
        raise ValueError(
            "odds must be greater than 1.0"
        )

    return odds


# ---------------------------------------------------------------------------
# Confidence / value resolution
# ---------------------------------------------------------------------------

def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve confidence for tickets.builder.Selection.

    Priority:
        1. explicit confidence
        2. model_probability * 100
        3. score
    """
    if "confidence" in candidate:
        value = _safe_float(
            candidate["confidence"],
            "confidence",
        )

    elif "model_probability" in candidate:
        value = (
            _safe_float(
                candidate["model_probability"],
                "model_probability",
            )
            * 100.0
        )

    else:
        value = _safe_float(
            candidate["score"],
            "score",
        )

    # Selection.validate() requires 0 <= confidence <= 100.
    return max(
        0.0,
        min(100.0, value),
    )


def _resolve_value_edge(candidate: dict) -> float:
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        value_edge = 0.0

    return value_edge


# ---------------------------------------------------------------------------
# Candidate -> Selection
# ---------------------------------------------------------------------------

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate into the exact Selection structure
    defined in tickets/builder.py.
    """
    _validate_candidate(candidate)

    match_id = _resolve_match_id(candidate)
    match = _resolve_match(candidate)
    market = _resolve_market(candidate)
    selection_name = _resolve_selection(candidate)
    odds = _resolve_candidate_odds(candidate)
    confidence = _resolve_confidence(candidate)
    value_edge = _resolve_value_edge(candidate)

    # 'selection_name' is intentionally resolved for compatibility, but
    # Selection itself stores the market name in its 'market' field.
    #
    # The actual selected outcome remains represented by the market.
    selection = Selection(
        match_id=match_id,
        match=match,
        market=market,
        odds=odds,
        confidence=confidence,
        value_edge=value_edge,
    )

    selection.validate()

    return selection


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
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


def _rank_candidates_for_ticket(
    candidates: Sequence[dict],
    ticket_name: str,
    usage_counts: Dict[str, int] | None = None,
) -> List[dict]:
    """
    Rank candidates for a ticket.

    Candidates already used twice are excluded.

    A diversity penalty is applied when a match has already appeared in
    another ticket.
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

        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_score = (
            base_metric
            - (
                usage_count
                * DIVERSITY_PENALTY
            )
        )

        ranked.append(
            (
                adjusted_score,
                base_metric,
                candidate,
            )
        )

    ranked.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return [
        candidate
        for _, _, candidate in ranked
    ]


# ---------------------------------------------------------------------------
# Ticket builder
# ---------------------------------------------------------------------------

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build a single ticket.

    A ticket is not forced when fewer than three valid selections are
    available.
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

        # Never repeat the same match inside one ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

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


# ---------------------------------------------------------------------------
# Main smart portfolio builder
# ---------------------------------------------------------------------------

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the four-ticket smart portfolio.

    Stake allocation:
        SAFE       40%
        BALANCED   30%
        AGGRESSIVE 20%
        VALUE      10%

    Rules:
        - minimum 3 selections for a populated ticket
        - ticket-specific maximum selections
        - no duplicate match inside a ticket
        - maximum two ticket appearances per match
        - no forced ticket when insufficient candidates exist
        - input candidates are not mutated
    """
    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(candidates)

    # Copy dictionaries so that portfolio construction never mutates
    # the caller's candidate objects.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []

    # Tracks how many different tickets each match has entered.
    usage_counts: Dict[str, int] = {}

    for ticket_name in TICKET_ORDER:
        ranked_candidates = (
            _rank_candidates_for_ticket(
                available,
                ticket_name,
                usage_counts,
            )
        )

        ticket = _build_ticket(
            ticket_name,
            ranked_candidates,
        )

        if ticket is None:
            continue

        portfolio.append(ticket)

        for selection in ticket.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(
                    match_id,
                    0,
                )
                + 1
            )

    return portfolio


# ---------------------------------------------------------------------------
# Market portfolio entry point
# ---------------------------------------------------------------------------

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Public market-portfolio entry point.

    Kept separate as a named wrapper so both the older smart-portfolio
    interface and the newer market portfolio interface remain available.
    """
    return build_smart_portfolio(candidates)


# ---------------------------------------------------------------------------
# Additional compatibility alias
# ---------------------------------------------------------------------------

def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Backward-compatible generic portfolio builder.
    """
    return build_smart_portfolio(candidates)
