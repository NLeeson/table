#!/usr/bin/env python3
"""Run the frozen IR benchmark through Codex CLI model/reasoning configurations."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "manifest.json"
TASKS_DIR = ROOT / "benchmark" / "tasks"
OUTPUT_SCHEMA = ROOT / "benchmark" / "codex_output.schema.json"
VERIFY = ROOT / "evaluator" / "verify.py"
VALID_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}
FORBIDDEN_ITEM_TYPES = {
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "collab_tool_call",
    "web_search",
}
PROMPT_VERSION = "codex-ir-v1"


def slug(value: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in value)


def parse_codex_command(value: str) -> list[str]:
    try:
        command = shlex.split(value)
    except ValueError as exc:
        raise ValueError(f"invalid --codex command: {exc}") from exc
    if not command:
        raise ValueError("--codex command must not be empty")
    return command


def run_text(cmd: list[str], *, cwd: Path | None = None) -> str | None:
    try:
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip()


def git_head() -> str | None:
    return run_text(["git", "-C", str(ROOT), "rev-parse", "HEAD"])


def load_task_seed(task_dir: Path) -> Any:
    meta = task_dir / "task.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text()).get("seed")
    except (OSError, json.JSONDecodeError):
        return None


def load_matrix(path: Path) -> list[tuple[str, str]]:
    data = json.loads(path.read_text())
    pairs: list[tuple[str, str]] = []
    for entry in data.get("matrix", []):
        model = str(entry["model"])
        for effort in entry.get("efforts", []):
            effort = str(effort)
            if effort not in VALID_EFFORTS:
                raise ValueError(f"unsupported effort in matrix: {effort}")
            pairs.append((model, effort))
    if not pairs:
        raise ValueError("matrix contains no model/effort pairs")
    return pairs


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None, list[str]]:
    events: list[dict[str, Any]] = []
    bad_lines: list[str] = []
    usage: dict[str, Any] | None = None
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            bad_lines.append(line)
            continue
        events.append(event)
        if event.get("type") == "turn.completed":
            maybe_usage = event.get("usage")
            if isinstance(maybe_usage, dict):
                usage = maybe_usage
    return events, usage, bad_lines


def tool_types(events: list[dict[str, Any]]) -> list[str]:
    found: set[str] = set()
    for event in events:
        if event.get("type") not in {"item.started", "item.updated", "item.completed"}:
            continue
        item = event.get("item")
        if isinstance(item, dict):
            kind = item.get("type")
            if kind in FORBIDDEN_ITEM_TYPES:
                found.add(str(kind))
    return sorted(found)


def prompt_for(reference: str, *, triple: str, mcpu: str) -> str:
    return f"""You are being evaluated on semantic-preserving LLVM IR optimization.

Return a JSON object matching the supplied output schema, with exactly one field named \"ir\" containing the complete replacement LLVM IR module.

Rules:
- Do not use any tools, shell commands, files, web search, plugins, subagents, or external information.
- Optimize only by reasoning from the LLVM IR supplied below.
- Preserve the function's semantics for all inputs.
- Keep the same externally visible function signature and function name.
- Do not add globals, external calls, inline assembly, or target-specific intrinsics.
- The benchmark target is {triple}, CPU model {mcpu}.
- Return a complete LLVM IR module that llvm-as can parse.

