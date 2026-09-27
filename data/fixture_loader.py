from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from data.api_football_client import get_fixtures
from data.models import Match


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def _convert_fixture_to_match(fixture) -> Match:
    """
    Convert one API fixture into a Match object.

    Supports both:
    1. Already-normalized fixture dictionaries returned by
       data.api_football_client.
    2. Match objects, which are returned by some tests/mocks.
    """

    if isinstance(fixture, Match):
        return fixture

    if not isinstance(fixture, dict):
        raise TypeError(
            "API fixture must be a dictionary or Match object"
        )

    required_fields = {
        "match_id",
        "home_team",
        "away_team",
        "league",
        "kickoff",
        "status",
        "odds",
    }

    missing_fields = sorted(
        field
        for field in required_fields
        if field not in fixture
    )

    if missing_fields:
        raise ValueError(
            "API fixture is missing required fields: "
            f"{missing_fields}"
        )

    kickoff = fixture["kickoff"]

    if not isinstance(kickoff, datetime):
        raise ValueError(
            "API fixture kickoff must be a datetime"
        )

    if kickoff.tzinfo is None or kickoff.utcoffset() is None:
        kickoff = kickoff.replace(
            tzinfo=KENYA_TIMEZONE
        )
    else:
        kickoff = kickoff.astimezone(
            KENYA_TIMEZONE
        )

    return Match(
        match_id=str(fixture["match_id"]),
        home_team=str(fixture["home_team"]).strip(),
        away_team=str(fixture["away_team"]).strip(),
        league=str(fixture["league"]).strip(),
        kickoff=kickoff,
        status=str(fixture["status"]),
        odds=dict(fixture["odds"]),
    )


def load_fixtures(
    destination_path: str | None = None,
    url: str | None = None,
    timeout: int = 30,
):
    """
    Load football fixtures from API-Football.

    The old implementation downloaded a Football-Data CSV.
    The system now uses API-Football as the live fixture source.

    destination_path and url are retained for compatibility with
    older callers/tests. They are not required by the API loader.
    """

    if destination_path is not None:
        if not isinstance(destination_path, str):
            raise TypeError(
                "destination_path must be a string"
            )

        if not destination_path.strip():
            raise ValueError(
                "destination_path must be a non-empty string"
            )

    if url is not None:
        if not isinstance(url, str):
            raise TypeError(
                "url must be a string"
            )

        if not url.strip():
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

    # IMPORTANT:
    # Keep this call simple because the existing test suite expects
    # get_fixtures(timeout=...) to be called this way.
    raw_fixtures = get_fixtures(
        timeout=timeout,
    )

    matches = []

    for fixture in raw_fixtures:
        matches.append(
            _convert_fixture_to_match(fixture)
        )

    return matches
