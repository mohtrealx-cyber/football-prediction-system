def implied_probability(odds: float) -> float:
    """
    Convert decimal odds into implied probability.

    Example:
    2.00 odds = 50%
    """
    if odds <= 1.0:
        raise ValueError("odds must be greater than 1.0")

    return round(1.0 / odds, 6)


def expected_value(
    model_probability: float,
    odds: float,
) -> float:
    """
    Calculate expected value.

    EV = (model probability × odds) - 1

    Example:
    60% probability at 2.00 odds:
    EV = (0.60 × 2.00) - 1
       = 0.20
       = +20%
    """
    if not 0 <= model_probability <= 1:
        raise ValueError(
            "model_probability must be between 0 and 1"
        )

    if odds <= 1.0:
        raise ValueError("odds must be greater than 1.0")

    return round(
        (model_probability * odds) - 1,
        6,
    )


def value_edge(
    model_probability: float,
    odds: float,
) -> float:
    """
    Compare model probability with bookmaker implied probability.

    Returns the difference in percentage points.

    Example:
    Model = 60%
    Odds = 2.00 → market = 50%

    Edge = +10 percentage points
    """
    market_probability = implied_probability(odds)

    edge = (
        model_probability
        - market_probability
    )

    return round(edge * 100, 2)
