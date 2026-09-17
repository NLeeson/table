# Living Scratchpad (SSoT)

**Current Milestone Context**: Complete.
**Timestamp**: 2026-09-17

---

## 1. Shortest Causal Chain & Working Hypotheses
- **Observed Behavior**: Failure semantics had been independently encoded at three seams: Alive2 process handling, speedup aggregation, and reasoning-efficiency filtering.
- **Root Responsibility**: Resolved by `evaluator/contracts.py`, consumed by verifier, runner, smoke gate, and scorer.
- **Working Hypothesis**: Confirmed: fail-closed verification and explicit metric populations eliminate the contradictory interpretations.

---

## 2. Targeted Evidence & Symbols
- `evaluator/contracts.py`: executable outcome invariants and result schema version.
- `evaluator/verify.py`: strict Alive2 summary classification, explicit function selection, and subprocess timeouts.
- `evaluator/score.py`: validated result sets, correct-only geomean, failure-inclusive score, and all-attempt reasoning efficiency.
- `evaluator/tests/`: permanent wrong-result, renamed-function, invalid-IR, contract, aggregate, and integration regressions.
- Historical evidence retained below:
- `.codex/0/logs/verify-wrong.json`: deliberately wrong `ret i32 0` candidate received `correct=true`, score `4.5`.
- `.codex/0/logs/verify-renamed.json`: candidate with no matching `@kernel` received `correct=true`, score `4.5`.
- `.codex/0/logs/alive-candidate-audit.txt:1-4`: saved rows reported as correct include two Alive2 failures-to-prove and one incorrect transformation.
- `.codex/0/logs/final-unit-tests.txt`: 22 focused tests pass.
- `.codex/0/logs/final-smoke.txt`: 6/6 frozen references verify with score 1.0.
- `.codex/0/logs/ssot-audit.diff`: audit showing persisted `correct`, `speedup`, `score`, parallel schema versioning, and permissive result-schema paths.

---

## 3. Pending Actions & Edge Cases
- [x] Contract, aggregate, and verifier regression tests added and observed failing against the old implementation.
- [x] Implement strict Alive2 summary parsing and failure classification.
- [x] Focused contract/verifier tests: 13 passed.
- [x] Wire runner and scorer to `evaluator/contracts.py` and reject contradictions.
- [x] Compilation, 13 focused tests, and runner dry-run pass after shared-contract wiring.
- [x] Restore correct-only geomean and enforce comparable input sets; four focused aggregation tests pass.
- [x] Replace successful-only mean token ratio with all-attempt ratio and coverage.
- [x] All 21 focused evaluator tests pass.
- [x] Version manifest/result rows, update metric documentation, and mark affected runs invalid.
- [x] Run targeted tests, reference smoke gate, compilation, schema, and diff checks.
- [x] Remove redundant outcome/performance fields and permissive schema paths in Milestone 8.
- [x] Final validation: 24 focused tests, 6/6 reference smoke checks, closed-schema checks, compilation, and diff hygiene pass.
- [ ] Decide whether partial token coverage should make the all-attempt efficiency metric null (planned default) or be reported as a partial metric.
- [ ] Decide whether saved candidates from affected runs should be batch re-verified or the runs should simply be marked invalid.
