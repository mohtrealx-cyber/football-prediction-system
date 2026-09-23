from data.historical_models import HistoricalMatch


def calculate_team_stats(matches: list[HistoricalMatch]) -> dict:
    """Calculate basic historical statistics for each team."""

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    stats = {}

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

        if match.home_team not in stats:
            stats[match.home_team] = {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
            }

        if match.away_team not in stats:
            stats[match.away_team] = {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
            }

        stats[match.home_team]["matches"] += 1
        stats[match.home_team]["goals_for"] += match.home_goals
        stats[match.home_team]["goals_against"] += match.away_goals

        stats[match.away_team]["matches"] += 1
        stats[match.away_team]["goals_for"] += match.away_goals
        stats[match.away_team]["goals_against"] += match.home_goals

    for team_stats in stats.values():
        matches_played = team_stats["matches"]

        if matches_played > 0:
            team_stats["avg_goals_for"] = (
                team_stats["goals_for"] / matches_played
            )
            team_stats["avg_goals_against"] = (
                team_stats["goals_against"] / matches_played
            )
        else:
            team_stats["avg_goals_for"] = 0.0
            team_stats["avg_goals_against"] = 0.0

    return stats