Reference LLVM IR:
```llvm
{reference}
```
"""


def base_result(
    *,
    manifest: dict[str, Any],
    run_id: str,
    model: str,
    effort: str,
    task_dir: Path,
    latency_ms: float,
    usage: dict[str, Any] | None,
    codex_version: str | None,
) -> dict[str, Any]:
    usage = usage or {}
    toolchain = manifest["toolchain"]
    return {
        "benchmark_version": manifest["benchmark_version"],
        "run_id": run_id,
        "model": model,
        "reasoning_effort": effort,
        "task_id": task_dir.name,
        "task_seed": load_task_seed(task_dir),
        "correct": False,
        "score": 0.0,
        "input_tokens": int(usage.get("input_tokens", 0) or 0),
        "cached_input_tokens": int(usage.get("cached_input_tokens", 0) or 0),
        "cache_write_input_tokens": int(usage.get("cache_write_input_tokens", 0) or 0),
        "reasoning_tokens": usage.get("reasoning_output_tokens"),
        "output_tokens": int(usage.get("output_tokens", 0) or 0),
        "latency_ms": latency_ms,
        "cost_usd": None,
        "candidate_sha256": "0" * 64,
        "candidate_ir_path": None,
        "llvm_version": toolchain["llvm_version"],
        "alive2_revision": toolchain["alive2_revision"],
        "target_triple": toolchain["target_triple"],
        "mcpu": toolchain["mcpu"],
        "codex_version": codex_version,
        "prompt_version": PROMPT_VERSION,
        "error": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--matrix", type=Path, help="JSON model/effort matrix")
    source.add_argument("--model", action="append", help="model; repeat for a Cartesian product")
    parser.add_argument("--effort", action="append", choices=sorted(VALID_EFFORTS))
    parser.add_argument("--task", action="append", help="task id; default is all frozen tasks")
    parser.add_argument("--run-id")
    parser.add_argument(
        "--codex",
        default="codex",
        help="Codex executable and optional fixed arguments, parsed with shell-style quoting",
    )
    parser.add_argument("--timeout", type=float, default=900.0, help="seconds per Codex invocation")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        codex_command = parse_codex_command(args.codex)
    except ValueError as exc:
        parser.error(str(exc))

    if args.matrix:
        if args.effort:
            parser.error("--effort cannot be combined with --matrix")
        try:
            pairs = load_matrix(args.matrix)
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            parser.error(str(exc))
    else:
        if not args.effort:
            parser.error("--effort is required with --model")
        pairs = [(m, e) for m in args.model for e in args.effort]

    manifest = json.loads(MANIFEST.read_text())
    toolchain = manifest["toolchain"]
    all_tasks = sorted(p for p in TASKS_DIR.iterdir() if p.is_dir() and (p / "reference.ll").is_file())
    if args.task:
        wanted = set(args.task)
        tasks = [p for p in all_tasks if p.name in wanted]
        missing = wanted - {p.name for p in tasks}
        if missing:
            parser.error(f"unknown task(s): {', '.join(sorted(missing))}")
    else:
        tasks = all_tasks

    if not tasks:
        parser.error("no benchmark tasks found")

    run_id = args.run_id or datetime.now(timezone.utc).strftime("codex-%Y%m%dT%H%M%SZ")
    total = len(pairs) * len(tasks)
    print(f"planned: {len(pairs)} model/effort configs x {len(tasks)} tasks = {total} Codex calls")
    for model, effort in pairs:
        print(f"  {model} / {effort}")
    if args.dry_run:
        return 0

    run_dir = ROOT / "runs" / run_id
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"ERROR: run already exists: {run_dir}", file=sys.stderr)
        return 2

    (run_dir / "candidates").mkdir()
    (run_dir / "events").mkdir()
    (run_dir / "responses").mkdir()
    (run_dir / "stderr").mkdir()
    results_path = run_dir / "results.jsonl"
    codex_version = run_text([*codex_command, "--version"])

    run_meta = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": manifest["benchmark"],
        "benchmark_version": manifest["benchmark_version"],
        "benchmark_git_head": git_head(),
        "prompt_version": PROMPT_VERSION,
        "codex_version": codex_version,
        "matrix": [{"model": m, "reasoning_effort": e} for m, e in pairs],
        "tasks": [p.name for p in tasks],
        "toolchain": toolchain,
        "codex_isolation": {
            "ephemeral": True,
            "ignore_user_config": True,
            "ignore_rules": True,
            "strict_config": True,
            "sandbox": "read-only",
            "web_search": "disabled",
            "working_directory": "fresh temporary directory per task",
            "tool_use_policy": "any command/file/MCP/collab/web-search event invalidates the task",
        },
    }
    (run_dir / "run.json").write_text(json.dumps(run_meta, indent=2, sort_keys=True) + "\n")

    failures = 0
    completed = 0
    for model, effort in pairs:
        config_key = f"{slug(model)}__{slug(effort)}"
        for task_dir in tasks:
            completed += 1
            print(f"[{completed}/{total}] {model} / {effort} / {task_dir.name}", flush=True)
            reference_path = task_dir / "reference.ll"
            reference = reference_path.read_text()
            candidate_dir = run_dir / "candidates" / config_key
            candidate_dir.mkdir(parents=True, exist_ok=True)
            candidate_path = candidate_dir / f"{task_dir.name}.ll"
            response_path = run_dir / "responses" / f"{config_key}__{task_dir.name}.json"
            events_path = run_dir / "events" / f"{config_key}__{task_dir.name}.jsonl"
            stderr_path = run_dir / "stderr" / f"{config_key}__{task_dir.name}.txt"

            cmd = [
                *codex_command,
                "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--strict-config",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--model",
                model,
                "-c",
                f'model_reasoning_effort="{effort}"',
                "-c",
                'web_search="disabled"',
                "--json",
                "--output-schema",
                str(OUTPUT_SCHEMA),
                "--output-last-message",
                str(response_path),
                "-",
            ]

            start = time.perf_counter()
            stdout = ""
            stderr = ""
            returncode: int | None = None
            timeout_error: str | None = None
            with tempfile.TemporaryDirectory(prefix="table-codex-") as tmp:
                try:
                    proc = subprocess.run(
                        cmd,
                        input=prompt_for(reference, triple=toolchain["target_triple"], mcpu=toolchain["mcpu"]),
                        cwd=tmp,
                        text=True,
                        capture_output=True,
                        timeout=args.timeout,
                    )
                    stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or ""
                    stderr = exc.stderr or ""
                    timeout_error = f"Codex timed out after {args.timeout:g}s"
                except OSError as exc:
                    timeout_error = f"failed to launch Codex: {exc}"
            latency_ms = (time.perf_counter() - start) * 1000.0
            events_path.write_text(stdout)
            stderr_path.write_text(stderr)
            events, usage, bad_event_lines = parse_events(stdout)
            forbidden = tool_types(events)
            row = base_result(
                manifest=manifest,
                run_id=run_id,
                model=model,
                effort=effort,
                task_dir=task_dir,
                latency_ms=latency_ms,
                usage=usage,
                codex_version=codex_version,
            )
            row["events_path"] = str(events_path.relative_to(ROOT))
            row["forbidden_tool_types"] = forbidden
            row["jsonl_parse_errors"] = len(bad_event_lines)

            error: str | None = timeout_error
            if error is None and returncode != 0:
                error = f"Codex exited {returncode}"
            if error is None and bad_event_lines:
                error = f"Codex emitted {len(bad_event_lines)} non-JSON event line(s)"
            if error is None and forbidden:
                error = f"forbidden Codex tool use: {', '.join(forbidden)}"
            if error is None and usage is None:
                error = "missing turn.completed usage event"
            if error is None and not response_path.exists():
                error = "Codex did not write --output-last-message"

            if error is None:
                try:
                    response = json.loads(response_path.read_text())
                    candidate = response["ir"]
                    if not isinstance(candidate, str) or not candidate.strip():
                        raise ValueError("response.ir is empty")
                    candidate_path.write_text(candidate.rstrip() + "\n")
                    row["candidate_ir_path"] = str(candidate_path.relative_to(ROOT))
                except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
                    error = f"invalid structured Codex response: {exc}"

            if error is None:
                verify = subprocess.run(
                    [
                        sys.executable,
                        str(VERIFY),
                        str(reference_path),
                        str(candidate_path),
                        f'--mcpu={toolchain["mcpu"]}',
                        f'--triple={toolchain["target_triple"]}',
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                try:
                    verified = json.loads(verify.stdout)
                except json.JSONDecodeError as exc:
                    verified = None
                    error = f"evaluator returned invalid JSON: {exc}"
                if verified is not None:
                    for key in (
                        "correct",
                        "baseline_throughput",
                        "candidate_throughput",
                        "speedup",
                        "score",
                        "candidate_sha256",
                    ):
                        if key in verified:
                            row[key] = verified[key]
                    if verified.get("error"):
                        error = str(verified["error"])

            row["error"] = error
            if error is not None or not row.get("correct"):
                failures += 1
            with results_path.open("a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")

            status = "PASS" if row.get("correct") and error is None else "FAIL"
            reasoning = row.get("reasoning_tokens")
            print(
                f"  {status} score={row.get('score')} reasoning_tokens={reasoning} latency_ms={latency_ms:.0f}"
                + (f" error={error}" if error else ""),
                flush=True,
            )

    print(f"\nrun: {run_dir}")
    print(f"results: {results_path}")
    print(f"aggregate: python3 evaluator/score.py {results_path.relative_to(ROOT)}")
    print(f"completed: {total - failures}/{total} without failure")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
