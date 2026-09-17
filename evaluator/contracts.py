"""Executable invariants for benchmark attempt outcomes."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

VERIFIED = "verified"
REASONING_EFFORTS = ("none", "low", "medium", "high", "xhigh", "max")
VERIFICATION_STATUSES = frozenset(
    {VERIFIED, "incorrect", "unproven", "invalid", "evaluator_error"}
)
RESULT_REQUIRED_FIELDS = frozenset(
    {
        "benchmark_version",
        "run_id",
        "model",
        "reasoning_effort",
        "task_id",
        "task_seed",
        "verification_status",
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "reasoning_tokens",
        "output_tokens",
        "latency_ms",
        "cost_usd",
        "candidate_sha256",
        "candidate_ir_path",
        "llvm_version",
        "alive2_revision",
        "target_triple",
        "mcpu",
        "codex_version",
        "prompt_version",
        "events_path",
        "forbidden_tool_types",
        "jsonl_parse_errors",
        "error",
    }
)
RESULT_OPTIONAL_FIELDS = frozenset(
    {"baseline_throughput", "candidate_throughput", "alive2_summary"}
)
RESULT_FIELDS = RESULT_REQUIRED_FIELDS | RESULT_OPTIONAL_FIELDS
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Raised when an attempt contradicts the benchmark result contract."""


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ContractError(f"{field} must be finite")
    return number


def verification_fields(status: str) -> dict[str, str]:
    """Create the sole persisted correctness fact."""
    if status not in VERIFICATION_STATUSES:
        raise ContractError(f"unknown verification_status: {status!r}")
    return {"verification_status": status}


def validate_attempt(row: Mapping[str, Any]) -> None:
    """Validate one attempt against the canonical status/measurement contract."""
    status = row.get("verification_status")
    if not isinstance(status, str):
        raise ContractError("verification_status is required")
    verification_fields(status)

    throughput_fields = ("baseline_throughput", "candidate_throughput")
    if status == VERIFIED:
        for field in throughput_fields:
            if _finite_number(row.get(field), field) <= 0:
                raise ContractError(f"{field} must be positive")
    else:
        present = [field for field in throughput_fields if field in row]
        if present:
            raise ContractError(
                f"non-verified attempt must not contain throughput fields: {present!r}"
            )

    reasoning_tokens = row.get("reasoning_tokens")
    if reasoning_tokens is not None and (
        isinstance(reasoning_tokens, bool)
        or not isinstance(reasoning_tokens, int)
        or reasoning_tokens < 0
    ):
        raise ContractError("reasoning_tokens must be a non-negative integer or null")


def task_score(row: Mapping[str, Any]) -> float:
    """Derive the only task score from canonical status and measurements."""
    validate_attempt(row)
    if row["verification_status"] != VERIFIED:
        return 0.0
    return float(row["baseline_throughput"]) / float(row["candidate_throughput"])


def validate_result_row(row: Mapping[str, Any], *, benchmark_version: str) -> None:
    """Validate the exact persisted result-row contract."""
    validate_attempt(row)
    fields = frozenset(row)
    missing = RESULT_REQUIRED_FIELDS - fields
    unknown = fields - RESULT_FIELDS
    if missing:
        raise ContractError(f"missing result fields: {sorted(missing)!r}")
    if unknown:
        raise ContractError(f"unknown result fields: {sorted(unknown)!r}")
    if row["benchmark_version"] != benchmark_version:
        raise ContractError(f"benchmark_version must be {benchmark_version!r}")

    for field in ("run_id", "model", "task_id", "events_path"):
        if not isinstance(row[field], str) or not row[field]:
            raise ContractError(f"{field} must be a non-empty string")
    if row["reasoning_effort"] not in REASONING_EFFORTS:
        raise ContractError(f"invalid reasoning_effort: {row['reasoning_effort']!r}")
    task_seed = row["task_seed"]
    if isinstance(task_seed, bool) or not isinstance(task_seed, (int, str)):
        raise ContractError("task_seed must be an integer or string")

    for field in (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
    ):
        value = row[field]
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value < 0
        ):
            raise ContractError(f"{field} must be a non-negative integer or null")
    parse_errors = row["jsonl_parse_errors"]
    if (
        isinstance(parse_errors, bool)
        or not isinstance(parse_errors, int)
        or parse_errors < 0
    ):
        raise ContractError("jsonl_parse_errors must be a non-negative integer")

    if _finite_number(row["latency_ms"], "latency_ms") < 0:
        raise ContractError("latency_ms must be non-negative")
    cost = row["cost_usd"]
    if cost is not None and _finite_number(cost, "cost_usd") < 0:
        raise ContractError("cost_usd must be non-negative or null")
    candidate_sha256 = row["candidate_sha256"]
    if candidate_sha256 is not None and (
        not isinstance(candidate_sha256, str) or not _SHA256.fullmatch(candidate_sha256)
    ):
        raise ContractError("candidate_sha256 must be a lowercase SHA-256 digest or null")

    for field in ("candidate_ir_path", "codex_version"):
        if row[field] is not None and not isinstance(row[field], str):
            raise ContractError(f"{field} must be a string or null")
    for field in ("llvm_version", "alive2_revision", "target_triple", "mcpu", "prompt_version"):
        if not isinstance(row[field], str) or not row[field]:
            raise ContractError(f"{field} must be a non-empty string")
    if not isinstance(row["forbidden_tool_types"], list) or not all(
        isinstance(value, str) for value in row["forbidden_tool_types"]
    ):
        raise ContractError("forbidden_tool_types must be an array of strings")
    if row["error"] is not None and not isinstance(row["error"], str):
        raise ContractError("error must be a string or null")
    if row["verification_status"] == VERIFIED:
        if row["error"] is not None:
            raise ContractError("verified result must not contain an error")
    elif not isinstance(row["error"], str) or not row["error"]:
        raise ContractError("non-verified result requires a non-empty error")

    summary = row.get("alive2_summary")
    if summary is not None:
        if not isinstance(summary, Mapping) or set(summary) != {
            "correct",
            "incorrect",
            "unproven",
            "errors",
        }:
            raise ContractError("alive2_summary has an invalid shape")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in summary.values()
        ):
            raise ContractError("alive2_summary counts must be non-negative integers")
