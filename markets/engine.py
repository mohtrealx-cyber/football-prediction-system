SUPPORTED_MARKETS = {
    "home_win": "home_win",
    "draw": "draw",
    "away_win": "away_win",
    "over_2_5": "over_2_5",
    "under_2_5": "under_2_5",
    "btts_yes": "btts_yes",
    "btts_no": "btts_no",
}


def get_market_probability(predictions, market):
    """Return the model probability for a supported market."""
    if market not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market: {market}")

    if not isinstance(predictions, dict):
        raise TypeError("predictions must be a dictionary")

    key = SUPPORTED_MARKETS[market]

    if key not in predictions:
        raise ValueError(f"Prediction missing for market: {market}")

    probability = predictions[key]

    if not isinstance(probability, (int, float)):
        raise TypeError("Market probability must be numeric")

    if not 0.0 <= probability <= 1.0:
        raise ValueError("Market probability must be between 0 and 1")

    return float(probability)


def get_supported_markets():
    """Return all supported betting markets."""
    return tuple(SUPPORTED_MARKETS.keys())
