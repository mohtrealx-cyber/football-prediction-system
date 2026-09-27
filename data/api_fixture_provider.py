from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from data.api_football_client import (
    APIFootballClient,
    PREMIER_LEAGUE_ID,
)
from data.models import Match


NAIROBI_TIMEZONE = ZoneInfo("Africa/Nairobi")


class APIFixtureProvider:
    """
    Convert API-Football fixtures into the project's Match model.
    """

    def __init__(
        self,
        client: APIFootballClient | None = None,
    ):
        self.client = client or APIFootballClient()

    def get_matches(
        self,
        fixture_date=None,
    ) -> list[Match]:

        if fixture_date is None:
            now = datetime.now(
                NAIROBI_TIMEZONE
            )
            fixture_date = now.date()

        fixtures = self.client.get_fixtures(
            fixture_date=fixture_date,
            league_id=PREMIER_LEAGUE_ID,
        )

        matches = []

        for fixture in fixtures:
            match = self._convert_fixture(
                fixture
            )

            if match is not None:
                matches.append(match)

        return matches

    @staticmethod
    def _convert_fixture(
        fixture: dict,
    ) -> Match | None:

        fixture_data = fixture.get(
            "fixture",
            {},
        )

        teams = fixture.get(
            "teams",
            {},
        )

        league = fixture.get(
            "league",
            {},
        )

        fixture_id = fixture_data.get("id")

        home = (
            teams.get("home", {})
            .get("name")
        )

        away = (
            teams.get("away", {})
            .get("name")
        )

        league_name = league.get(
            "name"
        )

        kickoff_text = fixture_data.get(
            "date"
        )

        status_short = (
            fixture_data
            .get("status", {})
            .get("short")
        )

        if not fixture_id:
            return None

        if not home or not away:
            return None

        if not league_name:
            return None

        if not kickoff_text:
            return None

        try:
            kickoff = datetime.fromisoformat(
                kickoff_text.replace(
                    "Z",
                    "+00:00",
                )
            )

            kickoff = kickoff.astimezone(
                NAIROBI_TIMEZONE
            )

        except ValueError:
            return None

        status = APIFixtureProvider._map_status(
            status_short
        )

        # API-Football's fixture endpoint does
        # not guarantee betting odds.
        #
        # We initially create a safe placeholder
        # only for fixtures that will later receive
        # actual odds from the odds endpoint.
        odds = {}

        return Match(
            match_id=str(fixture_id),
            home_team=home,
            away_team=away,
            league=league_name,
            kickoff=kickoff,
            status=status,
            odds=odds,
        )

    @staticmethod
    def _map_status(
        status: str | None,
    ) -> str:

        if status in {
            "NS",
            "TBD",
            "PST",
            "CANC",
        }:
            return "scheduled"

        if status in {
            "1H",
            "HT",
            "2H",
            "ET",
            "BT",
            "P",
            "LIVE",
        }:
            return "live"

        return "finished"
