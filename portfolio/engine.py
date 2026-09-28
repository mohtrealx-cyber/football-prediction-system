from __future__ import annotations

from typing import List

from tickets.builder import Selection, Ticket


# ---------------------------------------------------------------------------
# Current four-ticket portfolio specification
# ---------------------------------------------------------------------------

TICKET_SPECS = (
    ("IRONCLAD", 40.0),
    ("BALANCED", 30.0),
    ("VOLATILITY", 20.0),
    ("BENCHMARK", 10.0),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _candidate_to_selection(candidate: dict) -> Selection:
    """
    Convert a market candidate dictionary into a Selection object.
    """

    if not isinstance(candidate, dict):
        raise TypeError(
            "candidate must be a dictionary"
        )

    required_fields = (
        "match_id",
        "home_team",
        "away_team",
        "market",
        "selected_odds",
        "model_probability",
        "value_edge",
    )

    missing = [
        field
        for field in required_fields
        if field not in candidate
    ]

    if missing:
        raise ValueError(
            "Candidate is missing required fields: "
            f"{missing}"
        )

    match_id = str(
        candidate["match_id"]
    )

    home_team = str(
        candidate["home_team"]
    )

    away_team = str(
        candidate["away_team"]
    )

    market = str(
        candidate.get(
            "selection",
            candidate["market"],
        )
    )

    odds = float(
        candidate["selected_odds"]
    )

    confidence = float(
        candidate["model_probability"]
    ) * 100.0

    value_edge = float(
        candidate["value_edge"]
    )

    selection = Selection(
        match_id=match_id,
        match=(
            f"{home_team} vs {away_team}"
        ),
        market=market,
        odds=odds,
        confidence=confidence,
        value_edge=max(
            value_edge,
            0.0,
        ),
    )

    selection.validate()

    return selection


def _deduplicate_candidates(
    candidates: List[dict],
) -> List[dict]:
    """
    Remove duplicate market candidates.

    A match may contain several markets, so the uniqueness key is:

        match_id + market

    This allows different markets from the same match while preventing
    the exact same market from being added repeatedly.
    """

    seen = set()
    result = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        key = (
            candidate.get("match_id"),
            candidate.get("market"),
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(candidate)

    return result


def _qualified_candidates(
    candidates: List[dict],
) -> List[dict]:
    """
    Keep only explicitly qualified candidates.
    """

    return [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("qualified") is True
    ]


def _sort_by_score(
    candidates: List[dict],
) -> List[dict]:
    """
    Sort candidates from strongest to weakest score.
    """

    return sorted(
        candidates,
        key=lambda candidate: (
            -float(
                candidate.get(
                    "score",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "value_edge",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "model_probability",
                    0.0,
                )
            ),
        ),
    )


def _select_unique_matches(
    candidates: List[dict],
    maximum: int,
    used_match_ids: set[str] | None = None,
) -> List[dict]:
    """
    Select candidates while ensuring that a match is not repeated
    inside the same ticket.

    used_match_ids can additionally prevent a match from being reused
    across tickets when required.
    """

    if used_match_ids is None:
        used_match_ids = set()

    selected = []
    local_matches = set()

    for candidate in candidates:

        match_id = candidate.get(
            "match_id"
        )

        if not match_id:
            continue

        if match_id in local_matches:
            continue

        if match_id in used_match_ids:
            continue

        selected.append(candidate)

        local_matches.add(match_id)

        if len(selected) >= maximum:
            break

    return selected


def _make_ticket(
    name: str,
    stake_percent: float,
    candidates: List[dict],
) -> Ticket:
    """
    Convert candidates into a Ticket.
    """

    selections = [
        _candidate_to_selection(
            candidate
        )
        for candidate in candidates
    ]

    return Ticket(
        name=name,
        stake_percent=stake_percent,
        selections=selections,
    )


# ---------------------------------------------------------------------------
# Current market-aware portfolio builder
# ---------------------------------------------------------------------------

def build_market_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Build the current four-ticket market portfolio.

    Ticket allocation:

        IRONCLAD  = 40%
        BALANCED  = 30%
        VOLATILITY = 20%
        BENCHMARK = 10%

    The function expects already-qualified market candidates.

    The builder does not lower the value-edge requirement and does not
    manufacture selections when insufficient candidates exist.
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    qualified = _qualified_candidates(
        candidates
    )

    qualified = _deduplicate_candidates(
        qualified
    )

    qualified = _sort_by_score(
        qualified
    )

    if not qualified:
        return []

    tickets: List[Ticket] = []

    # ------------------------------------------------------------------
    # IRONCLAD
    # Safest/highest-confidence selections.
    # ------------------------------------------------------------------

    ironclad_candidates = sorted(
        qualified,
        key=lambda candidate: (
            -float(
                candidate.get(
                    "model_probability",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "score",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "value_edge",
                    0.0,
                )
            ),
        ),
    )

    ironclad = _select_unique_matches(
        ironclad_candidates,
        maximum=4,
    )

    if len(ironclad) >= 3:
        tickets.append(
            _make_ticket(
                "IRONCLAD",
                40.0,
                ironclad,
            )
        )

    # ------------------------------------------------------------------
    # BALANCED
    # Strong candidates with good value.
    # ------------------------------------------------------------------

    balanced_candidates = sorted(
        qualified,
        key=lambda candidate: (
            -float(
                candidate.get(
                    "score",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "value_edge",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "model_probability",
                    0.0,
                )
            ),
        ),
    )

    balanced = _select_unique_matches(
        balanced_candidates,
        maximum=5,
    )

    if len(balanced) >= 3:
        tickets.append(
            _make_ticket(
                "BALANCED",
                30.0,
                balanced,
            )
        )

    # ------------------------------------------------------------------
    # VOLATILITY
    # Higher-value candidates.
    # ------------------------------------------------------------------

    volatility_candidates = sorted(
        qualified,
        key=lambda candidate: (
            -float(
                candidate.get(
                    "value_edge",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "score",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "selected_odds",
                    0.0,
                )
            ),
        ),
    )

    volatility = _select_unique_matches(
        volatility_candidates,
        maximum=6,
    )

    if len(volatility) >= 3:
        tickets.append(
            _make_ticket(
                "VOLATILITY",
                20.0,
                volatility,
            )
        )

    # ------------------------------------------------------------------
    # BENCHMARK
    #
    # This ticket is intentionally independent of the first three
    # tickets where possible. It acts as the benchmark portfolio.
    # ------------------------------------------------------------------

    benchmark_candidates = sorted(
        qualified,
        key=lambda candidate: (
            -float(
                candidate.get(
                    "score",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "selected_odds",
                    0.0,
                )
            ),
            -float(
                candidate.get(
                    "value_edge",
                    0.0,
                )
            ),
        ),
    )

    benchmark = _select_unique_matches(
        benchmark_candidates,
        maximum=6,
    )

    if len(benchmark) >= 3:
        tickets.append(
            _make_ticket(
                "BENCHMARK",
                10.0,
                benchmark,
            )
        )

    return tickets


# ---------------------------------------------------------------------------
# Backward-compatible legacy entry point
# ---------------------------------------------------------------------------

def build_smart_portfolio(
    candidates: List[dict],
) -> List[Ticket]:
    """
    Backward-compatible alias for older tests and modules.

    The project previously exposed build_smart_portfolio().
    The current architecture uses build_market_portfolio().

    Keeping this wrapper prevents older callers from breaking while
    ensuring they receive the current four-ticket portfolio model.
    """

    return build_market_portfolio(
        candidates
    )
