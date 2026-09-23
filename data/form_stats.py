from data.historical_models import HistoricalMatch


def calculate_recent_form(
    matches: list[HistoricalMatch],
    recent_matches: int = 5,
) -> dict:
    """Calculate recent form statistics for each team."""

    if not isinstance(matches, list):
        raise TypeError("matches must be a list")

    if not isinstance(recent_matches, int):
        raise TypeError("recent_matches must be an integer")

    if recent_matches <= 0:
        raise ValueError("recent_matches must be greater than zero")

    for match in matches:
        if not isinstance(match, HistoricalMatch):
            raise TypeError("Every item must be a HistoricalMatch")

    if not matches:
        return {}

    sorted_matches = sorted(
        matches,
        key=lambda match: match.kickoff,
        reverse=True,
    )

    team_matches = {}

    for match in sorted_matches:
        if match.home_team not in team_matches:
            team_matches[match.home_team] = []

        if match.away_team not in team_matches:
            team_matches[match.away_team] = []

        if len(team_matches[match.home_team]) < recent_matches:
            team_matches[match.home_team].append(
                (
                    match,
                    "home",
                )
            )

        if len(team_matches[match.away_team]) < recent_matches:
            team_matches[match.away_team].append(
                (
                    match,
                    "away",
                )
            )

    form = {}

    for team, team_history in team_matches.items():
        stats = {
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0,
            "goals_for": 0,
            "goals_against": 0,
        }

        for match, venue in team_history:
            stats["matches"] += 1

            if venue == "home":
                goals_for = match.home_goals
                goals_against = match.away_goals
            else:
                goals_for = match.away_goals
                goals_against = match.home_goals

            stats["goals_for"] += goals_for
            stats["goals_against"] += goals_against

            if goals_for > goals_against:
                stats["wins"] += 1
                stats["points"] += 3
            elif goals_for == goals_against:
                stats["draws"] += 1
                stats["points"] += 1
            else:
                stats["losses"] += 1

        form[team] = stats

    return form
