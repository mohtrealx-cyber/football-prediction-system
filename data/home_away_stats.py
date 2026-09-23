from data.historical_models import HistoricalMatch


def calculate_home_away_stats(
    matches: list[HistoricalMatch],
) -> dict:
    """Calculate separate home and away statistics for each team."""

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    stats = {}

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

        if match.home_team not in stats:
            stats[match.home_team] = {
                "home_matches": 0,
                "home_goals_for": 0,
                "home_goals_against": 0,
                "away_matches": 0,
                "away_goals_for": 0,
                "away_goals_against": 0,
            }

        if match.away_team not in stats:
            stats[match.away_team] = {
                "home_matches": 0,
                "home_goals_for": 0,
                "home_goals_against": 0,
                "away_matches": 0,
                "away_goals_for": 0,
                "away_goals_against": 0,
            }

        home = stats[match.home_team]
        away = stats[match.away_team]

        home["home_matches"] += 1
        home["home_goals_for"] += match.home_goals
        home["home_goals_against"] += match.away_goals

        away["away_matches"] += 1
        away["away_goals_for"] += match.away_goals
        away["away_goals_against"] += match.home_goals

    for team_stats in stats.values():
        home_matches = team_stats["home_matches"]
        away_matches = team_stats["away_matches"]

        if home_matches > 0:
            team_stats["home_avg_goals_for"] = (
                team_stats["home_goals_for"] / home_matches
            )
            team_stats["home_avg_goals_against"] = (
                team_stats["home_goals_against"] / home_matches
            )
        else:
            team_stats["home_avg_goals_for"] = 0.0
            team_stats["home_avg_goals_against"] = 0.0

        if away_matches > 0:
            team_stats["away_avg_goals_for"] = (
                team_stats["away_goals_for"] / away_matches
            )
            team_stats["away_avg_goals_against"] = (
                team_stats["away_goals_against"] / away_matches
            )
        else:
            team_stats["away_avg_goals_for"] = 0.0
            team_stats["away_avg_goals_against"] = 0.0

    return stats
