#!/usr/bin/env python3
"""Run the correctness gate and deterministic static throughput score."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from contracts import verification_fields
from mca import block_rthroughput

_ALIVE2_SUMMARY = re.compile(
    r"^Summary:\s*\n"
    r"\s*(?P<correct>\d+) correct transformations\s*\n"
    r"\s*(?P<incorrect>\d+) incorrect transformations\s*\n"
    r"\s*(?P<unproven>\d+) failed-to-prove transformations\s*\n"
    r"\s*(?P<errors>\d+) Alive2 errors\s*\Z",
    re.MULTILINE,
)


def run(cmd: list[str], *, timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, timeout=timeout)


def parse_alive2_summary(stdout: str) -> tuple[str, dict[str, int] | None]:
    """Classify the single-function Alive2 summary, failing closed."""
    matches = list(_ALIVE2_SUMMARY.finditer(stdout))
    if len(matches) != 1:
        return "evaluator_error", None

    counts = {name: int(value) for name, value in matches[0].groupdict().items()}
    if counts["errors"]:
        return "evaluator_error", counts
    if counts["incorrect"]:
        return "incorrect", counts
    if counts["unproven"]:
        return "unproven", counts
    if counts == {"correct": 1, "incorrect": 0, "unproven": 0, "errors": 0}:
        return "verified", counts
    return "invalid", counts


def print_result(result: dict[str, object]) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--mcpu", required=True)
    parser.add_argument("--triple", default="x86_64-unknown-linux-gnu")
    parser.add_argument("--alive-tv", default="alive-tv")
    parser.add_argument("--llc", default="llc")
    parser.add_argument("--llvm-as", default="llvm-as")
    parser.add_argument("--llc-opt", default="-O3")
    parser.add_argument("--function", default="kernel")
    parser.add_argument("--tool-timeout", type=float, default=60.0)
    args = parser.parse_args()

    result: dict[str, object] = {
        "candidate_sha256": sha256(args.candidate),
        **verification_fields("evaluator_error"),
    }

    try:
        # Structural/type validity first.
        run(
            [args.llvm_as, str(args.candidate), "-o", "/dev/null"],
            timeout=args.tool_timeout,
        )
    except subprocess.CalledProcessError as exc:
        result.update(verification_fields("invalid"))
        result["error"] = str(exc)
        result["stderr"] = (exc.stderr or "").strip()
        print_result(result)
        return
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.update(verification_fields("evaluator_error"))
        result["error"] = str(exc)
        if isinstance(exc, subprocess.TimeoutExpired):
            result["stderr"] = (exc.stderr or "").strip()
        print_result(result)
        return

    try:
        alive = run(
            [
                args.alive_tv,
                f"--func={args.function}",
                str(args.reference),
                str(args.candidate),
            ],
            timeout=args.tool_timeout,
        )
        result["alive2_stdout"] = alive.stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        result.update(verification_fields("evaluator_error"))
        result["error"] = str(exc)
        if isinstance(exc, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
            result["stderr"] = (exc.stderr or "").strip()
        print_result(result)
        return

    status, counts = parse_alive2_summary(alive.stdout)
    result["alive2_summary"] = counts
    if status != "verified":
        result.update(verification_fields(status))
        result["error"] = f"Alive2 verification status: {status}"
        print_result(result)
        return

    try:
        with tempfile.TemporaryDirectory(prefix="table-irbench-") as tmp:
            tmpdir = Path(tmp)
            ref_asm = tmpdir / "reference.s"
            cand_asm = tmpdir / "candidate.s"

            common = [args.llc, args.llc_opt, f"-mtriple={args.triple}", f"-mcpu={args.mcpu}"]
            run([*common, str(args.reference), "-o", str(ref_asm)], timeout=args.tool_timeout)
            run([*common, str(args.candidate), "-o", str(cand_asm)], timeout=args.tool_timeout)

            baseline = block_rthroughput(ref_asm, mcpu=args.mcpu, timeout=args.tool_timeout)
            candidate = block_rthroughput(cand_asm, mcpu=args.mcpu, timeout=args.tool_timeout)
            result.update(
                {
                    "baseline_throughput": baseline,
                    "candidate_throughput": candidate,
                    **verification_fields("verified"),
                }
            )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
        result.pop("baseline_throughput", None)
        result.pop("candidate_throughput", None)
        result.update(verification_fields("evaluator_error"))
        result["error"] = str(exc)
        if isinstance(exc, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
            result["stderr"] = (exc.stderr or "").strip()

    print_result(result)


if __name__ == "__main__":
    main()
