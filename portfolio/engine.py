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
# CANDIDATE REQUIREMENTS
# ============================================================================

# This is the ORIGINAL / LEGACY portfolio candidate interface.
#
# IMPORTANT:
# "selection" is intentionally NOT required here.
#
# Older portfolio tests and callers provide:
#   match_id
#   market
#   odds
#   score
#   value_edge
#
# The Selection dataclass receives:
#   match_id
#   match
#   market
#   odds
#   confidence
#   value_edge
#
# So "selection" does not belong in the required legacy candidate schema.
LEGACY_REQUIRED_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


# Newer market candidates may contain "selection", but it is optional for
# compatibility because the actual Selection object does not have such a
# constructor field.
MARKET_OPTIONAL_FIELDS = (
    "selection",
    "selected_odds",
    "model_probability",
    "probability",
    "confidence",
    "match",
    "home_team",
    "away_team",
)


# ============================================================================
# BASIC VALIDATION
# ============================================================================

def _validate_candidate(
    candidate: dict,
    *,
    require_selection: bool = False,
) -> None:
    """
    Validate a portfolio candidate.

    Legacy portfolio candidates do NOT require "selection".

    A market-specific caller may explicitly request selection validation by
    passing require_selection=True.
    """
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")

    missing = [
        field
        for field in LEGACY_REQUIRED_FIELDS
        if field not in candidate
    ]

    if missing:
        raise ValueError(
            "candidate is missing required field(s): "
            + ", ".join(missing)
        )

    if require_selection:
        selection = candidate.get("selection")

        if not isinstance(selection, str) or not selection.strip():
            raise ValueError(
                "candidate selection must be a non-empty string"
            )


def _validate_candidates(
    candidates: Sequence[dict],
    *,
    require_selection: bool = False,
) -> None:
    """
    Validate a collection of candidates.
    """
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_candidate(
            candidate,
            require_selection=require_selection,
        )


def _safe_float(
    value: Any,
    field_name: str,
) -> float:
    """
    Convert a value to a finite float.
    """
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
    """
    Resolve the match ID.
    """
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
    """
    Resolve the market name.
    """
    market = candidate.get("market")

    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            "candidate market must be a non-empty string"
        )

    return market.strip()


def _resolve_selection_label(candidate: dict) -> str:
    """
    Resolve the actual selection label when one exists.

    This is used only as compatibility metadata/ranking information.

    The Selection dataclass itself does not have a "selection" field.
    """
    selection = candidate.get("selection")

    if isinstance(selection, str) and selection.strip():
        return selection.strip()

    # Common market -> selection fallback.
    market = candidate.get("market")

    market_selection_map = {
        "home_win": "HOME",
        "draw": "DRAW",
        "away_win": "AWAY",
        "over_2_5": "OVER_2_5",
        "under_2_5": "UNDER_2_5",
        "btts_yes": "BTTS_YES",
        "btts_no": "BTTS_NO",
    }

    if isinstance(market, str):
        normalized = market.strip().lower()

        if normalized in market_selection_map:
            return market_selection_map[normalized]

        # Legacy market naming.
        legacy_map = {
            "1": "HOME",
            "x": "DRAW",
            "2": "AWAY",
            "1x": "1X",
            "12": "12",
            "x2": "X2",
        }

        if normalized in legacy_map:
            return legacy_map[normalized]

    # Selection is not part of the Selection dataclass, so an empty value is
    # perfectly acceptable for legacy candidates.
    return ""


def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the final numeric odds price.

    Supported forms:

        odds = 1.80

    or:

        odds = {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    "selected_odds" is preferred when supplied.
    """

    # ------------------------------------------------------------
    # 1. Explicit selected odds
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # 2. Normal odds field
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # 3. Dictionary odds
    # ------------------------------------------------------------
    market = _resolve_market(candidate)

    # Exact market name first.
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
            "OVER 2.5 GOALS",
        ),
        "under_2_5": (
            "UNDER_2_5",
            "UNDER 2.5",
            "UNDER 2.5 GOALS",
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

    for alias in aliases.get(
        market,
        (),
    ):
        if alias in raw_odds:
            found_value = raw_odds[alias]
            break

    # Legacy selection lookup.
    if found_value is None:
        selection = candidate.get("selection")

        if selection in raw_odds:
            found_value = raw_odds[selection]

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


def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve Selection.confidence.

    Priority:
        1. explicit confidence
        2. model_probability * 100
        3. probability * 100
        4. score

    The Selection dataclass requires confidence between 0 and 100.
    """

    # Explicit confidence.
    if "confidence" in candidate:
        value = _safe_float(
            candidate["confidence"],
            "confidence",
        )

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )

    # model_probability in decimal form.
    if "model_probability" in candidate:
        value = (
            _safe_float(
                candidate["model_probability"],
                "model_probability",
            )
            * 100.0
        )

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )

    # probability in decimal form.
    if "probability" in candidate:
        value = (
            _safe_float(
                candidate["probability"],
                "probability",
            )
            * 100.0
        )

        return max(
            0.0,
            min(
                100.0,
                value,
            ),
        )

    # Legacy candidate score fallback.
    value = _safe_float(
        candidate["score"],
        "score",
    )

    return max(
        0.0,
        min(
            100.0,
            value,
        ),
    )


