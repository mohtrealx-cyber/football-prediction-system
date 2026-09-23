from markets.generator import generate_market_analyses


def run_market_pipeline(
    predictions,
    odds,
    minimum_edge=5.0,
):
    """
    Run the market analysis pipeline for one match.
    """
    return generate_market_analyses(
        predictions=predictions,
        odds=odds,
        minimum_edge=minimum_edge,
    )
