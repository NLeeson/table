"""Derived task-outcome and reasoning-efficiency representations."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from contracts import VERIFIED, task_score

ZERO = "zero"
FINITE = "finite"
UNBOUNDED = "unbounded"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class Efficiency:
    """A JSON-safe value in the extended non-negative efficiency domain."""

    kind: str
    value: float | None

    def as_dict(self) -> dict[str, float | str | None]:
        return {"kind": self.kind, "value": self.value}


@dataclass(frozen=True)
class TaskOutcome:
    """A task result where every non-verified outcome is the bottom element."""

    kind: str
    verification_status: str
    score: float
    reasoning_tokens: int | None
    efficiency: Efficiency


def task_outcome(row: Mapping[str, Any]) -> TaskOutcome:
    """Map one attempt into the ordered task-outcome domain."""
    score = task_score(row)
    status = str(row["verification_status"])
    tokens = row.get("reasoning_tokens")

    if status != VERIFIED:
        return TaskOutcome(
            kind="non_verified",
            verification_status=status,
            score=0.0,
            reasoning_tokens=tokens,
            efficiency=Efficiency(ZERO, 0.0),
        )
    if tokens is None:
        efficiency = Efficiency(UNKNOWN, None)
    elif tokens == 0:
        efficiency = Efficiency(UNBOUNDED, None)
    else:
        efficiency = Efficiency(FINITE, 1000.0 * score / tokens)
    return TaskOutcome(
        kind="verified",
        verification_status=status,
        score=score,
        reasoning_tokens=tokens,
        efficiency=efficiency,
    )


def compare_task_outcomes(left: TaskOutcome, right: TaskOutcome) -> str:
    """Compare paired task outcomes without collapsing quality and cost."""
    if left.kind != right.kind:
        return "left_wins" if left.kind == "verified" else "right_wins"
    if left.kind == "non_verified":
        return "tie"
    if left.reasoning_tokens is None or right.reasoning_tokens is None:
        return "unknown"

    left_at_least_as_good = (
        left.score >= right.score
        and left.reasoning_tokens <= right.reasoning_tokens
    )
    right_at_least_as_good = (
        right.score >= left.score
        and right.reasoning_tokens <= left.reasoning_tokens
    )
    if left_at_least_as_good and right_at_least_as_good:
        return "tie"
    if left_at_least_as_good:
        return "left_wins"
    if right_at_least_as_good:
        return "right_wins"
    return "tradeoff"


def pooled_score_per_1k_reasoning_tokens(
    rows: Iterable[Mapping[str, Any]],
) -> Efficiency:
    """Return the descriptive pooled rate; this is not completion-sensitive."""
    attempts = list(rows)
    if not attempts or any(row.get("reasoning_tokens") is None for row in attempts):
        return Efficiency(UNKNOWN, None)
    total_score = sum(task_score(row) for row in attempts)
    total_tokens = sum(int(row["reasoning_tokens"]) for row in attempts)
    if total_score == 0:
        return Efficiency(ZERO, 0.0)
    if total_tokens == 0:
        return Efficiency(UNBOUNDED, None)
    return Efficiency(FINITE, 1000.0 * total_score / total_tokens)
