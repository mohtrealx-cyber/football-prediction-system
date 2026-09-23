import os
import tempfile
import unittest

from data.football_data_provider import FootballDataProvider
from data.models import Match


class TestFootballDataProvider(unittest.TestCase):

    def _create_csv(self, content):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "matches.csv")

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

        return temp_dir, path

    def test_loads_matches_from_csv(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")
            matches = provider.get_matches()

            self.assertEqual(len(matches), 1)
            self.assertIsInstance(matches[0], Match)
        finally:
            temp_dir.cleanup()

    def test_match_data_is_loaded_correctly(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")
            match = provider.get_matches()[0]

            self.assertEqual(match.home_team, "Arsenal")
            self.assertEqual(match.away_team, "Chelsea")
            self.assertEqual(match.league, "Premier League")
            self.assertEqual(match.status, "finished")
        finally:
            temp_dir.cleanup()

    def test_odds_are_loaded_correctly(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")
            match = provider.get_matches()[0]

            self.assertEqual(match.odds["home_win"], 2.00)
            self.assertEqual(match.odds["draw"], 3.40)
            self.assertEqual(match.odds["away_win"], 3.80)
        finally:
            temp_dir.cleanup()

    def test_multiple_matches_are_loaded(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,2.00,3.40,3.80\n"
            "24/09/2026,Liverpool,Everton,1.70,3.60,5.00\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")
            matches = provider.get_matches()

            self.assertEqual(len(matches), 2)
        finally:
            temp_dir.cleanup()

    def test_missing_team_is_rejected(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_invalid_date_is_rejected(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "invalid,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_invalid_odds_are_rejected(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,invalid,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_empty_odds_are_rejected(self):
        content = (
            "Date,HomeTeam,AwayTeam,B365H,B365D,B365A\n"
            "23/09/2026,Arsenal,Chelsea,,,\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FootballDataProvider(path, "Premier League")

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
