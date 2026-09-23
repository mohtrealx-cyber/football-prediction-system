import os
import tempfile
import unittest
from unittest.mock import patch

from data.football_data_client import download_fixtures


class TestFootballDataClient(unittest.TestCase):

    def test_downloads_file_successfully(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        fake_data = b"Date,Home,Away\n23/09/2026,Team A,Team B\n"

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return fake_data

        with patch(
            "data.football_data_client.urlopen",
            return_value=FakeResponse(),
        ):
            result = download_fixtures(path)

        try:
            self.assertEqual(result, path)
            self.assertTrue(os.path.exists(path))

            with open(path, "rb") as file:
                self.assertEqual(file.read(), fake_data)
        finally:
            temp_dir.cleanup()

    def test_empty_download_is_rejected(self):
        temp_dir = tempfile.TemporaryDirectory()
        path = os.path.join(temp_dir.name, "fixtures.csv")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return b""

        with patch(
            "data.football_data_client.urlopen",
            return_value=FakeResponse(),
        ):
            with self.assertRaises(ValueError):
                download_fixtures(path)

        temp_dir.cleanup()

    def test_destination_path_must_be_string(self):
        with self.assertRaises(TypeError):
            download_fixtures(None)

    def test_destination_path_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            download_fixtures("")

    def test_url_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            download_fixtures(
                "fixtures.csv",
                url="",
            )

    def test_timeout_must_be_positive(self):
        with self.assertRaises(ValueError):
            download_fixtures(
                "fixtures.csv",
                timeout=0,
            )


if __name__ == "__main__":
    unittest.main()
