#!/usr/bin/env python3
"""Run every frozen benchmark reference against itself and require score == 1.0."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from contracts import VERIFIED, ContractError, task_score, validate_attempt

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "manifest.json"
TASKS_DIR = ROOT / "benchmark" / "tasks"
VERIFY = ROOT / "evaluator" / "verify.py"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    mcpu = manifest["toolchain"]["mcpu"]
    triple = manifest["toolchain"]["target_triple"]
    expected_tasks = sum(int(family["instances"]) for family in manifest["families"])

    task_dirs = sorted(
        p for p in TASKS_DIR.iterdir()
        if p.is_dir() and (p / "reference.ll").is_file()
    )

    if len(task_dirs) != expected_tasks:
        print(f"ERROR: expected {expected_tasks} smoke tasks, found {len(task_dirs)}", file=sys.stderr)
        return 2

    failures: list[str] = []
    rows: list[dict[str, object]] = []

    for task_dir in task_dirs:
        ref = task_dir / "reference.ll"
        proc = subprocess.run(
            [
                sys.executable,
                str(VERIFY),
                str(ref),
                str(ref),
                f"--mcpu={mcpu}",
                f"--triple={triple}",
            ],
            text=True,
            capture_output=True,
        )

        if proc.returncode != 0:
            failures.append(f"{task_dir.name}: verify.py exited {proc.returncode}: {proc.stderr.strip()}")
            continue

        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"{task_dir.name}: invalid JSON from verify.py: {exc}")
            continue

        try:
            validate_attempt(result)
        except ContractError as exc:
            failures.append(f"{task_dir.name}: result contract violation: {exc}")
            continue

        verification_status = result.get("verification_status")
        score = task_score(result)
        baseline = result.get("baseline_throughput")
        candidate = result.get("candidate_throughput")

        passed = (
            verification_status == VERIFIED
            and isinstance(score, (int, float))
            and abs(float(score) - 1.0) < 1e-12
            and baseline == candidate
        )

        rows.append(
            {
                "task_id": task_dir.name,
                "verification_status": verification_status,
                "baseline_throughput": baseline,
                "candidate_throughput": candidate,
                "derived_task_score": score,
                "pass": passed,
            }
        )

        if not passed:
            failures.append(f"{task_dir.name}: self-check mismatch: {json.dumps(result, sort_keys=True)}")

    print(json.dumps({"mcpu": mcpu, "target_triple": triple, "tasks": rows}, indent=2))

    if failures:
        print("\nFAILURES:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"\nPASS: {len(rows)}/{expected_tasks} reference self-checks verified with derived task score 1.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
