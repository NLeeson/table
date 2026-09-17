from __future__ import annotations

import sys
import unittest
from pathlib import Path

EVALUATOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALUATOR))

from metrics import (  # noqa: E402
    FINITE,
    UNBOUNDED,
    UNKNOWN,
    ZERO,
    compare_task_outcomes,
    pooled_score_per_1k_reasoning_tokens,
    task_outcome,
)


def attempt(status: str, score: float, tokens: int | None) -> dict[str, object]:
    row: dict[str, object] = {
        "verification_status": status,
        "reasoning_tokens": tokens,
    }
    if status == "verified":
        row["baseline_throughput"] = score
        row["candidate_throughput"] = 1.0
    return row


class TaskOutcomeTests(unittest.TestCase):
    def test_non_verified_zero_over_zero_is_bottom_not_undefined(self) -> None:
        outcome = task_outcome(attempt("incorrect", 0.0, 0))

        self.assertEqual(outcome.kind, "non_verified")
        self.assertEqual(outcome.score, 0.0)
        self.assertEqual(outcome.efficiency.kind, ZERO)
        self.assertEqual(outcome.efficiency.value, 0.0)

    def test_non_verified_missing_tokens_remains_bottom(self) -> None:
        outcome = task_outcome(attempt("unproven", 0.0, None))

        self.assertEqual(outcome.kind, "non_verified")
        self.assertIsNone(outcome.reasoning_tokens)
        self.assertEqual(outcome.efficiency.kind, ZERO)

    def test_verified_zero_tokens_is_explicitly_unbounded(self) -> None:
        outcome = task_outcome(attempt("verified", 2.0, 0))

        self.assertEqual(outcome.kind, "verified")
        self.assertEqual(outcome.efficiency.kind, UNBOUNDED)
        self.assertIsNone(outcome.efficiency.value)

    def test_verified_missing_tokens_is_unknown(self) -> None:
        outcome = task_outcome(attempt("verified", 2.0, None))

        self.assertEqual(outcome.efficiency.kind, UNKNOWN)
        self.assertIsNone(outcome.efficiency.value)

    def test_verified_finite_efficiency_preserves_ratio(self) -> None:
        outcome = task_outcome(attempt("verified", 2.0, 80))

        self.assertEqual(outcome.efficiency.kind, FINITE)
        self.assertEqual(outcome.efficiency.value, 25.0)

    def test_verified_always_beats_non_verified(self) -> None:
        result = compare_task_outcomes(
            task_outcome(attempt("incorrect", 0.0, 0)),
            task_outcome(attempt("verified", 1.0, 10_000)),
        )

        self.assertEqual(result, "right_wins")

    def test_two_non_verified_outcomes_tie_at_bottom(self) -> None:
        result = compare_task_outcomes(
            task_outcome(attempt("incorrect", 0.0, 0)),
            task_outcome(attempt("invalid", 0.0, 100)),
        )

        self.assertEqual(result, "tie")

    def test_successful_pareto_dominance_uses_score_and_tokens(self) -> None:
        result = compare_task_outcomes(
            task_outcome(attempt("verified", 2.0, 100)),
            task_outcome(attempt("verified", 2.0, 50)),
        )

        self.assertEqual(result, "right_wins")

    def test_successful_conflicting_dimensions_are_a_tradeoff(self) -> None:
        result = compare_task_outcomes(
            task_outcome(attempt("verified", 2.0, 50)),
            task_outcome(attempt("verified", 3.0, 100)),
        )

        self.assertEqual(result, "tradeoff")

    def test_successful_missing_tokens_are_unknown(self) -> None:
        result = compare_task_outcomes(
            task_outcome(attempt("verified", 2.0, None)),
            task_outcome(attempt("verified", 2.0, 100)),
        )

        self.assertEqual(result, "unknown")

    def test_pooled_rate_remains_descriptive_not_failure_sensitive(self) -> None:
        rows = [
            attempt("verified", 1.0, 0),
            attempt("incorrect", 0.0, 0),
            attempt("verified", 9.0, 100),
        ]

        pooled = pooled_score_per_1k_reasoning_tokens(rows)
        without_failure = pooled_score_per_1k_reasoning_tokens([rows[0], rows[2]])
        self.assertEqual(pooled.kind, FINITE)
        self.assertEqual(pooled.value, 100.0)
        self.assertEqual(pooled, without_failure)


if __name__ == "__main__":
    unittest.main()
