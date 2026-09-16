#!/usr/bin/env python3
"""Run the v0 correctness gate and deterministic static throughput score."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from mca import block_rthroughput, speedup


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


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
    args = parser.parse_args()

    result: dict[str, object] = {
        "correct": False,
        "score": 0.0,
        "candidate_sha256": sha256(args.candidate),
    }

    try:
        # Structural/type validity first.
        run([args.llvm_as, str(args.candidate), "-o", "/dev/null"])

        # Alive2 is the hard semantic gate. Any non-zero exit fails the task.
        alive = run([args.alive_tv, str(args.reference), str(args.candidate)])
        result["alive2_stdout"] = alive.stdout.strip()

        with tempfile.TemporaryDirectory(prefix="table-irbench-") as tmp:
            tmpdir = Path(tmp)
            ref_asm = tmpdir / "reference.s"
            cand_asm = tmpdir / "candidate.s"

            common = [args.llc, args.llc_opt, f"-mtriple={args.triple}", f"-mcpu={args.mcpu}"]
            run([*common, str(args.reference), "-o", str(ref_asm)])
            run([*common, str(args.candidate), "-o", str(cand_asm)])

            baseline = block_rthroughput(ref_asm, mcpu=args.mcpu)
            candidate = block_rthroughput(cand_asm, mcpu=args.mcpu)
            result.update(
                {
                    "correct": True,
                    "baseline_throughput": baseline,
                    "candidate_throughput": candidate,
                    "speedup": speedup(baseline, candidate),
                    "score": speedup(baseline, candidate),
                }
            )
    except (subprocess.CalledProcessError, ValueError) as exc:
        result["error"] = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            result["stderr"] = (exc.stderr or "").strip()

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
