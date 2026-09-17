#!/usr/bin/env python3
"""Small helpers for deterministic llvm-mca scoring."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Sequence

_BLOCK_RTHROUGHPUT = re.compile(r"^Block RThroughput:\s*([0-9]+(?:\.[0-9]+)?)\s*$", re.MULTILINE)


def block_rthroughput(
    assembly: Path,
    *,
    mcpu: str,
    extra_args: Sequence[str] = (),
    timeout: float | None = None,
) -> float:
    cmd = ["llvm-mca", f"-mcpu={mcpu}", *extra_args, str(assembly)]
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True, timeout=timeout)
    match = _BLOCK_RTHROUGHPUT.search(proc.stdout)
    if not match:
        raise ValueError("llvm-mca output did not contain Block RThroughput")
    value = float(match.group(1))
    if value <= 0:
        raise ValueError(f"invalid Block RThroughput: {value}")
    return value
