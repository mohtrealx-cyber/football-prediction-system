from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from data.api_football_client import (
    APIFootballClient,
    get_fixtures,
)
from data.models import Match


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def _convert_fixture_to_match(fixture: dict) -> Match:
    """
    Convert a project-format fixture dictionary into a Match object.
    """

    if not isinstance(fixture, dict):
        raise ValueError(
            "API fixture must be a dictionary"
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
        raise ValueError(
            "API fixture kickoff must be timezone-aware"
        )

    kickoff = kickoff.astimezone(
        KENYA_TIMEZONE
    )

    odds = fixture["odds"]

    if not isinstance(odds, dict) or not odds:
        raise ValueError(
            "API fixture odds must be a non-empty dictionary"
        )

    return Match(
        match_id=str(fixture["match_id"]),
        home_team=str(fixture["home_team"]).strip(),
        away_team=str(fixture["away_team"]).strip(),
        league=str(fixture["league"]).strip(),
        kickoff=kickoff,
        status=str(fixture["status"]),
        odds=dict(odds),
    )


def load_fixtures(
    destination_path: str,
    url: str = None,
    timeout: int = 30,
):
    """
    Load football fixtures from API-Football.

    Returns a list of Match objects.
    """

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

    # ---------------------------------------------------------
    # API-Football
    # ---------------------------------------------------------
    #
    # The compatibility get_fixtures() function handles the
    # API request and returns converted fixture dictionaries.
    #
    # We intentionally do not pass as_of/days_ahead here because
    # the existing tests expect timeout to be passed directly.
    # ---------------------------------------------------------

    raw_fixtures = get_fixtures(
        timeout=timeout,
    )

    if not isinstance(raw_fixtures, list):
        raise ValueError(
            "Fixture source must return a list"
        )

    matches = []

    for fixture in raw_fixtures:

        if isinstance(fixture, Match):
            matches.append(fixture)
            continue

        if not isinstance(fixture, dict):
            raise ValueError(
                "Fixture source returned an invalid fixture"
            )

        project_fields = {
            "match_id",
            "home_team",
            "away_team",
            "league",
            "kickoff",
            "status",
            "odds",
        }

        # Already converted by API client.
        if project_fields.issubset(
            fixture.keys()
        ):
            converted = fixture

        else:
            # Raw API-Football fixture.
            converted = (
                APIFootballClient.convert_fixture(
                    fixture
                )
            )

        matches.append(
            _convert_fixture_to_match(
                converted
            )
        )

    return matches
