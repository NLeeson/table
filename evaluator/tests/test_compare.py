from __future__ import annotations

import sys
import unittest
from pathlib import Path

EVALUATOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALUATOR))

from compare import compare_rows  # noqa: E402


def row(
    task: str,
    status: str,
    score: float,
    tokens: int | None,
    *,
    run_id: str,
) -> dict[str, object]:
    result: dict[str, object] = {
        "benchmark_version": "0.2.0",
        "run_id": run_id,
        "model": "model",
        "reasoning_effort": "high",
        "task_id": task,
        "task_seed": 1,
        "verification_status": status,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_input_tokens": 0,
        "reasoning_tokens": tokens,
        "output_tokens": 0,
        "latency_ms": 10.0,
        "cost_usd": None,
        "candidate_sha256": "0" * 64,
        "candidate_ir_path": None,
        "llvm_version": "22.1.0",
        "alive2_revision": "revision",
        "target_triple": "x86_64-unknown-linux-gnu",
        "mcpu": "haswell",
        "codex_version": None,
        "prompt_version": "test",
        "events_path": "events/test.jsonl",
        "forbidden_tool_types": [],
        "jsonl_parse_errors": 0,
        "error": None if status == "verified" else status,
    }
    if status == "verified":
        result["baseline_throughput"] = score
        result["candidate_throughput"] = 1.0
    return result


class CompareTests(unittest.TestCase):
    def test_pairs_tasks_and_counts_non_verified_as_a_loss(self) -> None:
        comparison = compare_rows(
            [
                row("a", "incorrect", 0.0, 0, run_id="left"),
                row("b", "verified", 2.0, 100, run_id="left"),
            ],
            [
                row("a", "verified", 1.0, 1_000, run_id="right"),
                row("b", "verified", 2.0, 50, run_id="right"),
            ],
            left_label="stock",
            right_label="modified",
        )

        self.assertEqual(
            comparison["paired_outcomes"],
            {
                "left_wins": 0,
                "right_wins": 2,
                "ties": 0,
                "tradeoffs": 0,
                "unknown": 0,
            },
        )
        self.assertEqual(comparison["left"]["verification_rate"], 0.5)
        self.assertEqual(comparison["right"]["verification_rate"], 1.0)
        self.assertEqual(comparison["tasks"][0]["paired_outcome"], "right_wins")
        self.assertEqual(
            comparison["tasks"][0]["left"]["score_per_1k_reasoning_tokens"],
            {"kind": "zero", "value": 0.0},
        )

    def test_rejects_different_pair_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "paired task coverage mismatch"):
            compare_rows(
                [row("a", "verified", 1.0, 10, run_id="left")],
                [row("b", "verified", 1.0, 10, run_id="right")],
                left_label="left",
                right_label="right",
            )

    def test_rejects_mismatched_benchmark_inputs(self) -> None:
        left = row("a", "verified", 1.0, 10, run_id="left")
        right = row("a", "verified", 1.0, 10, run_id="right")
        right["mcpu"] = "znver4"

        with self.assertRaisesRegex(ValueError, "incomparable field mcpu"):
            compare_rows(
                [left],
                [right],
                left_label="left",
                right_label="right",
            )


if __name__ == "__main__":
    unittest.main()