def _resolve_value_edge(candidate: dict) -> float:
    """
    Resolve Selection.value_edge.
    """
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    # Selection.validate() rejects negative value_edge.
    if value_edge < 0.0:
        value_edge = 0.0

    return value_edge


def _resolve_match(candidate: dict) -> str:
    """
    Resolve the human-readable match name.

    Supported formats:

        candidate["match"]

    or:

        candidate["home_team"]
        candidate["away_team"]

    or:

        candidate["match_id"]
    """

    # Existing explicit match.
    direct_match = candidate.get("match")

    if direct_match is not None:
        match = str(direct_match).strip()

        if match:
            return match

    # Home/Away pair.
    home_team = candidate.get("home_team")
    away_team = candidate.get("away_team")

    if (
        home_team is not None
        and away_team is not None
    ):
        home = str(home_team).strip()
        away = str(away_team).strip()

        if home and away:
            return f"{home} vs {away}"

    # Final fallback.
    return _resolve_match_id(candidate)


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a portfolio candidate into the exact Selection structure used by
    tickets/builder.py.

    Selection fields are ONLY:

        match_id
        match
        market
        odds
        confidence
        value_edge
    """

    _validate_candidate(candidate)

    match_id = _resolve_match_id(candidate)
    match = _resolve_match(candidate)
    market = _resolve_market(candidate)
    odds = _resolve_candidate_odds(candidate)
    confidence = _resolve_confidence(candidate)
    value_edge = _resolve_value_edge(candidate)

    selection = Selection(
        match_id=match_id,
        match=match,
        market=market,
        odds=odds,
        confidence=confidence,
        value_edge=value_edge,
    )

    # Use the validation already defined by Selection.
    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

def _candidate_metric(
    candidate: dict,
    metric: str,
) -> float:
    """
    Return the ranking metric for a candidate.
    """
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
    Rank candidates for a specific ticket.

    A candidate already used once receives a diversity penalty.

    A candidate already used MAX_MATCH_USAGE times is excluded.
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

        # Hard cap.
        if usage_count >= MAX_MATCH_USAGE:
            continue

        base_metric = _candidate_metric(
            candidate,
            metric,
        )

        adjusted_metric = (
            base_metric
            - (
                usage_count
                * DIVERSITY_PENALTY
            )
        )

        ranked.append(
            (
                adjusted_metric,
                base_metric,
                candidate,
            )
        )

    # Highest adjusted metric first.
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


# ============================================================================
# TICKET BUILDING
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build one ticket.

    Returns None when fewer than three valid selections are available.

    Weak/insufficient tickets are therefore not forced.
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

    # Do not force a ticket below the minimum.
    if len(selections) < MIN_SELECTIONS:
        return None

    return Ticket(
        name=ticket_name,
        stake_percent=spec["stake_percent"],
        selections=selections,
    )


# ============================================================================
# INTERNAL PORTFOLIO BUILDER
# ============================================================================

def _build_portfolio(
    candidates: List[dict],
    *,
    require_selection: bool = False,
) -> List[Ticket]:
    """
    Shared implementation for the legacy and newer portfolio entry points.
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(
        candidates,
        require_selection=require_selection,
    )

    # Never mutate the caller's input.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []
    usage_counts: Dict[str, int] = {}

    # Build tickets in the defined priority/order.
    for ticket_name in TICKET_ORDER:
        ranked = _rank_candidates_for_ticket(
            available,
            ticket_name,
            usage_counts,
        )

        ticket = _build_ticket(
            ticket_name,
            ranked,
        )

        # No forcing.
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


# ============================================================================
# ORIGINAL / LEGACY API
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Original V1 smart portfolio entry point.

    IMPORTANT:
    This function intentionally accepts the original candidate format,
    where "selection" is NOT required.
    """
    return _build_portfolio(
        candidates,
        require_selection=False,
    )


# ============================================================================
# MARKET PORTFOLIO API
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Market-aware portfolio entry point.

    New market candidates normally include "selection", but the conversion
    layer remains compatible with the original candidate format.
    """
    return _build_portfolio(
        candidates,
        require_selection=False,
    )


# ============================================================================
# BACKWARD-COMPATIBLE WRAPPER
# ============================================================================

def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Generic compatibility wrapper.
    """
    return build_smart_portfolio(candidates)
