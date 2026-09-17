#!/usr/bin/env python3
"""Aggregate benchmark JSONL and compute reasoning-efficiency metrics."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

from contracts import (
    REASONING_EFFORTS,
    VERIFIED,
    ContractError,
    task_score,
    validate_completion,
    validate_result_row,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "manifest.json"

EFFORT_ORDER = {
    name: index
    for index, name in enumerate(REASONING_EFFORTS)
}


def validate_result_set(rows: list[dict[str, Any]]) -> None:
    manifest = json.loads(MANIFEST.read_text())
    benchmark_version = manifest["benchmark_version"]
    run_ids: set[object] = set()
    attempts: set[tuple[object, str, str, str]] = set()
    task_sets: dict[tuple[str, str], set[str]] = defaultdict(set)

    for row in rows:
        validate_result_row(row, benchmark_version=benchmark_version)
        model = row["model"]
        effort = row["reasoning_effort"]
        task = row["task_id"]
        run_ids.add(row["run_id"])
        key = (row["run_id"], model, effort, task)
        if key in attempts:
            raise ContractError(f"duplicate attempt: {key!r}")
        attempts.add(key)
        task_sets[(model, effort)].add(task)

    if len(run_ids) > 1:
        raise ContractError("mixed run ids")
    distinct_task_sets = {frozenset(tasks) for tasks in task_sets.values()}
    if len(distinct_task_sets) > 1:
        raise ContractError("model/reasoning configurations have different task sets")


def geometric_mean(values: Iterable[float]) -> float | None:
    vals = list(values)
    if not vals:
        return None
    if any(not math.isfinite(v) or v <= 0 for v in vals):
        raise ContractError("geometric mean inputs must be finite and positive")
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_result_set(rows)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["model"]), str(row["reasoning_effort"]))].append(row)

    out: list[dict[str, Any]] = []
    for (model, effort), group in sorted(groups.items()):
        scores = [task_score(r) for r in group]
        verified_rows = [r for r in group if r["verification_status"] == VERIFIED]
        verified_scores = [task_score(r) for r in verified_rows]
        reasoning = [
            float(r["reasoning_tokens"])
            for r in group
            if r.get("reasoning_tokens") is not None
        ]
        reasoning_coverage = len(reasoning) / len(group) if group else 0.0
        total_score = sum(scores)
        all_attempt_efficiency = (
            sum(reasoning) / total_score
            if len(reasoning) == len(group) and total_score > 0
            else None
        )

        out.append(
            {
                "model": model,
                "reasoning_effort": effort,
                "tasks": len(group),
                "verified": len(verified_rows),
                "verification_rate": len(verified_rows) / len(group) if group else 0.0,
                "geomean_task_score_verified": geometric_mean(verified_scores),
                "mean_score_with_failures": mean(scores) if scores else 0.0,
                "median_score_with_failures": median(scores) if scores else 0.0,
                "mean_reasoning_tokens": mean(reasoning) if reasoning else None,
                "reasoning_token_coverage": reasoning_coverage,
                "reasoning_tokens_per_score_all_attempts": all_attempt_efficiency,
                "marginal_from_effort": None,
                "marginal_reasoning_tokens_per_score": None,
            }
        )

    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for summary in out:
        by_model[summary["model"]].append(summary)
    for model_summaries in by_model.values():
        ordered = sorted(
            model_summaries,
            key=lambda summary: EFFORT_ORDER.get(summary["reasoning_effort"], len(EFFORT_ORDER)),
        )
        for previous, current in zip(ordered, ordered[1:]):
            current["marginal_from_effort"] = previous["reasoning_effort"]
            if (
                previous["reasoning_token_coverage"] == 1.0
                and current["reasoning_token_coverage"] == 1.0
                and previous["mean_reasoning_tokens"] is not None
                and current["mean_reasoning_tokens"] is not None
            ):
                delta_score = (
                    current["mean_score_with_failures"] - previous["mean_score_with_failures"]
                )
                if delta_score > 0:
                    delta_tokens = (
                        current["mean_reasoning_tokens"] - previous["mean_reasoning_tokens"]
                    )
                    current["marginal_reasoning_tokens_per_score"] = delta_tokens / delta_score
    return out


def load_completed_rows(jsonl: Path) -> list[dict[str, Any]]:
    if jsonl.name != "results.jsonl":
        raise ContractError("scorer requires a run's canonical results.jsonl")
    run_path = jsonl.parent / "run.json"
    completion_path = jsonl.parent / "completed.json"
    if not run_path.is_file():
        raise ContractError(f"missing run metadata: {run_path}")
    if not completion_path.is_file():
        raise ContractError(f"run is incomplete: missing {completion_path}")

    lines = jsonl.read_text().splitlines()
    if not lines:
        raise ContractError("results.jsonl is empty")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line:
            raise ContractError(f"blank results.jsonl line: {line_number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ContractError(f"result line {line_number} is not an object")
        rows.append(value)

    run_meta = json.loads(run_path.read_text())
    completion = json.loads(completion_path.read_text())
    if not isinstance(run_meta, dict) or not isinstance(completion, dict):
        raise ContractError("run metadata and completion attestation must be objects")
    manifest = json.loads(MANIFEST.read_text())
    validate_completion(
        run_meta,
        completion,
        rows,
        jsonl,
        benchmark_version=manifest["benchmark_version"],
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()

    rows = load_completed_rows(args.jsonl)
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
