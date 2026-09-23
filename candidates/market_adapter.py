def adapt_markets_to_candidates(
    match_id,
    scored_markets,
):
    """
    Convert scored market results into candidate records
    that can be used by the existing candidate engine.
    """
    if not isinstance(match_id, str) or not match_id.strip():
        raise ValueError("match_id must be a non-empty string")

    if not isinstance(scored_markets, list):
        raise TypeError("scored_markets must be a list")

    required_fields = {
        "market",
        "model_probability",
        "odds",
        "market_probability",
        "expected_value",
        "value_edge",
        "qualified",
        "score",
    }

    candidates = []

    for market in scored_markets:
        if not isinstance(market, dict):
            raise TypeError("Each market result must be a dictionary")

        missing_fields = required_fields - market.keys()

        if missing_fields:
            raise ValueError(
                f"Market result is missing fields: "
                f"{sorted(missing_fields)}"
            )

        candidate = dict(market)
        candidate["match_id"] = match_id

        candidates.append(candidate)

    return candidates
