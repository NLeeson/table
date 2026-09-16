#!/usr/bin/env python3
"""Small helpers for deterministic llvm-mca scoring."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Sequence

_BLOCK_RTHROUGHPUT = re.compile(r"^Block RThroughput:\s*([0-9]+(?:\.[0-9]+)?)\s*$", re.MULTILINE)


def block_rthroughput(assembly: Path, *, mcpu: str, extra_args: Sequence[str] = ()) -> float:
    cmd = ["llvm-mca", f"-mcpu={mcpu}", *extra_args, str(assembly)]
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    match = _BLOCK_RTHROUGHPUT.search(proc.stdout)
    if not match:
        raise ValueError("llvm-mca output did not contain Block RThroughput")
    value = float(match.group(1))
    if value <= 0:
        raise ValueError(f"invalid Block RThroughput: {value}")
    return value


def speedup(baseline: float, candidate: float) -> float:
    if baseline <= 0 or candidate <= 0:
        raise ValueError("throughput values must be positive")
    return baseline / candidate
