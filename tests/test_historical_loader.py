import unittest
from unittest.mock import patch

from data.historical_loader import load_historical_matches


class TestHistoricalLoader(unittest.TestCase):

    @patch("data.historical_loader.HistoricalDataProvider")
    def test_loads_historical_matches(self, mock_provider):
        expected_matches = ["match1", "match2"]

        mock_instance = mock_provider.return_value
        mock_instance.get_matches.return_value = expected_matches

        result = load_historical_matches(
            csv_path="data/history.csv",
            league="Premier League",
        )

        self.assertEqual(result, expected_matches)

    @patch("data.historical_loader.HistoricalDataProvider")
    def test_passes_csv_path_and_league(self, mock_provider):
        load_historical_matches(
            csv_path="history.csv",
            league="Premier League",
        )

        mock_provider.assert_called_once_with(
            "history.csv",
            "Premier League",
        )

    @patch("data.historical_loader.HistoricalDataProvider")
    def test_provider_errors_are_propagated(self, mock_provider):
        mock_instance = mock_provider.return_value
        mock_instance.get_matches.side_effect = ValueError(
            "Invalid historical data"
        )

        with self.assertRaises(ValueError):
            load_historical_matches(
                csv_path="history.csv",
                league="Premier League",
            )


if __name__ == "__main__":
    unittest.main()
