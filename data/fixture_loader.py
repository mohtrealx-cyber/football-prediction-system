from data.fixture_provider import FixtureDataProvider
from data.football_data_client import download_fixtures


def load_fixtures(
    destination_path: str,
    url: str = None,
    timeout: int = 30,
):
    """
    Download the latest fixture CSV and convert it into Match objects.

    The downloader is imported into this module intentionally so that
    callers/tests can patch data.fixture_loader.download_fixtures.
    """

    if not isinstance(destination_path, str):
        raise TypeError(
            "destination_path must be a string"
        )

    if not destination_path.strip():
        raise ValueError(
            "destination_path must be a non-empty string"
        )

    if url is None:
        download_fixtures(
            destination_path=destination_path,
            timeout=timeout,
        )
    else:
        download_fixtures(
            destination_path=destination_path,
            url=url,
            timeout=timeout,
        )

    provider = FixtureDataProvider(
        destination_path
    )

    return provider.get_matches()
