from __future__ import annotations

from typing import Any

from tickets.builder import Selection, Ticket


# ============================================================
# PORTFOLIO CONFIGURATION
# ============================================================

# Production portfolio:
#
# IRONCLAD   = 40%
# BALANCED   = 30%
# VOLATILITY = 20%
# BENCHMARK  = 10%
#
# Legacy tests/projects:
#
# SAFE       = 40%
# BALANCED   = 30%
# AGGRESSIVE = 20%
# VALUE      = 10%
#
# The engine supports both schemas.
TICKET_SPECS = (
    ("IRONCLAD", 40.0),
    ("BALANCED", 30.0),
    ("VOLATILITY", 20.0),
    ("BENCHMARK", 10.0),
)

LEGACY_TICKET_SPECS = (
    ("SAFE", 40.0),
    ("BALANCED", 30.0),
    ("AGGRESSIVE", 20.0),
    ("VALUE", 10.0),
)

MIN_SELECTIONS = 3
MAX_SELECTIONS = 6

MAX_MATCH_REUSE = 2


# ============================================================
# PORTFOLIO RULES
# ============================================================

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

    # Legacy compatibility
    "SAFE": {
        "metric": "confidence",
        "threshold": 70.0,
    },
    "AGGRESSIVE": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
    "VALUE": {
        "metric": "value_edge",
        "threshold": 5.0,
    },
}


# ============================================================
# CANDIDATE NORMALIZATION
# ============================================================

def _is_legacy_candidate(candidate: dict) -> bool:
    """
    Detect the older candidate schema.

    Legacy candidates normally contain:
        odds

    Production candidates contain:
        selected_odds
        selection
    """

    return (
        "selected_odds" not in candidate
        and "selection" not in candidate
    )


def _get_selected_odds(candidate: dict) -> float:
    """
    Return the odds used by the selected market.

    Production:
        selected_odds

    Legacy:
        odds
    """

    if "selected_odds" in candidate:
        value = candidate["selected_odds"]

    else:
        value = candidate.get("odds")

    if not isinstance(value, (int, float)):
        raise TypeError(
            "candidate odds must be numeric"
        )

    if value <= 1.0:
        raise ValueError(
            "candidate selected_odds must be greater than 1.0"
        )

    return float(value)


def _get_selection_name(candidate: dict) -> str:
    """
    Get the market/selection name.

    Production candidates use `selection`.

    Legacy tests use `market`.
    """

    if "selection" in candidate:
        value = candidate["selection"]
    else:
        value = candidate.get("market")

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "candidate selection/market must be a non-empty string"
        )

    return value.strip()


def _validate_candidate(candidate: Any) -> None:
    """
    Validate one market candidate.

    The required logical fields are:

        match_id
        home_team
        away_team
        market/selection
        odds/selected_odds
        model_probability
        value_edge

    Both the legacy and production schemas are supported.
    """

    if not isinstance(candidate, dict):
        raise TypeError(
            "each candidate must be a dictionary"
        )

    required = {
        "match_id",
        "home_team",
        "away_team",
        "model_probability",
        "value_edge",
    }

    missing = required - candidate.keys()

    if missing:
        raise ValueError(
            "candidate missing required fields: "
            f"{sorted(missing)}"
        )

    if (
        "market" not in candidate
        and "selection" not in candidate
    ):
        raise ValueError(
            "candidate missing required field: market"
        )

    if (
        "odds" not in candidate
        and "selected_odds" not in candidate
    ):
        raise ValueError(
            "candidate missing required odds field"
        )

    match_id = candidate["match_id"]

    if (
        not isinstance(match_id, str)
        or not match_id.strip()
    ):
        raise ValueError(
            "candidate match_id must be a non-empty string"
        )

    home_team = candidate["home_team"]

    if (
        not isinstance(home_team, str)
        or not home_team.strip()
    ):
        raise ValueError(
            "candidate home_team must be a non-empty string"
        )

    away_team = candidate["away_team"]

    if (
        not isinstance(away_team, str)
        or not away_team.strip()
    ):
        raise ValueError(
            "candidate away_team must be a non-empty string"
        )

    _get_selection_name(candidate)

    _get_selected_odds(candidate)

    probability = candidate["model_probability"]

    if not isinstance(
        probability,
        (int, float),
    ):
        raise TypeError(
            "candidate model_probability must be numeric"
        )

    if not 0.0 <= float(probability) <= 1.0:
        raise ValueError(
            "candidate model_probability must be between 0 and 1"
        )

    value_edge = candidate["value_edge"]

    if not isinstance(
        value_edge,
        (int, float),
    ):
        raise TypeError(
            "candidate value_edge must be numeric"
        )

    if float(value_edge) < 0.0:
        raise ValueError(
            "candidate value_edge cannot be negative"
        )


