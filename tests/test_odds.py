import unittest

from odds.engine import (
    implied_probability,
    expected_value,
    value_edge,
)


class OddsEngineTests(unittest.TestCase):

    def test_implied_probability(self):
        result = implied_probability(2.0)

        self.assertAlmostEqual(result, 0.5)

    def test_expected_value(self):
        result = expected_value(0.60, 2.0)

        self.assertAlmostEqual(result, 0.20)

    def test_value_edge(self):
        result = value_edge(0.60, 2.0)

        self.assertAlmostEqual(result, 10.0)

    def test_invalid_odds_are_rejected(self):
        with self.assertRaises(ValueError):
            implied_probability(1.0)

    def test_invalid_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            expected_value(1.5, 2.0)

    def test_negative_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            expected_value(-0.1, 2.0)

    def test_probability_zero_is_allowed(self):
        result = expected_value(0.0, 2.0)

        self.assertAlmostEqual(result, -1.0)

    def test_probability_one_is_allowed(self):
        result = expected_value(1.0, 2.0)

        self.assertAlmostEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main()
