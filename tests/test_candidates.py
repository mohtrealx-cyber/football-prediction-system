import unittest

from candidates.engine import build_candidate_pool


class CandidateEngineTests(unittest.TestCase):

    def test_only_qualified_selections_are_kept(self):
        analyses = [
            {
                "match_id": "M1",
                "qualified": True,
                "score": 85.0,
            },
            {
                "match_id": "M2",
                "qualified": False,
                "score": 90.0,
            },
        ]

        result = build_candidate_pool(analyses)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["match_id"], "M1")

    def test_low_score_is_rejected(self):
        analyses = [
            {
                "match_id": "M1",
                "qualified": True,
                "score": 45.0,
            },
            {
                "match_id": "M2",
                "qualified": True,
                "score": 75.0,
            },
        ]

        result = build_candidate_pool(
            analyses,
            minimum_score=50.0,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["match_id"], "M2")

    def test_candidates_are_sorted_highest_first(self):
        analyses = [
            {
                "match_id": "M1",
                "qualified": True,
                "score": 65.0,
            },
            {
                "match_id": "M2",
                "qualified": True,
                "score": 85.0,
            },
            {
                "match_id": "M3",
                "qualified": True,
                "score": 75.0,
            },
        ]

        result = build_candidate_pool(analyses)

        scores = [
            item["score"]
            for item in result
        ]

        self.assertEqual(
            scores,
            [85.0, 75.0, 65.0],
        )

    def test_duplicate_match_is_removed(self):
        analyses = [
            {
                "match_id": "M1",
                "qualified": True,
                "score": 85.0,
            },
            {
                "match_id": "M1",
                "qualified": True,
                "score": 80.0,
            },
            {
                "match_id": "M2",
                "qualified": True,
                "score": 75.0,
            },
        ]

        result = build_candidate_pool(analyses)

        match_ids = [
            item["match_id"]
            for item in result
        ]

        self.assertEqual(
            match_ids,
            ["M1", "M2"],
        )

    def test_missing_match_id_is_rejected(self):
        analyses = [
            {
                "qualified": True,
                "score": 80.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_candidate_pool(analyses)

    def test_missing_qualified_field_is_rejected(self):
        analyses = [
            {
                "match_id": "M1",
                "score": 80.0,
            }
        ]

        with self.assertRaises(ValueError):
            build_candidate_pool(analyses)

    def test_missing_score_is_rejected(self):
        analyses = [
            {
                "match_id": "M1",
                "qualified": True,
            }
        ]

        with self.assertRaises(ValueError):
            build_candidate_pool(analyses)

    def test_invalid_minimum_score_is_rejected(self):
        with self.assertRaises(ValueError):
            build_candidate_pool(
                [],
                minimum_score=101.0,
            )


if __name__ == "__main__":
    unittest.main()
