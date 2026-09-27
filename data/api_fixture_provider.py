from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from data.api_football_client import (
    APIFootballClient,
    PREMIER_LEAGUE_ID,
)
from data.models import Match


NAIROBI_TIMEZONE = ZoneInfo("Africa/Nairobi")


class APIFixtureProvider:
    """
    Convert API-Football fixtures and odds into Match objects.
    """

    def __init__(
        self,
        client: APIFootballClient | None = None,
    ):
        self.client = client or APIFootballClient()

    def get_matches(
        self,
        fixture_date: date | None = None,
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

        matches: list[Match] = []

        for fixture in fixtures:

            match = self._convert_fixture(
                fixture
            )

            if match is not None:
                matches.append(match)

        return matches

    def _convert_fixture(
        self,
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

        league_name = league.get("name")

        kickoff_text = fixture_data.get("date")

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

        status = self._map_status(
            status_short
        )

        # We only want scheduled matches.
        if status != "scheduled":
            return None

        odds_response = self.client.get_fixture_odds(
            int(fixture_id)
        )

        odds = self._extract_odds(
            odds_response
        )

        # A Match without odds cannot enter
        # the live prediction pipeline.
        if not odds:
            return None

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
    def _extract_odds(
        odds_response: list[dict],
    ) -> dict[str, float]:

        odds: dict[str, float] = {}

        for bookmaker_block in odds_response:

            bookmakers = bookmaker_block.get(
                "bookmakers",
                [],
            )

            if not isinstance(
                bookmakers,
                list,
            ):
                continue

            for bookmaker in bookmakers:

                bets = bookmaker.get(
                    "bets",
                    [],
                )

                if not isinstance(
                    bets,
                    list,
                ):
                    continue

                for bet in bets:

                    bet_name = (
                        str(
                            bet.get("name", "")
                        )
                        .strip()
                        .lower()
                    )

                    values = bet.get(
                        "values",
                        [],
                    )

                    if not isinstance(
                        values,
                        list,
                    ):
                        continue

                    for value in values:

                        if not isinstance(
                            value,
                            dict,
                        ):
                            continue

                        selection = (
                            str(
                                value.get(
                                    "value",
                                    "",
                                )
                            )
                            .strip()
                            .lower()
                        )

                        odd_text = value.get(
                            "odd"
                        )

                        try:
                            odd = float(
                                odd_text
                            )
                        except (
                            TypeError,
                            ValueError,
                        ):
                            continue

                        if odd <= 1.0:
                            continue

                        # Match Winner
                        if (
                            bet_name
                            == "match winner"
                        ):
                            if selection == "home":
                                odds.setdefault(
                                    "home_win",
                                    odd,
                                )

                            elif selection == "draw":
                                odds.setdefault(
                                    "draw",
                                    odd,
                                )

                            elif selection == "away":
                                odds.setdefault(
                                    "away_win",
                                    odd,
                                )

                        # Over / Under
                        elif (
                            "goals over/under"
                            in bet_name
                            or "over/under"
                            in bet_name
                        ):
                            if selection == "over 2.5":
                                odds.setdefault(
                                    "over_2_5",
                                    odd,
                                )

                            elif selection == "under 2.5":
                                odds.setdefault(
                                    "under_2_5",
                                    odd,
                                )

                        # Both Teams To Score
                        elif (
                            bet_name
                            == "both teams score"
                        ):
                            if selection == "yes":
                                odds.setdefault(
                                    "btts_yes",
                                    odd,
                                )

                            elif selection == "no":
                                odds.setdefault(
                                    "btts_no",
                                    odd,
                                )

        return odds

    @staticmethod
    def _map_status(
        status: str | None,
    ) -> str:

        if status in {
            "NS",
            "TBD",
            "PST",
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
