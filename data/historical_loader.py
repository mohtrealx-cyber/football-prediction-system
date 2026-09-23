from data.historical_provider import HistoricalDataProvider


def load_historical_matches(
    csv_path: str,
    league: str,
):
    """Load historical matches through the historical data provider."""

    provider = HistoricalDataProvider(
        csv_path,
        league,
    )

    return provider.get_matches()
