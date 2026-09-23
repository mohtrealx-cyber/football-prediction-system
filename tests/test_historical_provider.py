import csv
import os
import tempfile
import unittest
from datetime import datetime, timezone

from data.historical_provider import HistoricalDataProvider
from data.historical_models import HistoricalMatch


class TestHistoricalDataProvider(unittest.TestCase):

    def create_csv(self, rows):
        file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            newline="",
            encoding="utf-8",
        )

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Date",
                "HomeTeam",
                "AwayTeam",
                "FTHG",
                "FTAG",
                "B365H",
                "B365D",
                "B365A",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)
        file.close()

        self.addCleanup(lambda: os.path.exists(file.name) and os.unlink(file.name))
        return file.name

    def test_loads_historical_match(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        matches = provider.get_matches()

        self.assertEqual(len(matches), 1)
        self.assertIsInstance(matches[0], HistoricalMatch)

    def test_match_data_is_loaded_correctly(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        match = provider.get_matches()[0]

        self.assertEqual(match.home_team, "Arsenal")
        self.assertEqual(match.away_team, "Chelsea")
        self.assertEqual(match.league, "Premier League")

    def test_final_score_is_loaded(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "3",
                "FTAG": "2",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        match = provider.get_matches()[0]

        self.assertEqual(match.home_goals, 3)
        self.assertEqual(match.away_goals, 2)

    def test_odds_are_loaded(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        match = provider.get_matches()[0]

        self.assertEqual(match.odds["home_win"], 2.00)
        self.assertEqual(match.odds["draw"], 3.40)
        self.assertEqual(match.odds["away_win"], 3.80)

    def test_kickoff_is_timezone_aware(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        match = provider.get_matches()[0]

        self.assertIsNotNone(match.kickoff.tzinfo)

    def test_missing_home_team_is_rejected(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")

        with self.assertRaises(ValueError):
            provider.get_matches()

    def test_missing_score_is_rejected(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")

        with self.assertRaises(ValueError):
            provider.get_matches()

    def test_invalid_score_is_rejected(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "abc",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            }
        ])

        provider = HistoricalDataProvider(path, "Premier League")

        with self.assertRaises(ValueError):
            provider.get_matches()

    def test_multiple_historical_matches_are_loaded(self):
        path = self.create_csv([
            {
                "Date": "20/09/2026",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "FTHG": "2",
                "FTAG": "1",
                "B365H": "2.00",
                "B365D": "3.40",
                "B365A": "3.80",
            },
            {
                "Date": "21/09/2026",
                "HomeTeam": "Liverpool",
                "AwayTeam": "Everton",
                "FTHG": "3",
                "FTAG": "0",
                "B365H": "1.50",
                "B365D": "4.00",
                "B365A": "6.00",
            },
        ])

        provider = HistoricalDataProvider(path, "Premier League")
        matches = provider.get_matches()

        self.assertEqual(len(matches), 2)


if __name__ == "__main__":
    unittest.main()
