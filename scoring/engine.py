from typing import List, Dict


def calculate_score(
    model_probability: float,
    value_edge: float,
) -> float:
    """
    Create a simple 0-100 selection score.

    70% = model probability
    30% = value edge

    value_edge is capped at 20 percentage points.
    """

    if not 0 <= model_probability <= 1:
        raise ValueError(
            "model_probability must be between 0 and 1"
        )

    if value_edge < 0:
        raise ValueError(
            "value_edge cannot be negative"
        )

    probability_component = model_probability * 70

    capped_edge = min(value_edge, 20.0)

    value_component = (
        capped_edge / 20.0
    ) * 30

    score = (
        probability_component
        + value_component
    )

    return round(score, 2)


def rank_selections(
    selections: List[Dict],
) -> List[Dict]:
    """
    Add a score to each selection and return
    the selections from strongest to weakest.

    Each selection must contain:
        model_probability
        value_edge
    """

    ranked = []

    for selection in selections:
        if "model_probability" not in selection:
            raise ValueError(
                "selection is missing model_probability"
            )

        if "value_edge" not in selection:
            raise ValueError(
                "selection is missing value_edge"
            )

        item = selection.copy()

        item["score"] = calculate_score(
            selection["model_probability"],
            selection["value_edge"],
        )

        ranked.append(item)

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked
