import unittest
from unittest.mock import patch

from data.api_football_client import (
    APIFootballClient,
    APIFootballError,
)


class TestAPIFootballClient(unittest.TestCase):

    def test_api_key_is_required(self):
        with patch.dict(
            "os.environ",
            {},
            clear=True,
        ):
            with self.assertRaises(ValueError):
                APIFootballClient()

    def test_api_key_can_come_from_environment(self):
        with patch.dict(
            "os.environ",
            {
                "API_FOOTBALL_KEY": "test-key",
            },
        ):
            client = APIFootballClient()

        self.assertEqual(
            client.api_key,
            "test-key",
        )

    @patch(
        "data.api_football_client.urlopen"
    )
    def test_fixtures_response_is_parsed(
        self,
        mock_urlopen,
    ):

        class FakeResponse:

            def __enter__(self):
                return self

            def __exit__(
                self,
                exc_type,
                exc_value,
                traceback,
            ):
                return False

            def read(self):
                return (
                    b'{"errors":[],"response":[]}'
                )

        mock_urlopen.return_value = (
            FakeResponse()
        )

        client = APIFootballClient(
            api_key="test-key"
        )

        result = client.get_fixtures(
            fixture_date=__import__(
                "datetime"
            ).date(
                2026,
                9,
                28,
            )
        )

        self.assertEqual(
            result,
            [],
        )

    @patch(
        "data.api_football_client.urlopen"
    )
    def test_api_errors_are_rejected(
        self,
        mock_urlopen,
    ):

        class FakeResponse:

            def __enter__(self):
                return self

            def __exit__(
                self,
                exc_type,
                exc_value,
                traceback,
            ):
                return False

            def read(self):
                return (
                    b'{"errors":{"token":"invalid"}}'
                )

        mock_urlopen.return_value = (
            FakeResponse()
        )

        client = APIFootballClient(
            api_key="test-key"
        )

        with self.assertRaises(
            APIFootballError
        ):
            client.get_fixtures(
                fixture_date=__import__(
                    "datetime"
                ).date(
                    2026,
                    9,
                    28,
                )
            )


if __name__ == "__main__":
    unittest.main()
