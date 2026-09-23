from datetime import datetime

from data.models import Match


def filter_fixtures_by_time(
    matches: list[Match],
    start: datetime,
    end: datetime,
) -> list[Match]:
    """
    Return scheduled matches whose kickoff falls
    within the inclusive start/end time window.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    if not isinstance(start, datetime):
        raise TypeError("start must be a datetime")

    if not isinstance(end, datetime):
        raise TypeError("end must be a datetime")

    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start and end must be timezone-aware")

    if end < start:
        raise ValueError("end must not be earlier than start")

    filtered = []

    for match in matches:
        if not isinstance(match, Match):
            raise TypeError("matches must contain Match objects")

        if match.status != "scheduled":
            continue

        if start <= match.kickoff <= end:
            filtered.append(match)

    return filtered
