from backtesting.rolling import rolling_backtest
from markets.engine import get_supported_markets


def rolling_backtest_all_markets(
    matches: list,
    stake: float = 1.0,
) -> dict:
    """
    Run the rolling historical backtest across every supported market.

    Each market is tested independently using the existing
    rolling_backtest() engine.

    Returns:
        {
            "home_win": [...],
            "draw": [...],
            "away_win": [...],
            "over_2_5": [...],
            "under_2_5": [...],
            "btts_yes": [...],
            "btts_no": [...],
        }
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    supported_markets = get_supported_markets()

    results = {}

    for market in supported_markets:
        results[market] = rolling_backtest(
            matches=matches,
            market=market,
            stake=stake,
        )

    return results