def _validate_candidates(
    candidates: list[dict],
) -> None:
    """Validate the complete candidate collection."""

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    for candidate in candidates:
        _validate_candidate(candidate)


# ============================================================
# CONVERSION
# ============================================================

def _candidate_to_selection(
    candidate: dict,
) -> Selection:
    """
    Convert a market candidate into a Ticket Selection.
    """

    return Selection(
        match_id=str(
            candidate["match_id"]
        ),
        match=(
            f"{candidate['home_team']} "
            f"vs "
            f"{candidate['away_team']}"
        ),
        market=_get_selection_name(candidate),
        odds=_get_selected_odds(candidate),
        confidence=float(
            candidate["model_probability"]
        ) * 100.0,
        value_edge=float(
            candidate["value_edge"]
        ),
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
    """

    if metric == "confidence":
        return sorted(
            candidates,
            key=lambda item: (
                float(
                    item["model_probability"]
                ),
                float(
                    item["value_edge"]
                ),
                _get_selected_odds(item),
                float(
                    item.get("score", 0.0)
                ),
            ),
            reverse=True,
        )

    if metric == "value_edge":
        return sorted(
            candidates,
            key=lambda item: (
                float(
                    item["value_edge"]
                ),
                float(
                    item["model_probability"]
                ),
                _get_selected_odds(item),
                float(
                    item.get("score", 0.0)
                ),
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
    """
    Return candidates satisfying a ticket rule.
    """

    if metric == "confidence":
        return [
            candidate
            for candidate in candidates
            if (
                float(
                    candidate["model_probability"]
                ) * 100.0
                >= threshold
            )
        ]

    if metric == "value_edge":
        return [
            candidate
            for candidate in candidates
            if float(
                candidate["value_edge"]
            ) >= threshold
        ]

    raise ValueError(
        f"Unsupported portfolio metric: {metric}"
    )


# ============================================================
# MATCH REUSE CONTROL
# ============================================================

def _select_unique_matches(
    candidates: list[dict],
    maximum: int,
    global_usage: dict[str, int] | None = None,
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Select candidates with:

    1. No duplicate match inside one ticket.
    2. A maximum global reuse of two tickets.
    3. Optional blocked matches.

    This is important because a match can have several markets,
    but the same fixture should not dominate the portfolio.
    """

    if global_usage is None:
        global_usage = {}

    if blocked_matches is None:
        blocked_matches = set()

    selected: list[dict] = []
    used_inside_ticket: set[str] = set()

    for candidate in candidates:

        match_id = str(
            candidate["match_id"]
        )

        # Never duplicate a fixture inside one ticket.
        if match_id in used_inside_ticket:
            continue

        # Respect explicit blocking.
        if match_id in blocked_matches:
            continue

        # Global maximum: two tickets.
        if (
            global_usage.get(
                match_id,
                0,
            )
            >= MAX_MATCH_REUSE
        ):
            continue

        selected.append(candidate)

        used_inside_ticket.add(
            match_id
        )

        global_usage[match_id] = (
            global_usage.get(
                match_id,
                0,
            )
            + 1
        )

        if len(selected) >= maximum:
            break

    return selected


# ============================================================
# TICKET FILL
# ============================================================

def _fill_ticket(
    selected: list[dict],
    fallback_candidates: list[dict],
    maximum: int,
    global_usage: dict[str, int],
    blocked_matches: set[str] | None = None,
) -> list[dict]:
    """
    Controlled fallback.

    We can relax the ticket threshold when necessary, but we
    still enforce:

        - no duplicate match in one ticket
        - maximum two-ticket reuse
        - blocked matches
    """

    if blocked_matches is None:
        blocked_matches = set()

    selected_ids = {
        str(
            candidate["match_id"]
        )
        for candidate in selected
    }

    for candidate in fallback_candidates:

        match_id = str(
            candidate["match_id"]
        )

        if match_id in selected_ids:
            continue

        if match_id in blocked_matches:
            continue

        if (
            global_usage.get(
                match_id,
                0,
            )
            >= MAX_MATCH_REUSE
        ):
            continue

        selected.append(candidate)

        selected_ids.add(match_id)

        global_usage[match_id] = (
            global_usage.get(
                match_id,
                0,
            )
            + 1
        )

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
    global_usage: dict[str, int],
    blocked_matches: set[str] | None = None,
) -> Ticket | None:
    """
    Build one ticket.
    """

    if blocked_matches is None:
        blocked_matches = set()

    rules = TICKET_RULES[name]

    eligible = _eligible_candidates(
        candidates=candidates,
        metric=rules["metric"],
        threshold=rules["threshold"],
    )

    eligible = _sort_candidates(
        candidates=eligible,
        metric=rules["metric"],
    )

    selected = _select_unique_matches(
        candidates=eligible,
        maximum=MAX_SELECTIONS,
        global_usage=global_usage,
        blocked_matches=blocked_matches,
    )

    # Controlled fallback.
    if len(selected) < MIN_SELECTIONS:

        fallback = _sort_candidates(
            candidates=candidates,
            metric=rules["metric"],
        )

        selected = _fill_ticket(
            selected=selected,
            fallback_candidates=fallback,
            maximum=MAX_SELECTIONS,
            global_usage=global_usage,
            blocked_matches=blocked_matches,
        )

    if len(selected) < MIN_SELECTIONS:
        return None

    selections = [
        _candidate_to_selection(candidate)
        for candidate in selected
    ]

    ticket = Ticket(
        name=name,
        stake_percent=float(
            stake_percent
        ),
        selections=selections,
    )

    return ticket


