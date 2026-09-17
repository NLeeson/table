from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "evaluator"
FIXTURES = EVALUATOR / "tests" / "fixtures"
REFERENCE = ROOT / "benchmark" / "tasks" / "bitops_popcount32" / "reference.ll"
sys.path.insert(0, str(EVALUATOR))

from verify import parse_alive2_summary  # noqa: E402
from contracts import task_score  # noqa: E402


class Alive2SummaryTests(unittest.TestCase):
    def test_counterexample_is_incorrect(self) -> None:
        status, counts = parse_alive2_summary(
            """Summary:
  0 correct transformations
  1 incorrect transformations
  0 failed-to-prove transformations
  0 Alive2 errors
"""
        )
        self.assertEqual(status, "incorrect")
        self.assertEqual(counts["incorrect"], 1)

    def test_failed_proof_is_unproven(self) -> None:
        status, _ = parse_alive2_summary(
            """Summary:
  0 correct transformations
  0 incorrect transformations
  1 failed-to-prove transformations
  0 Alive2 errors
"""
        )
        self.assertEqual(status, "unproven")

    def test_zero_matches_is_invalid(self) -> None:
        status, _ = parse_alive2_summary(
            """Summary:
  0 correct transformations
  0 incorrect transformations
  0 failed-to-prove transformations
  0 Alive2 errors
"""
        )
        self.assertEqual(status, "invalid")

    def test_missing_summary_is_evaluator_error(self) -> None:
        status, counts = parse_alive2_summary("unexpected output")
        self.assertEqual(status, "evaluator_error")
        self.assertIsNone(counts)


@unittest.skipUnless(
    all(shutil.which(tool) for tool in ("alive-tv", "llvm-as", "llc", "llvm-mca")),
    "LLVM/Alive2 tools are required",
)
class VerifyIntegrationTests(unittest.TestCase):
    def verify(self, candidate: Path, *extra: str) -> dict[str, object]:
        proc = subprocess.run(
            [
                sys.executable,
                str(EVALUATOR / "verify.py"),
                str(REFERENCE),
                str(candidate),
                "--mcpu=haswell",
                "--triple=x86_64-unknown-linux-gnu",
                *extra,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)

    def test_reference_verifies(self) -> None:
        result = self.verify(REFERENCE)
        self.assertEqual(result["verification_status"], "verified")
        self.assertEqual(task_score(result), 1.0)

    def test_wrong_candidate_scores_zero(self) -> None:
        result = self.verify(FIXTURES / "wrong.ll")
        self.assertEqual(result["verification_status"], "incorrect")
        self.assertEqual(task_score(result), 0.0)

    def test_renamed_candidate_scores_zero(self) -> None:
        result = self.verify(FIXTURES / "renamed.ll")
        self.assertEqual(result["verification_status"], "invalid")
        self.assertEqual(task_score(result), 0.0)

    def test_invalid_ir_scores_zero(self) -> None:
        result = self.verify(FIXTURES / "invalid.ll")
        self.assertEqual(result["verification_status"], "invalid")
        self.assertEqual(task_score(result), 0.0)

    def test_missing_alive2_is_evaluator_error(self) -> None:
        result = self.verify(REFERENCE, "--alive-tv=/definitely/missing/alive-tv")
        self.assertEqual(result["verification_status"], "evaluator_error")
        self.assertEqual(task_score(result), 0.0)


if __name__ == "__main__":
    unittest.main()
