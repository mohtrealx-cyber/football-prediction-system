from datetime import datetime

from data.historical_filter import filter_matches_before
from data.historical_models import HistoricalMatch
from data.models import Match
from data.historical_stats import calculate_team_stats
from data.home_away_stats import calculate_home_away_stats
from data.form_stats import calculate_recent_form
from data.league_stats import calculate_league_stats


def build_match_features(
    historical_matches: list[HistoricalMatch],
    target_match: Match,
) -> dict:
    """
    Build historical features for a target match.

    Only historical matches before the target kickoff are used.
    """

    if not isinstance(historical_matches, list):
        raise TypeError("historical_matches must be a list")

    if not isinstance(target_match, Match):
        raise TypeError("target_match must be a Match")

    for match in historical_matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every historical match must be a HistoricalMatch")

    if not isinstance(target_match.kickoff, datetime):
        raise TypeError("target_match kickoff must be a datetime")

    if target_match.kickoff.tzinfo is None:
        raise ValueError("target_match kickoff must be timezone-aware")

    # Prevent future-data leakage.
    previous_matches = filter_matches_before(
        historical_matches,
        target_match.kickoff,
    )

    # Restrict calculations to the target league.
    league_matches = [
        match
        for match in previous_matches
        if match.league == target_match.league
    ]

    team_stats = calculate_team_stats(league_matches)
    home_away_stats = calculate_home_away_stats(league_matches)
    recent_form = calculate_recent_form(league_matches, recent_matches=5)
    league_stats = calculate_league_stats(league_matches)

    home_team = target_match.home_team
    away_team = target_match.away_team

    home_team_stats = team_stats.get(
        home_team,
        {
            "matches": 0,
            "goals_for": 0,
            "goals_against": 0,
            "avg_goals_for": 0.0,
            "avg_goals_against": 0.0,
        },
    )

    away_team_stats = team_stats.get(
        away_team,
        {
            "matches": 0,
            "goals_for": 0,
            "goals_against": 0,
            "avg_goals_for": 0.0,
            "avg_goals_against": 0.0,
        },
    )

    home_form = recent_form.get(
        home_team,
        {
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0,
            "goals_for": 0,
            "goals_against": 0,
        },
    )

    away_form = recent_form.get(
        away_team,
        {
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0,
            "goals_for": 0,
            "goals_against": 0,
        },
    )

    home_specific = home_away_stats.get(
        home_team,
        {
            "home": {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
                "avg_goals_for": 0.0,
                "avg_goals_against": 0.0,
            },
            "away": {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
                "avg_goals_for": 0.0,
                "avg_goals_against": 0.0,
            },
        },
    )

    away_specific = home_away_stats.get(
        away_team,
        {
            "home": {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
                "avg_goals_for": 0.0,
                "avg_goals_against": 0.0,
            },
            "away": {
                "matches": 0,
                "goals_for": 0,
                "goals_against": 0,
                "avg_goals_for": 0.0,
                "avg_goals_against": 0.0,
            },
        },
    )

    league_home_avg = league_stats["avg_home_goals"]
    league_away_avg = league_stats["avg_away_goals"]

    # Use neutral fallback strengths when the league baseline is zero.
    if league_home_avg > 0:
        home_attack_strength = (
            home_team_stats["avg_goals_for"] / league_home_avg
        )
    else:
        home_attack_strength = 0.0

    if league_away_avg > 0:
        away_attack_strength = (
            away_team_stats["avg_goals_for"] / league_away_avg
        )
    else:
        away_attack_strength = 0.0

    if league_away_avg > 0:
        home_defense_strength = (
            home_team_stats["avg_goals_against"] / league_away_avg
        )
    else:
        home_defense_strength = 0.0

    if league_home_avg > 0:
        away_defense_strength = (
            away_team_stats["avg_goals_against"] / league_home_avg
        )
    else:
        away_defense_strength = 0.0

    return {
        "home_attack_strength": home_attack_strength,
        "home_defense_strength": home_defense_strength,
        "away_attack_strength": away_attack_strength,
        "away_defense_strength": away_defense_strength,

        "home_recent_points": home_form["points"],
        "away_recent_points": away_form["points"],

        "home_form_goals_for": home_form["goals_for"],
        "away_form_goals_for": away_form["goals_for"],

        "home_home_avg_goals": home_specific["home"]["avg_goals_for"],
        "away_away_avg_goals": away_specific["away"]["avg_goals_for"],

        "league_avg_home_goals": league_home_avg,
        "league_avg_away_goals": league_away_avg,
    }
