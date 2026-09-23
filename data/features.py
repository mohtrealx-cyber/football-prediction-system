    home_specific = home_away_stats.get(
        home_team,
        {
            "home_matches": 0,
            "home_goals_for": 0,
            "home_goals_against": 0,
            "home_avg_goals_for": 0.0,
            "home_avg_goals_against": 0.0,
            "away_matches": 0,
            "away_goals_for": 0,
            "away_goals_against": 0,
            "away_avg_goals_for": 0.0,
            "away_avg_goals_against": 0.0,
        },
    )

    away_specific = home_away_stats.get(
        away_team,
        {
            "home_matches": 0,
            "home_goals_for": 0,
            "home_goals_against": 0,
            "home_avg_goals_for": 0.0,
            "home_avg_goals_against": 0.0,
            "away_matches": 0,
            "away_goals_for": 0,
            "away_goals_against": 0,
            "away_avg_goals_for": 0.0,
            "away_avg_goals_against": 0.0,
        },
    )
