import csv
from datetime import datetime, timezone

from data.models import Match


class FootballDataProvider:
    """Load football matches from a Football-Data style CSV file."""

    def __init__(self, csv_path: str, league: str):
        if not isinstance(csv_path, str) or not csv_path.strip():
            raise ValueError("csv_path must be a non-empty string")

        if not isinstance(league, str) or not league.strip():
            raise ValueError("league must be a non-empty string")

        self.csv_path = csv_path
        self.league = league

    def get_matches(self) -> list[Match]:
        matches = []

        with open(self.csv_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                home_team = row.get("HomeTeam", "").strip()
                away_team = row.get("AwayTeam", "").strip()
                date_text = row.get("Date", "").strip()

                if not home_team or not away_team or not date_text:
                    raise ValueError(
                        f"Missing required match data on CSV row {row_number}"
                    )

                kickoff = self._parse_date(date_text)

                match_id = (
                    f"{self.league}-{date_text}-"
                    f"{home_team}-{away_team}"
                )

                odds = self._extract_odds(row)

                matches.append(
                    Match(
                        match_id=match_id,
                        home_team=home_team,
                        away_team=away_team,
                        league=self.league,
                        kickoff=kickoff,
                        status="finished",
                        odds=odds,
                    )
                )

        return matches

    @staticmethod
    def _parse_date(date_text: str) -> datetime:
        formats = (
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y-%m-%d",
        )

        for date_format in formats:
            try:
                parsed = datetime.strptime(date_text, date_format)
                return parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        raise ValueError(f"Unsupported date format: {date_text}")

    @staticmethod
    def _extract_odds(row: dict) -> dict:
        odds = {}

        mappings = {
            "home_win": "B365H",
            "draw": "B365D",
            "away_win": "B365A",
        }

        for market, column in mappings.items():
            value = row.get(column, "")

            if value is None or not value.strip():
                continue

            try:
                odds[market] = float(value)
            except ValueError:
                raise ValueError(
                    f"Invalid odds value for {column}: {value}"
                )

        if not odds:
            raise ValueError("No valid odds found for match")

        return odds