# ============================================================
# DUPLICATE CANDIDATE REMOVAL
# ============================================================

def _deduplicate_candidates(
    candidates: list[dict],
) -> list[dict]:
    """
    Remove exact duplicate market candidates.

    Different markets for the same fixture are retained because
    the portfolio may legitimately evaluate them separately.
    """

    unique_candidates: list[dict] = []

    seen: set[tuple[str, str]] = set()

    for candidate in candidates:

        key = (
            str(
                candidate["match_id"]
            ),
            _get_selection_name(
                candidate
            ),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_candidates.append(
            candidate
        )

    return unique_candidates


# ============================================================
# PORTFOLIO BUILDING
# ============================================================

def _build_portfolio(
    candidates: list[dict],
    ticket_specs: tuple[
        tuple[str, float],
        ...,
    ],
) -> list[Ticket]:
    """
    Internal portfolio builder.

    Every fixture may appear at most twice across the complete
    four-ticket portfolio.
    """

    if not candidates:
        return []

    candidates = _deduplicate_candidates(
        candidates
    )

    ordered = sorted(
        candidates,
        key=lambda item: (
            float(
                item.get(
                    "score",
                    0.0,
                )
            ),
            float(
                item["model_probability"]
            ),
            float(
                item["value_edge"]
            ),
            _get_selected_odds(item),
        ),
        reverse=True,
    )

    tickets: list[Ticket] = []

    global_usage: dict[str, int] = {}

    # The first ticket gets first access to the strongest
    # candidates.
    #
    # For production we also protect the largest allocation
    # from excessive overlap with BENCHMARK.
    first_ticket_name = ticket_specs[0][0]

    first_ticket = _build_ticket(
        name=first_ticket_name,
        stake_percent=ticket_specs[0][1],
        candidates=ordered,
        global_usage=global_usage,
    )

    if first_ticket is None:
        return []

    tickets.append(first_ticket)

    first_ticket_matches = {
        selection.match_id
        for selection in first_ticket.selections
    }

    # --------------------------------------------------------
    # Remaining tickets
    # --------------------------------------------------------

    for index, (
        name,
        stake_percent,
    ) in enumerate(
        ticket_specs[1:],
        start=1,
    ):

        blocked: set[str] = set()

        # Keep the largest and final benchmark portfolio
        # separated.
        if index == len(ticket_specs) - 1:
            blocked = set(
                first_ticket_matches
            )

        ticket = _build_ticket(
            name=name,
            stake_percent=stake_percent,
            candidates=ordered,
            global_usage=global_usage,
            blocked_matches=blocked,
        )

        if ticket is None:
            return []

        tickets.append(ticket)

    # --------------------------------------------------------
    # Validate final portfolio
    # --------------------------------------------------------

    if len(tickets) != 4:
        return []

    total_stake = round(
        sum(
            ticket.stake_percent
            for ticket in tickets
        ),
        6,
    )

    if total_stake != 100.0:
        raise AssertionError(
            "Portfolio stake allocation "
            "must equal 100%"
        )

    # No duplicate fixture within a ticket.
    for ticket in tickets:

        match_ids = [
            selection.match_id
            for selection in ticket.selections
        ]

        if (
            len(match_ids)
            != len(set(match_ids))
        ):
            raise AssertionError(
                f"{ticket.name} contains "
                "duplicate matches"
            )

        if not (
            MIN_SELECTIONS
            <= len(ticket.selections)
            <= MAX_SELECTIONS
        ):
            raise AssertionError(
                f"{ticket.name} must contain "
                f"{MIN_SELECTIONS}-"
                f"{MAX_SELECTIONS} selections"
            )

    # Global maximum reuse = 2.
    usage: dict[str, int] = {}

    for ticket in tickets:

        for selection in ticket.selections:

            usage[
                selection.match_id
            ] = (
                usage.get(
                    selection.match_id,
                    0,
                )
                + 1
            )

    for match_id, count in usage.items():

        if count > MAX_MATCH_REUSE:
            raise AssertionError(
                f"Match {match_id} appears "
                f"in {count} tickets; "
                f"maximum is "
                f"{MAX_MATCH_REUSE}"
            )

    return tickets


# ============================================================
# PUBLIC API
# ============================================================

def build_market_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Build the production four-ticket portfolio.

    Production allocation:

        IRONCLAD    40%
        BALANCED    30%
        VOLATILITY  20%
        BENCHMARK   10%

    The same match may appear in at most two tickets.
    """

    if not isinstance(candidates, list):
        raise TypeError(
            "candidates must be a list"
        )

    if not candidates:
        return []

    _validate_candidates(
        candidates
    )

    # Real production candidates have selected_odds and
    # selection. Legacy tests have odds and market.
    legacy_mode = any(
        _is_legacy_candidate(candidate)
        for candidate in candidates
    )

    if legacy_mode:
        return _build_portfolio(
            candidates=candidates,
            ticket_specs=LEGACY_TICKET_SPECS,
        )

    return _build_portfolio(
        candidates=candidates,
        ticket_specs=TICKET_SPECS,
    )


def build_smart_portfolio(
    candidates: list[dict],
) -> list[Ticket]:
    """
    Backward-compatible public API.

    Older tests and modules import:

        build_smart_portfolio

    Keep this function as an alias to the same portfolio engine.
    """

    return build_market_portfolio(
        candidates
    )


# ============================================================
# OPTIONAL VALIDATION HELPER
# ============================================================

def validate_portfolio(
    tickets: list[Ticket],
) -> None:
    """
    Validate a completed portfolio.

    This function intentionally supports both naming schemes:

        Production:
            IRONCLAD / BALANCED / VOLATILITY / BENCHMARK

        Legacy:
            SAFE / BALANCED / AGGRESSIVE / VALUE
    """

    if not isinstance(tickets, list):
        raise TypeError(
            "tickets must be a list"
        )

    if len(tickets) != 4:
        raise ValueError(
            "portfolio must contain exactly "
            "four tickets"
        )

    names = [
        ticket.name
        for ticket in tickets
    ]

    production_names = {
        "IRONCLAD",
        "BALANCED",
        "VOLATILITY",
        "BENCHMARK",
    }

    legacy_names = {
        "SAFE",
        "BALANCED",
        "AGGRESSIVE",
        "VALUE",
    }

    if set(names) not in (
        production_names,
        legacy_names,
    ):
        raise ValueError(
            "portfolio contains an unsupported "
            "ticket naming scheme"
        )

    total_stake = round(
        sum(
            ticket.stake_percent
            for ticket in tickets
        ),
        6,
    )

    if total_stake != 100.0:
        raise ValueError(
            "portfolio stake allocation must "
            "equal 100%"
        )

    usage: dict[str, int] = {}

    for ticket in tickets:

        if not (
            MIN_SELECTIONS
            <= len(ticket.selections)
            <= MAX_SELECTIONS
        ):
            raise ValueError(
                f"{ticket.name} must contain "
                f"{MIN_SELECTIONS}-"
                f"{MAX_SELECTIONS} selections"
            )

        inside_ticket: set[str] = set()

        for selection in ticket.selections:

            if (
                selection.match_id
                in inside_ticket
            ):
                raise ValueError(
                    f"{ticket.name} contains "
                    f"duplicate match "
                    f"{selection.match_id}"
                )

            inside_ticket.add(
                selection.match_id
            )

            usage[
                selection.match_id
            ] = (
                usage.get(
                    selection.match_id,
                    0,
                )
                + 1
            )

    for match_id, count in usage.items():

        if count > MAX_MATCH_REUSE:
            raise ValueError(
                f"match {match_id} appears "
                f"in {count} tickets; "
                f"maximum is "
                f"{MAX_MATCH_REUSE}"
            )
