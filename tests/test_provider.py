import inspect
import unittest
from datetime import datetime, timezone

from data.models import Match
from data.provider import DataProvider


class FakeProvider:
    """Simple provider used to test the interface."""

    def get_matches(self) -> list[Match]:
        return [
            Match(
                match_id="TEST-001",
                home_team="Team A",
                away_team="Team B",
                league="Test League",
                kickoff=datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc),
                status="scheduled",
                odds={
                    "home_win": 2.0,
                    "draw": 3.2,
                    "away_win": 3.5,
                },
            )
        ]


class TestDataProvider(unittest.TestCase):

    def test_provider_has_get_matches_method(self):
        self.assertTrue(hasattr(DataProvider, "get_matches"))

    def test_get_matches_has_expected_return_annotation(self):
        method = DataProvider.get_matches
        signature = inspect.signature(method)

        self.assertEqual(
            signature.return_annotation,
            list[Match],
        )

    def test_fake_provider_returns_match_list(self):
        provider = FakeProvider()

        matches = provider.get_matches()

        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 1)
        self.assertIsInstance(matches[0], Match)


if __name__ == "__main__":
    unittest.main()
