from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

EVALUATOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALUATOR))

from contracts import completion_record, file_sha256  # noqa: E402
from score import load_completed_rows, summarize  # noqa: E402


def row(
    task: str,
    status: str,
    score: float,
    tokens: int | None,
    *,
    model: str = "model",
    effort: str = "high",
    version: str = "0.2.0",
) -> dict[str, object]:
    result: dict[str, object] = {
        "benchmark_version": version,
        "run_id": "test-run",
        "model": model,
        "reasoning_effort": effort,
        "task_id": task,
        "task_seed": 1,
        "verification_status": status,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_input_tokens": 0,
        "reasoning_tokens": tokens,
        "output_tokens": 0,
        "latency_ms": 1.0,
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


class ScoreTests(unittest.TestCase):
    def test_all_correct_geomean(self) -> None:
        summary = summarize(
            [row("a", "verified", 1.0, 100), row("b", "verified", 4.0, 100)]
        )[0]
        self.assertEqual(summary["verified"], 2)
        self.assertEqual(summary["geomean_task_score_verified"], 2.0)

    def test_mixed_failure_keeps_correct_only_geomean(self) -> None:
        summary = summarize(
            [row("a", "verified", 2.0, 100), row("b", "incorrect", 0.0, 10_000)]
        )[0]

        self.assertEqual(summary["verified"], 1)
        self.assertEqual(summary["verification_rate"], 0.5)
        self.assertEqual(summary["geomean_task_score_verified"], 2.0)
        self.assertEqual(summary["mean_score_with_failures"], 1.0)
        self.assertEqual(summary["reasoning_tokens_per_score_all_attempts"], 5050.0)
        self.assertEqual(summary["reasoning_token_coverage"], 1.0)

    def test_all_failed_efficiency_is_undefined(self) -> None:
        summary = summarize(
            [row("a", "incorrect", 0.0, 100), row("b", "unproven", 0.0, 200)]
        )[0]

        self.assertIsNone(summary["geomean_task_score_verified"])
        self.assertIsNone(summary["reasoning_tokens_per_score_all_attempts"])

    def test_missing_tokens_reports_coverage_and_no_efficiency(self) -> None:
        summary = summarize(
            [row("a", "verified", 1.0, 100), row("b", "verified", 1.0, None)]
        )[0]

        self.assertEqual(summary["reasoning_token_coverage"], 0.5)
        self.assertIsNone(summary["reasoning_tokens_per_score_all_attempts"])

    def test_duplicate_attempt_is_rejected(self) -> None:
        duplicate = row("a", "verified", 1.0, 100)
        with self.assertRaisesRegex(ValueError, "duplicate attempt"):
            summarize([duplicate, dict(duplicate)])

    def test_mixed_benchmark_versions_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "benchmark_version must be"):
            summarize(
                [
                    row("a", "verified", 1.0, 100, version="0.2.0"),
                    row("b", "verified", 1.0, 100, version="0.3.0"),
                ]
            )

    def test_mixed_run_ids_are_rejected(self) -> None:
        first = row("a", "verified", 1.0, 100)
        second = row("a", "verified", 1.0, 100)
        second["run_id"] = "another-run"
        with self.assertRaisesRegex(ValueError, "run ids"):
            summarize([first, second])

    def test_unknown_result_field_is_rejected(self) -> None:
        result = row("a", "verified", 1.0, 100)
        result["score"] = 1.0
        with self.assertRaisesRegex(ValueError, "unknown result fields"):
            summarize([result])

    def test_different_task_sets_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "task sets"):
            summarize(
                [
                    row("a", "verified", 1.0, 100, model="one"),
                    row("b", "verified", 1.0, 100, model="two"),
                ]
            )

    def test_marginal_efficiency_uses_comparable_all_attempt_means(self) -> None:
        summaries = summarize(
            [
                row("a", "verified", 1.0, 100, effort="high"),
                row("a", "verified", 2.0, 300, effort="max"),
            ]
        )
        by_effort = {summary["reasoning_effort"]: summary for summary in summaries}
        self.assertIsNone(by_effort["high"]["marginal_reasoning_tokens_per_score"])
        self.assertEqual(by_effort["max"]["marginal_from_effort"], "high")
        self.assertEqual(by_effort["max"]["marginal_reasoning_tokens_per_score"], 200.0)


class CompletedRunTests(unittest.TestCase):
    def write_run(
        self,
        directory: Path,
        rows: list[dict[str, object]],
        *,
        tasks: list[str],
        complete: bool,
    ) -> Path:
        run_meta = {
            "run_id": "test-run",
            "benchmark_version": "0.2.0",
            "matrix": [{"model": "model", "reasoning_effort": "high"}],
            "tasks": tasks,
        }
        (directory / "run.json").write_text(json.dumps(run_meta) + "\n")
        results_path = directory / "results.jsonl"
        results_path.write_text("".join(json.dumps(item) + "\n" for item in rows))
        if complete:
            completion = completion_record(
                run_meta,
                attempts=len(rows),
                results_sha256=file_sha256(results_path),
                completed_at="2026-09-17T00:00:00+00:00",
            )
            (directory / "completed.json").write_text(json.dumps(completion) + "\n")
        return results_path

    def test_completed_exact_run_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_run(
                Path(tmp), [row("a", "verified", 1.0, 100)], tasks=["a"], complete=True
            )
            self.assertEqual(load_completed_rows(path)[0]["task_id"], "a")

    def test_missing_completion_attestation_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_run(
                Path(tmp), [row("a", "verified", 1.0, 100)], tasks=["a"], complete=False
            )
            with self.assertRaisesRegex(ValueError, "run is incomplete"):
                load_completed_rows(path)

    def test_missing_planned_attempt_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_run(
                Path(tmp),
                [row("a", "verified", 1.0, 100)],
                tasks=["a", "b"],
                complete=True,
            )
            with self.assertRaisesRegex(ValueError, "coverage mismatch"):
                load_completed_rows(path)

    def test_results_changed_after_completion_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_run(
                Path(tmp), [row("a", "verified", 1.0, 100)], tasks=["a"], complete=True
            )
            value = json.loads(path.read_text())
            path.write_text(json.dumps(value, sort_keys=True) + "\n")
            with self.assertRaisesRegex(ValueError, "digest does not match"):
                load_completed_rows(path)


if __name__ == "__main__":
    unittest.main()
