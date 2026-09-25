from markets.engine import get_supported_markets
from performance.engine import calculate_performance
from performance.market import calculate_market_performance


def build_performance_report(results: dict) -> dict:
    """
    Build one overall performance report containing:

    1. Overall performance across all supported markets.
    2. Separate performance for each market.
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

    # Require every supported market.
    missing_markets = supported_market_set - provided_market_set

    if missing_markets:
        raise ValueError(
            f"Missing market(s): {sorted(missing_markets)}"
        )

    # First calculate the individual market performance.
    market_performance = calculate_market_performance(results)

    # Combine all market results into one overall result list.
    all_results = []

    for market in supported_markets:
        market_results = results[market]

        if not isinstance(market_results, list):
            raise TypeError(
                f"Results for {market} must be a list"
            )

        all_results.extend(market_results)

    # Calculate the overall performance.
    overall_performance = calculate_performance(all_results)

    return {
        "overall": overall_performance,
        "markets": market_performance,
    }
