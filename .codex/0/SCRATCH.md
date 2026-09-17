# Living Scratchpad (SSoT)

**Current Milestone Context**: Complete — approved Strategy 3 implemented and validated.
**Timestamp**: 2026-09-17

---

## 1. Shortest Causal Chain & Working Hypotheses
- **Observed Behavior**: Normal-client Terra Low has verified scores `1` and `9.285714...` at `0` and `90` reasoning tokens plus an incorrect scan at score/token `0/0`. Its aggregate `1000 * sum(score) / sum(tokens) = 114.285714...`; removing the failed scan yields exactly the same value. Terra High analogously yields `97.035...` from 106 tokens.
- **Root Responsibility**: `evaluator/score.py` defines efficiency as a ratio of totals. A zero-score/zero-token task is the additive identity in both totals, so the statistic cannot observe the failure even though `task_score()` correctly returns zero.
- **Working Hypothesis**: Confirmed. Tagged task outcomes and paired Pareto comparison retain task identity, so a zero-score/zero-token failure cannot disappear into pooled totals.

---

## 2. Targeted Evidence & Symbols
- `evaluator/contracts.py`: executable outcome invariants and result schema version.
- `evaluator/verify.py`: strict Alive2 summary classification, explicit function selection, and subprocess timeouts.
- `evaluator/score.py`: validated result sets, correct-only geomean, failure-inclusive score, and all-attempt reasoning efficiency.
- `runs/luna-terra-lhm-hard3/results.jsonl`: Terra Low/High each contain one incorrect scan with zero reasoning tokens; Low's other tasks have scores 1 and 9.285714... with only 90 total reasoning tokens.
- `.codex/0/logs/hard3-normal-rows.json`: bounded projection of the authoritative normal-client hard-3 rows.
- `.codex/0/logs/hard3-bare-rows.json`: bounded projection of the authoritative modified-client hard-3 rows.
- `evaluator/metrics.py`: authoritative tagged efficiency and task-outcome comparison domain.
- `evaluator/compare.py`: completed-run pairing, comparability checks, per-task deltas, and win/loss/tie/trade-off/unknown summaries.
- `.codex/0/logs/milestone13-focused-tests.txt`: 29 focused tests pass.
- `.codex/0/logs/milestone13-hard3-compare.json`: real normal/modded-client paired output; all 18 task pairs accounted for.
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
- [x] Trace completion state and every score/efficiency consumer.
- [x] Demonstrate the precise false-positive calculation.
- [x] Present three strategies and wait for approval per root-cause protocol.
- [x] After approval, implement only the selected representation and focused tests.
- [x] Confirm tagged output is strict JSON with no `NaN`/`Infinity` values.
- [x] Reproduce Terra pooled values without changing historical run artifacts.
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
- [ ] Add completion attestation, exact plan-coverage validation, and interrupted-run regressions.
- [x] Add completion attestation, exact plan-coverage validation, and interrupted-run regressions.
- [x] Diagnose Luna/Low failure: default 10-second and raised 30-second Alive2 SMT budgets time out; disabling only undef-input modeling proves the `ctpop` rewrite in about four seconds.
- [x] Final validation: 28 focused tests, 6/6 smoke checks, compilation, and diff hygiene pass.
- [ ] Decide whether partial token coverage should make the all-attempt efficiency metric null (planned default) or be reported as a partial metric.
- [ ] Decide whether saved candidates from affected runs should be batch re-verified or the runs should simply be marked invalid.
- [x] Make the defined-input policy executable from the manifest; the saved Luna/Low `ctpop` candidate now verifies and the one-task runner completes.
