from data.historical_models import HistoricalMatch


def calculate_league_stats(
    matches: list[HistoricalMatch],
) -> dict:
    """Calculate basic league-wide goal statistics."""

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

    if not matches:
        return {
            "matches": 0,
            "avg_home_goals": 0.0,
            "avg_away_goals": 0.0,
            "avg_total_goals": 0.0,
        }

    total_home_goals = sum(
        match.home_goals
        for match in matches
    )

    total_away_goals = sum(
        match.away_goals
        for match in matches
    )

    total_goals = (
        total_home_goals
        + total_away_goals
    )

    match_count = len(matches)

    return {
        "matches": match_count,
        "avg_home_goals": total_home_goals / match_count,
        "avg_away_goals": total_away_goals / match_count,
        "avg_total_goals": total_goals / match_count,
    }
