from typing import Dict

from analysis.engine import analyze_selection
from data.models import Match
from prediction.engine import predict_match
from scoring.engine import calculate_score


SUPPORTED_MARKETS = {
    "home_win",
    "draw",
    "away_win",
    "over_2_5",
    "under_2_5",
    "btts_yes",
    "btts_no",
}


def run_match_pipeline(
    match: Match,
    market: str,
    home_expected_goals: float,
    away_expected_goals: float,
    odds: float,
    minimum_edge: float = 5.0,
) -> Dict:
    """
    Run one match through the current pipeline.

    Flow:
        Match
          ↓
        Prediction
          ↓
        Select market probability
          ↓
        Odds/value analysis
          ↓
        Ranking score
    """

    match.validate()

    if market not in SUPPORTED_MARKETS:
        raise ValueError(
            f"Unsupported market: {market}"
        )

    predictions = predict_match(
        home_expected_goals,
        away_expected_goals,
    )

    model_probability = predictions[market]

    analysis = analyze_selection(
        market=market,
        model_probability=model_probability,
        odds=odds,
        minimum_edge=minimum_edge,
    )

    score = calculate_score(
        model_probability=model_probability,
        value_edge=analysis.value_edge,
    )

    return {
        "match_id": match.match_id,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "league": match.league,
        "kickoff": match.kickoff.isoformat(),
        "market": market,
        "model_probability": model_probability,
        "odds": odds,
        "market_probability": analysis.market_probability,
        "expected_value": analysis.expected_value,
        "value_edge": analysis.value_edge,
        "qualified": analysis.qualified,
        "score": score,
    }
