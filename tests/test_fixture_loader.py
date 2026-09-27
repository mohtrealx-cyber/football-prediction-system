import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from data.fixture_loader import load_fixtures
from data.models import Match


class TestFixtureLoader(unittest.TestCase):

    def _api_fixture(
        self,
        fixture_id=12345,
        home="Arsenal",
        away="Chelsea",
        league="Premier League",
        kickoff="2026-09-28T19:00:00+00:00",
        status="NS",
    ):
        return {
            "fixture": {
                "id": fixture_id,
                "date": kickoff,
                "status": {
                    "short": status,
                },
            },
            "league": {
                "name": league,
            },
            "teams": {
                "home": {
                    "name": home,
                },
                "away": {
                    "name": away,
                },
            },
        }

    @patch("data.fixture_loader.get_fixtures")
    def test_loads_fixtures_from_api(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture(
                fixture_id=1001,
                home="Arsenal",
                away="Chelsea",
            ),
            self._api_fixture(
                fixture_id=1002,
                home="Liverpool",
                away="Everton",
            ),
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        self.assertEqual(
            len(matches),
            2,
        )

        self.assertIsInstance(
            matches[0],
            Match,
        )

        self.assertEqual(
            matches[0].match_id,
            "1001",
        )

        self.assertEqual(
            matches[0].home_team,
            "Arsenal",
        )

        self.assertEqual(
            matches[0].away_team,
            "Chelsea",
        )

        self.assertEqual(
            matches[1].home_team,
            "Liverpool",
        )

        self.assertEqual(
            matches[1].away_team,
            "Everton",
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_api_timeout_is_passed_to_client(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = []

        load_fixtures(
            destination_path="fixtures.csv",
            timeout=15,
        )

        mock_get_fixtures.assert_called_once_with(
            timeout=15,
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_api_error_is_propagated(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.side_effect = RuntimeError(
            "API request failed"
        )

        with self.assertRaises(RuntimeError):
            load_fixtures(
                destination_path="fixtures.csv",
            )

    def test_destination_path_must_be_string(self):
        with self.assertRaises(TypeError):
            load_fixtures(
                destination_path=None,
            )

    def test_destination_path_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            load_fixtures(
                destination_path="",
            )

    def test_timeout_must_be_positive(self):
        with self.assertRaises(ValueError):
            load_fixtures(
                destination_path="fixtures.csv",
                timeout=0,
            )

    @patch("data.fixture_loader.get_fixtures")
    def test_scheduled_fixture_status(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture(
                status="NS",
            )
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        self.assertEqual(
            matches[0].status,
            "scheduled",
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_live_fixture_status(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture(
                status="1H",
            )
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        self.assertEqual(
            matches[0].status,
            "live",
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_finished_fixture_status(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture(
                status="FT",
            )
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        self.assertEqual(
            matches[0].status,
            "finished",
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_kickoff_is_converted_to_nairobi_time(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture(
                kickoff="2026-09-28T19:00:00+00:00",
            )
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        expected = datetime(
            2026,
            9,
            28,
            22,
            0,
            tzinfo=ZoneInfo(
                "Africa/Nairobi"
            ),
        )

        self.assertEqual(
            matches[0].kickoff,
            expected,
        )

    @patch("data.fixture_loader.get_fixtures")
    def test_fixture_odds_exist(
        self,
        mock_get_fixtures,
    ):
        mock_get_fixtures.return_value = [
            self._api_fixture()
        ]

        matches = load_fixtures(
            destination_path="fixtures.csv",
        )

        self.assertIn(
            "home_win",
            matches[0].odds,
        )

        self.assertIn(
            "draw",
            matches[0].odds,
        )

        self.assertIn(
            "away_win",
            matches[0].odds,
        )


if __name__ == "__main__":
    unittest.main()
