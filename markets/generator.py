from analysis.engine import analyze_selection
from markets.engine import get_market_probability, get_supported_markets


def generate_market_analyses(
    predictions,
    odds,
    minimum_edge=5.0,
):
    """
    Analyze every supported market for which odds are available.
    """
    if not isinstance(predictions, dict):
        raise TypeError("predictions must be a dictionary")

    if not isinstance(odds, dict):
        raise TypeError("odds must be a dictionary")

    analyses = []

    for market in get_supported_markets():
        if market not in odds:
            continue

        model_probability = get_market_probability(
            predictions,
            market,
        )

        result = analyze_selection(
            market=market,
            model_probability=model_probability,
            odds=odds[market],
            minimum_edge=minimum_edge,
        )

        analyses.append(result)

    return analyses
