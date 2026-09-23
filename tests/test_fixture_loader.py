import os
import tempfile
import unittest
from unittest.mock import patch

from data.fixture_loader import load_fixtures
from data.models import Match


class TestFixtureLoader(unittest.TestCase):

    def test_download_and_load_fixtures(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        csv_data = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
            "E0,24/09/2026,19:30,Liverpool,Everton,1.70,3.60,5.00\n"
        )

        def fake_download(destination_path, **kwargs):
            with open(destination_path, "w", encoding="utf-8") as file:
                file.write(csv_data)

            return destination_path

        with patch(
            "data.fixture_loader.download_fixtures",
            side_effect=fake_download,
        ):
            matches = load_fixtures(path)

        try:
            self.assertEqual(len(matches), 2)
            self.assertIsInstance(matches[0], Match)
            self.assertEqual(matches[0].home_team, "Arsenal")
            self.assertEqual(matches[0].away_team, "Chelsea")
            self.assertEqual(matches[1].home_team, "Liverpool")
            self.assertEqual(matches[1].away_team, "Everton")
        finally:
            temp_dir.cleanup()

    def test_custom_url_is_passed_to_downloader(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        csv_data = (
            "Div,Date,Time,Home,Away,1,X,2\n"
            "E0,23/09/2026,20:00,Arsenal,Chelsea,2.00,3.40,3.80\n"
        )

        def fake_download(destination_path, url=None, timeout=30):
            self.assertEqual(url, "https://example.com/fixtures.csv")
            self.assertEqual(timeout, 15)

            with open(destination_path, "w", encoding="utf-8") as file:
                file.write(csv_data)

            return destination_path

        with patch(
            "data.fixture_loader.download_fixtures",
            side_effect=fake_download,
        ):
            matches = load_fixtures(
                path,
                url="https://example.com/fixtures.csv",
                timeout=15,
            )

        try:
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].home_team, "Arsenal")
        finally:
            temp_dir.cleanup()

    def test_download_error_is_propagated(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        with patch(
            "data.fixture_loader.download_fixtures",
            side_effect=RuntimeError("Download failed"),
        ):
            with self.assertRaises(RuntimeError):
                load_fixtures(path)

        temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
