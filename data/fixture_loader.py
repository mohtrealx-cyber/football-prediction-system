from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from data.api_football_client import get_fixtures
from data.models import Match


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def load_fixtures(
    destination_path: str | None = None,
    url: str | None = None,
    timeout: int = 30,
    as_of: datetime | None = None,
    days_ahead: int = 0,
) -> list[Match]:
    """
    Load football fixtures from API-Football and convert them
    into Match objects.

    destination_path and url are retained for backwards
    compatibility with the previous CSV-based loader.

    Fixtures are returned as Match objects.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

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

    if (
        not isinstance(days_ahead, int)
        or isinstance(days_ahead, bool)
        or days_ahead < 0
    ):
        raise ValueError(
            "days_ahead must be a non-negative integer"
        )

    # ---------------------------------------------------------
    # CURRENT TIME
    # ---------------------------------------------------------

    if as_of is None:
        as_of = datetime.now(
            KENYA_TIMEZONE
        )

    if (
        not isinstance(as_of, datetime)
        or as_of.tzinfo is None
        or as_of.utcoffset() is None
    ):
        raise ValueError(
            "as_of must be a timezone-aware datetime"
        )

    as_of = as_of.astimezone(
        KENYA_TIMEZONE
    )

    # ---------------------------------------------------------
    # API-FOOTBALL
    # ---------------------------------------------------------

    raw_fixtures = get_fixtures(
        as_of=as_of,
        days_ahead=days_ahead,
        timeout=timeout,
    )

    if raw_fixtures is None:
        return []

    if not isinstance(raw_fixtures, list):
        raise ValueError(
            "get_fixtures() must return a list"
        )

    # ---------------------------------------------------------
    # CONVERT API DICTS -> MATCH OBJECTS
    # ---------------------------------------------------------

    matches: list[Match] = []

    for fixture in raw_fixtures:

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
            required_fields - fixture.keys()
        )

        if missing_fields:
            raise ValueError(
                "API fixture is missing required fields: "
                f"{missing_fields}"
            )

        kickoff = fixture["kickoff"]

        if not isinstance(kickoff, datetime):
            raise ValueError(
                "Fixture kickoff must be a datetime"
            )

        if (
            kickoff.tzinfo is None
            or kickoff.utcoffset() is None
        ):
            raise ValueError(
                "Fixture kickoff must be timezone-aware"
            )

        kickoff = kickoff.astimezone(
            KENYA_TIMEZONE
        )

        odds = fixture["odds"]

        if not isinstance(odds, dict):
            raise ValueError(
                "Fixture odds must be a dictionary"
            )

        match = Match(
            match_id=str(
                fixture["match_id"]
            ),
            home_team=str(
                fixture["home_team"]
            ).strip(),
            away_team=str(
                fixture["away_team"]
            ).strip(),
            league=str(
                fixture["league"]
            ).strip(),
            kickoff=kickoff,
            status=str(
                fixture["status"]
            ),
            odds=odds,
        )

        matches.append(match)

    return matches
