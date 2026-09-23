import csv
from datetime import datetime
from zoneinfo import ZoneInfo

from data.models import Match


class FixtureDataProvider:
    """Load upcoming football fixtures from a Football-Data style CSV."""

    SOURCE_TIMEZONE = ZoneInfo("Europe/London")

    def __init__(self, csv_path: str):
        if not isinstance(csv_path, str) or not csv_path.strip():
            raise ValueError("csv_path must be a non-empty string")

        self.csv_path = csv_path

    def get_matches(self) -> list[Match]:
        matches = []

        with open(
            self.csv_path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                date_text = row.get("Date", "").strip()
                time_text = row.get("Time", "").strip()
                home_team = row.get("Home", "").strip()
                away_team = row.get("Away", "").strip()
                league = row.get("Div", "").strip()

                if not date_text:
                    raise ValueError(
                        f"Missing date on CSV row {row_number}"
                    )

                if not time_text:
                    raise ValueError(
                        f"Missing kickoff time on CSV row {row_number}"
                    )

                if not home_team or not away_team:
                    raise ValueError(
                        f"Missing team on CSV row {row_number}"
                    )

                if not league:
                    raise ValueError(
                        f"Missing league on CSV row {row_number}"
                    )

                kickoff = self._parse_kickoff(
                    date_text,
                    time_text,
                )

                odds = self._extract_odds(row)

                match_id = (
                    f"{league}-{date_text}-{time_text}-"
                    f"{home_team}-{away_team}"
                )

                matches.append(
                    Match(
                        match_id=match_id,
                        home_team=home_team,
                        away_team=away_team,
                        league=league,
                        kickoff=kickoff,
                        status="scheduled",
                        odds=odds,
                    )
                )

        return matches

    @classmethod
    def _parse_kickoff(
        cls,
        date_text: str,
        time_text: str,
    ) -> datetime:
        formats = (
            "%d/%m/%Y %H:%M",
            "%d/%m/%y %H:%M",
            "%Y-%m-%d %H:%M",
        )

        combined = f"{date_text} {time_text}"

        for date_format in formats:
            try:
                parsed = datetime.strptime(
                    combined,
                    date_format,
                )

                local_time = parsed.replace(
                    tzinfo=cls.SOURCE_TIMEZONE
                )

                return local_time
            except ValueError:
                continue

        raise ValueError(
            f"Unsupported kickoff format: {combined}"
        )

    @staticmethod
    def _extract_odds(row: dict) -> dict:
        odds = {}

        mappings = {
            "home_win": "1",
            "draw": "X",
            "away_win": "2",
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
            raise ValueError("No valid odds found for fixture")

        return odds
