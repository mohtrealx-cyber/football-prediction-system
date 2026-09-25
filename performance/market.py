from markets.engine import get_supported_markets
from performance.engine import calculate_performance


def calculate_market_performance(results: dict) -> dict:
    """
    Calculate performance metrics separately for every supported market.

    Expected input:

        {
            "home_win": [...],
            "draw": [...],
            "away_win": [...],
            "over_2_5": [...],
            "under_2_5": [...],
            "btts_yes": [...],
            "btts_no": [...],
        }

    Each market contains the rolling backtest results for that market.

    Returns a dictionary containing the normal performance metrics for
    each market.
    """

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    supported_markets = get_supported_markets()
    supported_market_set = set(supported_markets)

    provided_market_set = set(results.keys())

    # Reject unknown markets.
    unknown_markets = provided_market_set - supported_market_set

    if unknown_markets:
        raise ValueError(
            f"Unsupported market(s): {sorted(unknown_markets)}"
        )

    # Require every supported market to be present.
    missing_markets = supported_market_set - provided_market_set

    if missing_markets:
        raise ValueError(
            f"Missing market(s): {sorted(missing_markets)}"
        )

    performance_by_market = {}

    for market in supported_markets:
        market_results = results[market]

        if not isinstance(market_results, list):
            raise TypeError(
                f"Results for {market} must be a list"
            )

        # Reuse the existing performance engine instead of duplicating
        # the calculations for wins, losses, ROI and drawdown.
        try:
            performance = calculate_performance(market_results)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid results for market {market}: {exc}"
            ) from exc

        performance_by_market[market] = performance

    return performance_by_market
