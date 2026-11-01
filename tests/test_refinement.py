import unittest
from unittest.mock import Mock

from src.agents.refinement import parse_rating, refine


def run_refine(evaluations, **kwargs):
    """Runs refine over canned evaluations; each revision moves to the next resume version."""
    versions = {"current": 0}
    evaluate = Mock(side_effect=evaluations)
    revise = Mock(side_effect=lambda _: versions.update(current=versions["current"] + 1))
    snapshot = Mock(side_effect=lambda: versions["current"])
    restore = Mock(side_effect=lambda state: versions.update(current=state))
    result = refine(evaluate, revise, snapshot, restore, **kwargs)
    return result, versions["current"], revise, restore


class ParseRatingTests(unittest.TestCase):
    def test_accepts_common_formats(self):
        cases = {
            "FINAL_RATING: 8.5": 8.5,
            "**FINAL_RATING:** 9": 9.0,
            "FINAL_RATING: 7,5/10": 7.5,
            "final_rating = 10": 10.0,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(parse_rating(text), expected)

    def test_uses_last_occurrence(self):
        self.assertEqual(parse_rating("FINAL_RATING: 6\nsome text\nFINAL_RATING: 7"), 7.0)

    def test_rejects_missing_or_out_of_scale(self):
        for text in ("Overall rating: 8/10", "", None, "FINAL_RATING: 85", "FINAL_RATING: 0"):
            with self.subTest(text=text):
                self.assertIsNone(parse_rating(text))


class RefineTests(unittest.TestCase):
    def test_no_revision_when_first_rating_reaches_target(self):
        result, version, revise, restore = run_refine(["FINAL_RATING: 8.5"])
        self.assertTrue(result.reached_target)
        self.assertEqual(result.ratings, [8.5])
        self.assertEqual(version, 0)
        revise.assert_not_called()
        restore.assert_not_called()

    def test_revises_until_target(self):
        result, version, revise, restore = run_refine(
            ["FINAL_RATING: 6", "FINAL_RATING: 7.5", "FINAL_RATING: 9"]
        )
        self.assertTrue(result.reached_target)
        self.assertEqual(result.ratings, [6.0, 7.5, 9.0])
        self.assertEqual(revise.call_count, 2)
        self.assertEqual(version, 2)
        restore.assert_not_called()

    def test_feedback_reaches_the_revision(self):
        _, _, revise, _ = run_refine(["FINAL_RATING: 6 add keywords", "FINAL_RATING: 9"])
        revise.assert_called_once_with("FINAL_RATING: 6 add keywords")

    def test_stops_and_restores_when_revision_makes_it_worse(self):
        result, version, revise, restore = run_refine(["FINAL_RATING: 7.5", "FINAL_RATING: 7"])
        self.assertEqual(result.stop_reason, "no_improvement")
        self.assertEqual(result.best_rating, 7.5)
        self.assertEqual(result.final_feedback, "FINAL_RATING: 7.5")
        self.assertTrue(result.restored)
        self.assertEqual(revise.call_count, 1)
        self.assertEqual(version, 0)
        restore.assert_called_once_with(0)

    def test_stops_when_rating_stalls(self):
        result, version, revise, _ = run_refine(["FINAL_RATING: 7", "FINAL_RATING: 7"])
        self.assertEqual(result.stop_reason, "no_improvement")
        self.assertEqual(revise.call_count, 1)
        self.assertEqual(version, 0)

    def test_respects_revision_limit(self):
        result, version, revise, restore = run_refine(
            ["FINAL_RATING: 5", "FINAL_RATING: 6", "FINAL_RATING: 7"], max_revisions=2
        )
        self.assertEqual(result.stop_reason, "max_revisions")
        self.assertFalse(result.reached_target)
        self.assertEqual(revise.call_count, 2)
        self.assertEqual(version, 2)
        restore.assert_not_called()

    def test_zero_revisions_only_evaluates(self):
        result, _, revise, _ = run_refine(["FINAL_RATING: 5"], max_revisions=0)
        self.assertEqual(result.stop_reason, "max_revisions")
        revise.assert_not_called()

    def test_unreadable_first_rating_keeps_current_version(self):
        result, version, revise, restore = run_refine(["no rating here"])
        self.assertEqual(result.stop_reason, "unrated")
        self.assertIsNone(result.best_rating)
        self.assertEqual(result.final_feedback, "no rating here")
        self.assertEqual(version, 0)
        revise.assert_not_called()
        restore.assert_not_called()

    def test_unreadable_rating_after_revision_restores_best(self):
        result, version, _, restore = run_refine(["FINAL_RATING: 7", "no rating here"])
        self.assertEqual(result.stop_reason, "unrated")
        self.assertEqual(result.best_rating, 7.0)
        self.assertTrue(result.restored)
        self.assertEqual(version, 0)
        restore.assert_called_once_with(0)

    def test_summary_is_honest_about_missing_target(self):
        result, *_ = run_refine(["FINAL_RATING: 7", "FINAL_RATING: 6"])
        summary = result.summary()
        self.assertIn("Target reached: no", summary)
        self.assertIn("Final rating: 7.0", summary)
        self.assertIn("restored", summary)


if __name__ == "__main__":
    unittest.main()
