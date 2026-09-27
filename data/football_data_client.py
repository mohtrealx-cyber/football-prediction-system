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
    """Download the Football-Data fixtures CSV."""

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if not isinstance(url, str) or not url.strip():
        raise ValueError(
            "url must be a non-empty string"
        )

    if (
        not isinstance(timeout, int)
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError(
            "timeout must be a positive integer"
        )

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
            "Accept": (
                "text/csv,text/plain,"
                "application/csv,*/*"
            ),
        },
    )

    with urlopen(
        request,
        timeout=timeout,
    ) as response:
        data = response.read()

        # Some test doubles do not provide headers.
        # Only read Content-Type when headers exist.
        headers = getattr(response, "headers", None)

        if headers is not None:
            content_type = headers.get(
                "Content-Type",
                "",
            )
        else:
            content_type = ""

    if not data:
        raise ValueError(
            "Downloaded fixture file is empty"
        )

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Downloaded fixture file is not valid UTF-8 text"
        ) from exc

    if not text.strip():
        raise ValueError(
            "Downloaded fixture file contains no data"
        )

    # Validate that the downloaded resource looks like
    # the Football-Data fixtures CSV.
    first_line = text.splitlines()[0].strip()

    required_headers = {
        "Date",
        "Time",
        "Home",
        "Away",
        "Div",
    }

    headers = {
        column.strip()
        for column in first_line.split(",")
        if column.strip()
    }

    missing_headers = sorted(
        required_headers - headers
    )

    if missing_headers:
        raise ValueError(
            "Downloaded fixture source did not return "
            "the expected Football-Data CSV. "
            f"Missing columns: {missing_headers}. "
            f"Content-Type: {content_type!r}. "
            f"First line: {first_line[:300]!r}"
        )

    with open(
        destination_path,
        "wb",
    ) as file:
        file.write(data)

    return destination_path
