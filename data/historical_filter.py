from datetime import datetime

from data.historical_models import HistoricalMatch


def filter_matches_before(
    matches: list[HistoricalMatch],
    cutoff: datetime,
) -> list[HistoricalMatch]:
    """Return historical matches that occurred before the cutoff."""

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    if not isinstance(cutoff, datetime):
        raise TypeError("cutoff must be a datetime")

    if cutoff.tzinfo is None:
        raise ValueError("cutoff must be timezone-aware")

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

    return [
        match
        for match in matches
        if match.kickoff < cutoff
    ]
