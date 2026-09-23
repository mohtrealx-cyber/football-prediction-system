from urllib.request import Request, urlopen


FIXTURES_URL = (
    "https://www.football-data.co.uk/"
    "matches/resources/fixtures.csv"
)


def download_fixtures(
    destination_path: str,
    url: str = FIXTURES_URL,
    timeout: int = 30,
) -> str:
    """Download the Football-Data fixtures CSV to a local file."""

    if not isinstance(destination_path, str):
        raise TypeError("destination_path must be a string")

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    request = Request(
        url,
        headers={
            "User-Agent": "football-prediction-system/1.0"
        },
    )

    with urlopen(request, timeout=timeout) as response:
        data = response.read()

    if not data:
        raise ValueError("Downloaded fixture file is empty")

    with open(destination_path, "wb") as file:
        file.write(data)

    return destination_path
