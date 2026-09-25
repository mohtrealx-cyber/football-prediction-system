from markets.engine import get_supported_markets
from performance.engine import calculate_performance
from performance.market import calculate_market_performance
from performance.streaks import calculate_streaks


def build_performance_report(results: dict) -> dict:
    """
    Build the complete performance report.

    The report contains:
    - overall performance across all market results
    - performance for each supported market
    - streak statistics across all market results
    """

    if not isinstance(results, dict):
        raise TypeError("results must be a dictionary")

    supported_markets = get_supported_markets()
    required_markets = set(supported_markets)
    provided_markets = set(results.keys())

    unknown_markets = provided_markets - required_markets
    if unknown_markets:
        raise ValueError(
            f"unknown markets: {sorted(unknown_markets)}"
        )

    missing_markets = required_markets - provided_markets
    if missing_markets:
        raise ValueError(
            f"missing markets: {sorted(missing_markets)}"
        )

    # Calculate performance separately for every market.
    market_performance = calculate_market_performance(results)

    # Combine all market results into one list for overall performance
    # and streak calculations.
    all_results = []

    for market_name in supported_markets:
        market_results = results[market_name]

        if not isinstance(market_results, list):
            raise TypeError(
                f"results for market '{market_name}' must be a list"
            )

        all_results.extend(market_results)

    overall_performance = calculate_performance(all_results)

    # Calculate streaks across all market results.
    streaks = calculate_streaks(all_results)

    return {
        "overall": overall_performance,
        "markets": market_performance,
        "streaks": streaks,
    }
