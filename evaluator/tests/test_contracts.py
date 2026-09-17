from __future__ import annotations

import sys
import unittest
from pathlib import Path

EVALUATOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALUATOR))

from contracts import (  # noqa: E402
    ContractError,
    task_score,
    validate_attempt,
    verification_fields,
)


class OutcomeContractTests(unittest.TestCase):
    def test_status_is_the_only_persisted_outcome(self) -> None:
        for status in ("incorrect", "unproven", "invalid", "evaluator_error"):
            with self.subTest(status=status):
                self.assertEqual(verification_fields(status), {"verification_status": status})

    def test_verified_score_is_derived_from_throughputs(self) -> None:
        row = {
            "verification_status": "verified",
            "baseline_throughput": 5.0,
            "candidate_throughput": 2.0,
        }
        validate_attempt(row)
        self.assertEqual(task_score(row), 2.5)

    def test_validator_rejects_measurements_on_non_verified_attempt(self) -> None:
        with self.assertRaises(ContractError):
            validate_attempt(
                {
                    "verification_status": "incorrect",
                    "baseline_throughput": 3.0,
                    "candidate_throughput": 1.0,
                    "reasoning_tokens": 10,
                }
            )

    def test_non_verified_score_is_derived_as_zero(self) -> None:
        self.assertEqual(task_score({"verification_status": "incorrect"}), 0.0)

    def test_validator_rejects_missing_status(self) -> None:
        with self.assertRaises(ContractError):
            validate_attempt({})


if __name__ == "__main__":
    unittest.main()
