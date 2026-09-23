import csv
from datetime import datetime, timezone

from data.historical_models import HistoricalMatch


class HistoricalDataProvider:
    """Load completed football matches from a historical CSV file."""

    def __init__(self, csv_path: str, league: str):
        if not isinstance(csv_path, str) or not csv_path.strip():
            raise ValueError("csv_path must be a non-empty string")

        if not isinstance(league, str) or not league.strip():
            raise ValueError("league must be a non-empty string")

        self.csv_path = csv_path
        self.league = league

    def get_matches(self) -> list[HistoricalMatch]:
        matches = []

        with open(
            self.csv_path,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                home_team = row.get("HomeTeam", "").strip()
                away_team = row.get("AwayTeam", "").strip()
                date_text = row.get("Date", "").strip()
                home_goals_text = row.get("FTHG", "").strip()
                away_goals_text = row.get("FTAG", "").strip()

                if not home_team:
                    raise ValueError(
                        f"Missing home team on CSV row {row_number}"
                    )

                if not away_team:
                    raise ValueError(
                        f"Missing away team on CSV row {row_number}"
                    )

                if not date_text:
                    raise ValueError(
                        f"Missing date on CSV row {row_number}"
                    )

                if not home_goals_text or not away_goals_text:
                    raise ValueError(
                        f"Missing final score on CSV row {row_number}"
                    )

                kickoff = self._parse_date(date_text)

                try:
                    home_goals = int(home_goals_text)
                    away_goals = int(away_goals_text)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid final score on CSV row {row_number}"
                    ) from exc

                odds = self._extract_odds(row)

                match_id = (
                    f"{self.league}-{date_text}-"
                    f"{home_team}-{away_team}"
                )

                matches.append(
                    HistoricalMatch(
                        match_id=match_id,
                        home_team=home_team,
                        away_team=away_team,
                        league=self.league,
                        kickoff=kickoff,
                        home_goals=home_goals,
                        away_goals=away_goals,
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
            except ValueError as exc:
                raise ValueError(
                    f"Invalid odds value for {column}: {value}"
                ) from exc

        return odds
