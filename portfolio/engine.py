from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from tickets.builder import Selection, Ticket


# ============================================================================
# CONFIGURATION
# ============================================================================

TICKET_SPECS = {
    "SAFE": {
        "stake_percent": 40.0,
        "preferred_matches": 3,
        "max_matches": 4,
        "metric": "score",
        "threshold": 80.0,
    },
    "BALANCED": {
        "stake_percent": 30.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "score",
        "threshold": 70.0,
    },
    "AGGRESSIVE": {
        "stake_percent": 20.0,
        "preferred_matches": 5,
        "max_matches": 6,
        "metric": "score",
        "threshold": 60.0,
    },
    "VALUE": {
        "stake_percent": 10.0,
        "preferred_matches": 4,
        "max_matches": 5,
        "metric": "value_edge",
        "threshold": 5.0,
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
# LEGACY SMART-PORTFOLIO CANDIDATE CONTRACT
# ============================================================================

LEGACY_REQUIRED_FIELDS = (
    "match_id",
    "home_team",
    "away_team",
    "market",
    "odds",
    "score",
    "value_edge",
)


# ============================================================================
# MODERN MARKET-PORTFOLIO CANDIDATE CONTRACT
# ============================================================================

MARKET_REQUIRED_FIELDS = (
    "match_id",
    "market",
    "odds",
    "score",
    "value_edge",
)


# ============================================================================
# BASIC VALIDATION
# ============================================================================

def _validate_candidate_dict(candidate: Any) -> None:
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary")


def _validate_legacy_candidate(candidate: dict) -> None:
    """
    Validation for the original smart portfolio API.

    The original tests/callers expect home_team and away_team to exist.
    selection is intentionally NOT required because the old interface
    derived it from market.
    """
    _validate_candidate_dict(candidate)

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


def _validate_market_candidate(candidate: dict) -> None:
    """
    Validation for the newer market portfolio API.

    home_team and away_team are intentionally optional here because newer
    candidates may instead provide a ready-made 'match' field.
    """
    _validate_candidate_dict(candidate)

    missing = [
        field
        for field in MARKET_REQUIRED_FIELDS
        if field not in candidate
    ]

    if missing:
        raise ValueError(
            "candidate is missing required field(s): "
            + ", ".join(missing)
        )


def _validate_legacy_candidates(
    candidates: Sequence[dict],
) -> None:
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_legacy_candidate(candidate)


def _validate_market_candidates(
    candidates: Sequence[dict],
) -> None:
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    for candidate in candidates:
        _validate_market_candidate(candidate)


# ============================================================================
# NUMERIC HELPERS
# ============================================================================

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


# ============================================================================
# MATCH / MARKET / SELECTION RESOLUTION
# ============================================================================

def _resolve_match_id(candidate: dict) -> str:
    match_id = candidate.get("match_id")

    if match_id is None:
        raise ValueError("candidate match_id cannot be missing")

    match_id = str(match_id).strip()

    if not match_id:
        raise ValueError("candidate match_id cannot be empty")

    return match_id


def _resolve_match(candidate: dict) -> str:
    """
    Build the human-readable match string expected by Selection.

    Priority:
        1. existing 'match'
        2. home_team + away_team
        3. match_id
    """
    if "match" in candidate and candidate["match"] is not None:
        match = str(candidate["match"]).strip()

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


def _resolve_market(candidate: dict) -> str:
    market = candidate.get("market")

    if not isinstance(market, str):
        raise ValueError("candidate market must be a non-empty string")

    market = market.strip()

    if not market:
        raise ValueError("candidate market must be a non-empty string")

    return market


def _derive_selection_from_market(market: str) -> str:
    """
    Convert market identifiers into the legacy selection label.

    This is intentionally simple because Selection itself stores:
        match_id, match, market, odds, confidence, value_edge

    The extra candidate-level 'selection' field is not part of Selection.
    """
    normalized = market.strip().upper()

    mapping = {
        "HOME_WIN": "HOME",
        "HOME": "HOME",
        "1": "HOME",

        "DRAW": "DRAW",
        "X": "DRAW",

        "AWAY_WIN": "AWAY",
        "AWAY": "AWAY",
        "2": "AWAY",

        "OVER_2_5": "OVER_2_5",
        "OVER 2.5": "OVER_2_5",
        "O2.5": "OVER_2_5",

        "UNDER_2_5": "UNDER_2_5",
        "UNDER 2.5": "UNDER_2_5",
        "U2.5": "UNDER_2_5",

        "BTTS_YES": "BTTS_YES",
        "BTTS YES": "BTTS_YES",
        "BTTS": "BTTS_YES",

        "BTTS_NO": "BTTS_NO",
        "BTTS NO": "BTTS_NO",

        # Legacy double-chance naming.
        "1X": "1X",
        "X2": "X2",
        "12": "12",

        # Draw-no-bet style legacy labels.
        "DNB_HOME": "HOME",
        "DNB_AWAY": "AWAY",
    }

    return mapping.get(normalized, normalized)


def _resolve_selection(candidate: dict) -> str:
    """
    Resolve a candidate-level selection.

    New candidates may explicitly provide 'selection'.

    Old candidates do not. In that case it is safely derived from 'market'.
    """
    if "selection" in candidate:
        value = candidate["selection"]

        if value is not None:
            selection = str(value).strip()

            if selection:
                return selection

    return _derive_selection_from_market(
        _resolve_market(candidate)
    )


# ============================================================================
# ODDS RESOLUTION
# ============================================================================

def _resolve_candidate_odds(candidate: dict) -> float:
    """
    Resolve the numeric odds for the selected market.

    Supported inputs:

        "odds": 1.80

    or:

        "odds": {
            "home_win": 1.80,
            "draw": 3.50,
            "away_win": 4.50,
            ...
        }

    A numeric 'selected_odds' takes priority when provided.
    """

    # Newer daily pipeline provides selected_odds.
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
        odds = _safe_float(raw_odds, "odds")

        if odds <= 1.0:
            raise ValueError(
                "odds must be greater than 1.0"
            )

        return odds

    # Dictionary odds.
    market = _resolve_market(candidate)

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

    normalized_market = market.upper()

    aliases = {
        "HOME_WIN": ("HOME", "1"),
        "DRAW": ("DRAW", "X"),
        "AWAY_WIN": ("AWAY", "2"),
        "OVER_2_5": ("OVER_2_5", "OVER 2.5"),
        "UNDER_2_5": ("UNDER_2_5", "UNDER 2.5"),
        "BTTS_YES": ("BTTS_YES", "BTTS YES"),
        "BTTS_NO": ("BTTS_NO", "BTTS NO"),
        "1X": ("1X",),
        "X2": ("X2",),
        "12": ("12",),
    }

    found = None

    for alias in aliases.get(normalized_market, ()):
        if alias in raw_odds:
            found = raw_odds[alias]
            break

    # Try candidate-level selection as a fallback lookup key.
    if found is None and "selection" in candidate:
        selection = candidate["selection"]

        if selection in raw_odds:
            found = raw_odds[selection]

    if found is None:
        raise ValueError(
            f"no odds found for market: {market}"
        )

    odds = _safe_float(found, "odds")

    if odds <= 1.0:
        raise ValueError(
            "odds must be greater than 1.0"
        )

    return odds


# ============================================================================
# CONFIDENCE / VALUE EDGE
# ============================================================================

def _resolve_confidence(candidate: dict) -> float:
    """
    Resolve the confidence required by tickets.builder.Selection.

    Priority:
        1. explicit confidence
        2. model_probability * 100
        3. score
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

    # Selection.validate() requires 0 <= confidence <= 100.
    confidence = max(
        0.0,
        min(100.0, confidence),
    )

    return confidence


def _resolve_value_edge(candidate: dict) -> float:
    value_edge = _safe_float(
        candidate["value_edge"],
        "value_edge",
    )

    if value_edge < 0:
        raise ValueError(
            "value_edge cannot be negative"
        )

    return value_edge


# ============================================================================
# CANDIDATE -> SELECTION
# ============================================================================

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert either legacy or modern candidate data into the exact Selection
    constructor defined in tickets/builder.py.
    """
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

    selection.validate()

    return selection


# ============================================================================
# RANKING
# ============================================================================

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
    Rank candidates for a specific ticket.

    Candidates below the ticket threshold are excluded.

    A match already used once receives a diversity penalty.

    A match used MAX_MATCH_USAGE times is excluded.
    """
    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    usage_counts = usage_counts or {}

    spec = TICKET_SPECS[ticket_name]
    metric = spec["metric"]
    threshold = spec["threshold"]

    ranked = []

    for candidate in candidates:
        _validate_market_candidate(candidate)

        match_id = _resolve_match_id(candidate)

        current_usage = usage_counts.get(
            match_id,
            0,
        )

        if current_usage >= MAX_MATCH_USAGE:
            continue

        metric_value = _candidate_metric(
            candidate,
            metric,
        )

        # Do not include candidates below the ticket's quality threshold.
        if metric_value < threshold:
            continue

        adjusted_score = (
            metric_value
            - (
                current_usage
                * DIVERSITY_PENALTY
            )
        )

        ranked.append(
            (
                adjusted_score,
                metric_value,
                match_id,
                candidate,
            )
        )

    # Highest adjusted score first.
    # match_id is included as a deterministic tie-breaker.
    ranked.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        ),
        reverse=True,
    )

    return [
        item[3]
        for item in ranked
    ]


# ============================================================================
# TICKET BUILDING
# ============================================================================

def _build_ticket(
    ticket_name: str,
    candidates: Sequence[dict],
) -> Ticket | None:
    """
    Build a single ticket.

    A ticket is not forced when fewer than three qualifying selections exist.
    """
    if ticket_name not in TICKET_SPECS:
        raise ValueError(
            f"unsupported ticket: {ticket_name}"
        )

    spec = TICKET_SPECS[ticket_name]

    selections: List[Selection] = []
    seen_match_ids = set()

    for candidate in candidates:
        match_id = _resolve_match_id(candidate)

        # No duplicate match inside one ticket.
        if match_id in seen_match_ids:
            continue

        selection = _candidate_to_selection(
            candidate
        )

        selections.append(selection)
        seen_match_ids.add(match_id)

        if len(selections) >= spec["max_matches"]:
            break

    # Never force a weak/incomplete ticket.
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
    candidates: Sequence[dict],
) -> List[Ticket]:
    """
    Shared portfolio construction logic used by both public APIs.
    """
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a list")

    if not candidates:
        return []

    # Never mutate the caller's input.
    available = [
        dict(candidate)
        for candidate in candidates
    ]

    portfolio: List[Ticket] = []
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

        if ticket is None:
            continue

        portfolio.append(ticket)

        for selection in ticket.selections:
            match_id = selection.match_id

            usage_counts[match_id] = (
                usage_counts.get(match_id, 0) + 1
            )

    return portfolio


# ============================================================================
# LEGACY SMART PORTFOLIO API
# ============================================================================

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Original V1 portfolio API.

    This keeps the original candidate contract expected by
    tests/test_portfolio.py.

    IMPORTANT:
    The old candidate format does NOT require a candidate-level
    'selection' field. It derives selection information from 'market'.
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    if not candidates:
        return []

    _validate_legacy_candidates(candidates)

    return _build_portfolio(candidates)


# ============================================================================
# MODERN MARKET PORTFOLIO API
# ============================================================================

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Newer market-aware portfolio API.

    Supports both:
        - old numeric odds
        - newer dictionary odds
        - optional candidate-level selection
        - optional model_probability
        - optional precomputed confidence
        - optional match string
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    if not candidates:
        return []

    _validate_market_candidates(candidates)

    return _build_portfolio(candidates)


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================

def build_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Generic compatibility entry point.

    Historically this function referred to the smart portfolio builder.
    """
    return build_smart_portfolio(candidates)
