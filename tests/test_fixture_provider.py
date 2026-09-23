import os
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from data.fixture_provider import FixtureDataProvider
from data.models import Match


class TestFixtureDataProvider(unittest.TestCase):

    def _create_csv(self, content):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

        return temp_dir, path

    def test_loads_upcoming_fixture(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)
            matches = provider.get_matches()

            self.assertEqual(len(matches), 1)
            self.assertIsInstance(matches[0], Match)
        finally:
            temp_dir.cleanup()

    def test_fixture_has_correct_match_data(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)
            match = provider.get_matches()[0]

            self.assertEqual(match.home_team, "Arsenal")
            self.assertEqual(match.away_team, "Chelsea")
            self.assertEqual(match.league, "E0")
            self.assertEqual(match.status, "scheduled")
        finally:
            temp_dir.cleanup()

    def test_fixture_odds_are_loaded(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)
            match = provider.get_matches()[0]

            self.assertEqual(match.odds["home_win"], 2.00)
            self.assertEqual(match.odds["draw"], 3.40)
            self.assertEqual(match.odds["away_win"], 3.80)
        finally:
            temp_dir.cleanup()

    def test_kickoff_uses_london_timezone(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)
            match = provider.get_matches()[0]

            self.assertEqual(
                match.kickoff,
                datetime(
                    2026,
                    9,
                    23,
                    20,
                    0,
                    tzinfo=ZoneInfo("Europe/London"),
                ),
            )
        finally:
            temp_dir.cleanup()

    def test_multiple_fixtures_are_loaded(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
            "E0,24/09/2026,19:30,Liverpool,Everton,1.70,3.60,5.00\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)
            matches = provider.get_matches()

            self.assertEqual(len(matches), 2)
        finally:
            temp_dir.cleanup()

    def test_missing_date_is_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_missing_time_is_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_missing_team_is_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_missing_league_is_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            ",23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_invalid_kickoff_is_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,invalid,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_invalid_odds_are_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,invalid,3.40,3.80\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()

    def test_empty_odds_are_rejected(self):
        content = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,,,\n"
        )

        temp_dir, path = self._create_csv(content)

        try:
            provider = FixtureDataProvider(path)

            with self.assertRaises(ValueError):
                provider.get_matches()
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
