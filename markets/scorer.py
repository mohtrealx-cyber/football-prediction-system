from scoring.engine import calculate_score


def score_market_analyses(analyses):
    """
    Calculate scores for all market analyses and rank them.
    """
    if not isinstance(analyses, list):
        raise TypeError("analyses must be a list")

    scored = []

    for analysis in analyses:
        if not hasattr(analysis, "model_probability"):
            raise ValueError("Analysis is missing model_probability")

        if not hasattr(analysis, "value_edge"):
            raise ValueError("Analysis is missing value_edge")

        item = analysis.__dict__.copy()

        item["score"] = calculate_score(
            model_probability=analysis.model_probability,
            value_edge=analysis.value_edge,
        )

        scored.append(item)

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored
