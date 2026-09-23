from dataclasses import dataclass

from odds.engine import expected_value, implied_probability, value_edge


@dataclass
class SelectionAnalysis:
    market: str
    model_probability: float
    odds: float
    market_probability: float
    expected_value: float
    value_edge: float
    qualified: bool

    def to_dict(self) -> dict:
        return {
            "market": self.market,
            "model_probability": self.model_probability,
            "odds": self.odds,
            "market_probability": self.market_probability,
            "expected_value": self.expected_value,
            "value_edge": self.value_edge,
            "qualified": self.qualified,
        }


def analyze_selection(
    market: str,
    model_probability: float,
    odds: float,
    minimum_edge: float = 5.0,
) -> SelectionAnalysis:
    """
    Combine model probability with bookmaker odds.

    minimum_edge is measured in percentage points.

    Example:
    model probability = 0.60
    odds = 2.00
    market probability = 50%
    value edge = 10%
    """

    if not market.strip():
        raise ValueError("market cannot be empty")

    if not 0 <= model_probability <= 1:
        raise ValueError(
            "model_probability must be between 0 and 1"
        )

    if odds <= 1.0:
        raise ValueError(
            "odds must be greater than 1.0"
        )

    if minimum_edge < 0:
        raise ValueError(
            "minimum_edge cannot be negative"
        )

    market_probability = implied_probability(odds)
    ev = expected_value(model_probability, odds)
    edge = value_edge(model_probability, odds)

    qualified = edge >= minimum_edge

    return SelectionAnalysis(
        market=market,
        model_probability=round(model_probability, 6),
        odds=odds,
        market_probability=market_probability,
        expected_value=ev,
        value_edge=edge,
        qualified=qualified,
    )
