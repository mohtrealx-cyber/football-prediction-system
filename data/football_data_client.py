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

    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/154.0.0.0 Safari/537.36"
            ),
            "Accept": "text/csv,text/plain,*/*",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        data = response.read()

    if not data:
        raise ValueError(
            "Downloaded fixture file is empty"
        )

    # Decode enough of the response to verify that we actually
    # received a CSV-like document rather than an HTML/error page.
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Downloaded fixture file is not valid UTF-8 CSV data"
        ) from exc

    if not text.strip():
        raise ValueError(
            "Downloaded fixture file contains no CSV data"
        )

    first_line = text.splitlines()[0].strip()

    if not first_line:
        raise ValueError(
            "Downloaded fixture file has an empty header"
        )

    # Football-Data fixture CSVs must contain these columns.
    required_columns = {
        "Date",
        "Time",
        "Home",
        "Away",
        "Div",
    }

    header = {
        column.strip().strip('"')
        for column in first_line.split(",")
    }

    missing = sorted(required_columns - header)

    if missing:
        preview = text[:300].replace("\n", "\\n")

        raise ValueError(
            "Downloaded fixture data does not contain the expected "
            f"Football-Data CSV columns. Missing: {missing}. "
            f"Response preview: {preview}"
        )

    with open(destination_path, "wb") as file:
        file.write(data)

    return destination_path
