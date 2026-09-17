# Living Plan (SSoT)

**Objective**: Establish one executable scoring contract and fix correctness gating, aggregate speedup, and reasoning-efficiency handling at every consuming seam.
**Status**: Completed

---

## Contract to Make Authoritative

Each attempt persists only source facts produced by the evaluator and runner:

- `verification_status`: `verified | incorrect | unproven | invalid | evaluator_error`
- `baseline_throughput` and `candidate_throughput`: present only for verified attempts
- `reasoning_tokens`: non-negative integer or null; retained for every attempt, including failures

Correctness and task score are never persisted. They are derived as `verification_status == verified` and `baseline_throughput / candidate_throughput` respectively; non-verified attempts derive score `0.0`.

Aggregate metrics have distinct, explicit populations:

- `verification_rate`: verified attempts / all attempts
- `geomean_task_score_verified`: geometric mean of derived scores from verified attempts only
- `mean_score_with_failures`: arithmetic mean of normalized scores across all attempts
- `reasoning_tokens_per_score_all_attempts`: sum of known reasoning tokens across all attempts / sum of normalized scores; null when token coverage is incomplete or total score is zero
- `reasoning_token_coverage`: attempts with known reasoning tokens / all attempts

The manifest documents these names and populations, but executable normalization/validation code is the runtime SSoT.

---

## Active Milestone
- [x] **Milestone 9 — Make run completion explicit and fail closed**
  - Write a completion attestation only after every planned attempt has emitted exactly one validated row.
  - Bind the attestation to the run id, current benchmark version, exact attempt count, and results-file digest.
  - Make the scorer require `run.json`, the completion attestation, exact plan coverage, and a matching digest.
  - Raise on missing/incomplete/interrupted artifacts; never synthesize absent tasks or aggregate partial rows.

---

## Milestone Backlog
- None.

---

## Completed Milestones
- [x] **Milestone 0 — Root-cause review**: Located independent policy interpretations in Alive2 gating, geometric-mean aggregation, and token-efficiency filtering.
- [x] **Milestone 1 — Lock the contract with regression fixtures**
  - Add focused fixtures/tests for: verified equivalence, Alive2 counterexample, failed-to-prove, zero matched functions, invalid IR, and evaluator failure.
  - Add aggregation fixtures for: all-correct, mixed success/failure, all-failed, missing token usage, and a token-expensive failure.
  - Assert invariants once: non-verified implies `correct=false` and `score=0`; verified implies a finite positive score.
  - Preserve the two demonstrated regressions (`ret i32 0` and renamed `@kernel`) as permanent fixtures.
- [x] **Milestone 2 — Make Alive2 fail closed**: Strictly classified one-function summaries, added timeouts, and verified all non-proof paths produce zero-score outcomes.
- [x] **Milestone 3 — Centralize attempt normalization**: Added `contracts.py`; verifier, runner, and scorer now validate the same coupled status/correctness/score invariants.
- [x] **Milestone 4 — Separate aggregate populations explicitly**: Correct-only geomean and failure-inclusive mean now use explicit populations; duplicate/mixed/incomparable result sets are rejected.
- [x] **Milestone 5 — Make efficiency include failed work**: All-attempt token cost, token coverage, and comparable adjacent-tier marginal efficiency are implemented; 21 focused tests pass.
- [x] **Milestone 6 — Align documentation and invalidate bad runs**: Versioned the manifest/result contract to v2, synchronized metric definitions, and marked all v0.1 runs invalid.
- [x] **Milestone 7 — Targeted validation and handoff**: 22 focused tests, six reference self-checks, schema validation, compilation, and diff hygiene all pass.
- [x] **Milestone 8 — Eliminate remaining secondary authorities**: Removed persisted derived fields and parallel schema versioning; exact current-version rows now fail closed on missing, unknown, or contradictory facts.
- [x] **Milestone 9 — Make run completion explicit and fail closed**: Added atomic digest-bound completion attestations and exact plan coverage; interrupted, partial, duplicated, or mutated runs raise before aggregation.
- [x] **Milestone 10 — Make the defined-input contract executable**: Declared Alive2's `--disable-undef-input` policy once in the manifest, loaded it from the verifier, and confirmed the minimal Luna/Low run completes.

---

## Decision Log & Deviations
- **2026-09-17**: The executable normalizer will be the runtime SSoT; prose/schema mirror it and regression tests enforce equivalence.
- **2026-09-17**: Correct-only speedup and failure-inclusive quality/efficiency remain separate metrics so their populations cannot be confused.
- **2026-09-17**: Existing results cannot be repaired from stored `correct=true` alone because the runner discarded Alive2 proof diagnostics; affected runs must be invalidated or re-verified from saved candidates.
- **2026-09-17**: The parallel result-schema version channel was removed; the scorer accepts only the current `benchmark_version` read from the manifest.
- **2026-09-17**: SSoT correction: strict validation of redundant fields is still weaker than having no redundant persisted fields. Remove the mirrors rather than maintaining them.
- **2026-09-17**: Missing usage and candidate hashes are represented as `null`; zero values and all-zero hashes are not used as unknown-value sentinels.
- **2026-09-17**: A task failure is a completed zero-score attempt; a missing attempt is a failed run and is never scored.
- **2026-09-17**: The Luna/Low `ctpop` candidate failed because Alive2 timed out while modeling undef inputs. It proves when `--disable-undef-input` is used, but changing that semantic domain requires an explicit benchmark-contract decision and was not done implicitly.
- **2026-09-17**: The benchmark contract now explicitly selects defined external inputs with manifest `toolchain.alive2_args=["--disable-undef-input"]`; the strict Alive2 summary gate remains unchanged.
