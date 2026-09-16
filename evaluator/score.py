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


def task_score(row: dict[str, Any]) -> float:
    if not row.get("correct", False):
        return 0.0
    score = row.get("score")
    if score is not None:
        return float(score)
    baseline = float(row["baseline_throughput"])
    candidate = float(row["candidate_throughput"])
    if baseline <= 0 or candidate <= 0:
        return 0.0
    return baseline / candidate


def tokens_per_score(row: dict[str, Any]) -> float | None:
    score = task_score(row)
    tokens = row.get("reasoning_tokens")
    if score <= 0 or tokens is None:
        return None
    return float(tokens) / score


def geometric_mean(values: Iterable[float]) -> float | None:
    vals = [v for v in values if v > 0]
    if not vals:
        return None
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["model"]), str(row["reasoning_effort"]))].append(row)

    out: list[dict[str, Any]] = []
    for (model, effort), group in sorted(groups.items()):
        scores = [task_score(r) for r in group]
        correct_scores = [s for s in scores if s > 0]
        tps = [v for r in group if (v := tokens_per_score(r)) is not None]
        reasoning = [float(r["reasoning_tokens"]) for r in group if r.get("reasoning_tokens") is not None]

        out.append(
            {
                "model": model,
                "reasoning_effort": effort,
                "tasks": len(group),
                "correct": len(correct_scores),
                "correctness_rate": len(correct_scores) / len(group) if group else 0.0,
                "geomean_speedup_correct": geometric_mean(correct_scores),
                "mean_score_with_failures": mean(scores) if scores else 0.0,
                "median_score_with_failures": median(scores) if scores else 0.0,
                "mean_reasoning_tokens": mean(reasoning) if reasoning else None,
                "mean_tokens_per_score": mean(tps) if tps else None,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.jsonl.read_text().splitlines() if line.strip()]
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
