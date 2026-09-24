from data.historical_models import HistoricalMatch


SUPPORTED_MARKETS = {
    "home_win",
    "draw",
    "away_win",
    "over_2_5",
    "under_2_5",
    "btts_yes",
    "btts_no",
}


def settle_market(match: HistoricalMatch, market: str) -> bool:
    """
    Determine whether a historical market selection won.

    Returns:
        True  -> selection won
        False -> selection lost
    """

    if not isinstance(match, HistoricalMatch):
        raise TypeError("match must be a HistoricalMatch")

    if not isinstance(market, str):
        raise TypeError("market must be a string")

    if market not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market: {market}")

    home_goals = match.home_goals
    away_goals = match.away_goals
    total_goals = home_goals + away_goals

    if market == "home_win":
        return home_goals > away_goals

    if market == "draw":
        return home_goals == away_goals

    if market == "away_win":
        return away_goals > home_goals

    if market == "over_2_5":
        return total_goals > 2

    if market == "under_2_5":
        return total_goals <= 2

    if market == "btts_yes":
        return home_goals >= 1 and away_goals >= 1

    if market == "btts_no":
        return home_goals == 0 or away_goals == 0

    return False
