from __future__ import annotations

from datetime import datetime

from data.api_football_client import get_fixtures
from data.models import Match


def load_fixtures(
    destination_path: str,
    url: str | None = None,
    timeout: int = 30,
):
    """
    Load football fixtures from API-Football and convert them
    into Match objects.

    The API-Football client is now the primary fixture source.
    The legacy CSV URL argument is retained for compatibility
    with existing callers/tests.

    The Free API-Football plan currently supports the current
    date, so days_ahead is intentionally set to 0.
    """

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if url is not None and (
        not isinstance(url, str)
        or not url.strip()
    ):
        raise ValueError(
            "url must be a non-empty string"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

    # API-Football is now the live fixture source.
    #
    # days_ahead=0 is intentional because the current
    # API-Football Free plan only permits the supported
    # date window.
    raw_fixtures = get_fixtures(
        as_of=datetime.now().astimezone(),
        days_ahead=0,
        timeout=timeout,
    )

    matches = []

    for fixture in raw_fixtures:
        match = Match(
            match_id=str(
                fixture["match_id"]
            ),
            home_team=fixture["home_team"],
            away_team=fixture["away_team"],
            league=fixture["league"],
            kickoff=fixture["kickoff"],
            status=fixture["status"],
            odds=fixture["odds"],
        )

        match.validate()
        matches.append(match)

    return matches
