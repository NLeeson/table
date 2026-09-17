#!/usr/bin/env python3
"""Compare two completed benchmark runs by paired task outcomes."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from contracts import ContractError
from metrics import (
    TaskOutcome,
    compare_task_outcomes,
    pooled_score_per_1k_reasoning_tokens,
    task_outcome,
)
from score import load_completed_rows, validate_result_set

PAIR_FIELDS = (
    "benchmark_version",
    "task_seed",
    "llvm_version",
    "alive2_revision",
    "target_triple",
    "mcpu",
    "prompt_version",
)


def _key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row["model"]), str(row["reasoning_effort"]), str(row["task_id"]))


def _outcome_payload(row: dict[str, Any], outcome: TaskOutcome) -> dict[str, Any]:
    return {
        "verification_status": outcome.verification_status,
        "score": outcome.score,
        "reasoning_tokens": outcome.reasoning_tokens,
        "score_per_1k_reasoning_tokens": outcome.efficiency.as_dict(),
        "latency_ms": row["latency_ms"],
    }


def _percentage_change(left: int | None, right: int | None) -> dict[str, Any]:
    if left is None or right is None:
        return {"kind": "unknown", "value": None}
    if left == 0:
        if right == 0:
            return {"kind": "not_applicable", "value": None}
        return {"kind": "unbounded_increase", "value": None}
    return {"kind": "finite", "value": 100.0 * (right - left) / left}


def _side_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes = [task_outcome(row) for row in rows]
    known_tokens = [
        outcome.reasoning_tokens
        for outcome in outcomes
        if outcome.reasoning_tokens is not None
    ]
    return {
        "tasks": len(outcomes),
        "verified": sum(outcome.kind == "verified" for outcome in outcomes),
        "verification_rate": (
            sum(outcome.kind == "verified" for outcome in outcomes) / len(outcomes)
            if outcomes
            else 0.0
        ),
        "mean_score_with_failures": (
            mean(outcome.score for outcome in outcomes) if outcomes else 0.0
        ),
        "reasoning_token_coverage": (
            len(known_tokens) / len(outcomes) if outcomes else 0.0
        ),
        "total_reasoning_tokens": (
            sum(known_tokens) if len(known_tokens) == len(outcomes) else None
        ),
        "pooled_score_per_1k_reasoning_tokens": (
            pooled_score_per_1k_reasoning_tokens(rows).as_dict()
        ),
    }


def _paired_counts(results: list[str]) -> dict[str, int]:
    counts = Counter(results)
    return {
        "left_wins": counts["left_wins"],
        "right_wins": counts["right_wins"],
        "ties": counts["tie"],
        "tradeoffs": counts["tradeoff"],
        "unknown": counts["unknown"],
    }


def compare_rows(
    left_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
    *,
    left_label: str,
    right_label: str,
) -> dict[str, Any]:
    """Compare two validated result sets paired by model, effort, and task."""
    validate_result_set(left_rows)
    validate_result_set(right_rows)
    left_by_key = {_key(row): row for row in left_rows}
    right_by_key = {_key(row): row for row in right_rows}
    if set(left_by_key) != set(right_by_key):
        missing_right = sorted(set(left_by_key) - set(right_by_key))
        missing_left = sorted(set(right_by_key) - set(left_by_key))
        raise ContractError(
            "paired task coverage mismatch: "
            f"missing_left={missing_left!r}, missing_right={missing_right!r}"
        )

    tasks: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for key in sorted(left_by_key):
        left = left_by_key[key]
        right = right_by_key[key]
        for field in PAIR_FIELDS:
            if left[field] != right[field]:
                raise ContractError(
                    f"incomparable field {field} for paired task {key!r}: "
                    f"{left[field]!r} != {right[field]!r}"
                )
        left_outcome = task_outcome(left)
        right_outcome = task_outcome(right)
        paired_result = compare_task_outcomes(left_outcome, right_outcome)
        left_tokens = left_outcome.reasoning_tokens
        right_tokens = right_outcome.reasoning_tokens
        record = {
            "model": key[0],
            "reasoning_effort": key[1],
            "task_id": key[2],
            "paired_outcome": paired_result,
            "left": _outcome_payload(left, left_outcome),
            "right": _outcome_payload(right, right_outcome),
            "score_delta": right_outcome.score - left_outcome.score,
            "reasoning_tokens_delta": (
                right_tokens - left_tokens
                if left_tokens is not None and right_tokens is not None
                else None
            ),
            "reasoning_tokens_percent_change": _percentage_change(
                left_tokens, right_tokens
            ),
            "latency_ms_delta": float(right["latency_ms"]) - float(left["latency_ms"]),
        }
        tasks.append(record)
        grouped[(key[0], key[1])].append(record)

    configurations: list[dict[str, Any]] = []
    for (model, effort), records in sorted(grouped.items()):
        keys = [
            (record["model"], record["reasoning_effort"], record["task_id"])
            for record in records
        ]
        config_left = [left_by_key[key] for key in keys]
        config_right = [right_by_key[key] for key in keys]
        configurations.append(
            {
                "model": model,
                "reasoning_effort": effort,
                "paired_outcomes": _paired_counts(
                    [str(record["paired_outcome"]) for record in records]
                ),
                "left": _side_summary(config_left),
                "right": _side_summary(config_right),
            }
        )

    return {
        "left_label": left_label,
        "right_label": right_label,
        "paired_outcomes": _paired_counts(
            [str(record["paired_outcome"]) for record in tasks]
        ),
        "left": _side_summary(left_rows),
        "right": _side_summary(right_rows),
        "configurations": configurations,
        "tasks": tasks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--left-label")
    parser.add_argument("--right-label")
    args = parser.parse_args()

    comparison = compare_rows(
        load_completed_rows(args.left),
        load_completed_rows(args.right),
        left_label=args.left_label or args.left.parent.name,
        right_label=args.right_label or args.right.parent.name,
    )
    print(json.dumps(comparison, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
