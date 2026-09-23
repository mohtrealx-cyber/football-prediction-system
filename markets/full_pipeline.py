from markets.pipeline import run_market_pipeline
from markets.scorer import score_market_analyses


def run_full_market_pipeline(
    predictions,
    odds,
    minimum_edge=5.0,
):
    """
    Generate, analyze, score, and rank all available markets.
    """
    analyses = run_market_pipeline(
        predictions=predictions,
        odds=odds,
        minimum_edge=minimum_edge,
    )

    return score_market_analyses(analyses)
