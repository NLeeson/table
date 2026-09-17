# Living Scratchpad (SSoT)

**Current Milestone Context**: Complete — approved fail-closed timeout handling implemented and validated.
**Timestamp**: 2026-09-18

---

## 1. Shortest Causal Chain & Working Hypotheses
- **Timeout Query**: `benchmark/run_codex.py --timeout` is passed to `subprocess.run` around the Codex process. Expiry kills Codex, sets `timeout_error`, and thereby prevents response parsing and verification. The base row remains `invalid`, with derived score zero.
- **Evaluator Timeout**: `evaluator/verify.py --tool-timeout` defaults to 60 seconds per LLVM/Alive2/MCA subprocess. Expiry returns `evaluator_error`, with no throughput and score zero.
- **New Root Cause**: `subprocess.TimeoutExpired.stdout` and `.stderr` are bytes when captured, even under `text=True`. The runner assigns those values directly and calls `Path.write_text`, which requires strings. A timeout after partial output therefore raises `TypeError` before a result row or completion attestation can be written.
- **Observability Gap**: Timeout provenance is represented only by free-text `error`; there is no typed failure-stage/reason field. Existing stored result rows contain zero timeout error matches.
- **As-Is Boundary**: Arbitrary in-progress reasoning is not a candidate IR. Only a complete schema-valid candidate materialized before/at the deadline could be verified; current code rejects it whenever a timeout occurred.
- **Implemented Outcome**: `invoke_codex` normalizes timeout bytes, partial event/stderr logs are durable, and new timeout rows carry conditional `timeout_stage` provenance (`model` with `invalid`; `evaluator` with `evaluator_error`). `run.json` freezes `model_timeout_seconds`. Historical rows need no rewrite.
- **Current Query**: Increasing stochastic samples per task is not exposed by a runner parameter. The CLI enumerates one call for every model/effort/task product, and the scorer forbids duplicate `(run_id, model, effort, task)` attempts.
- **Current Recommendation**: Launch the same plan multiple times with unique `--run-id` values, then analyze samples across those completed runs; implementing an in-run repeat count would require adding a replicate identity throughout metadata, filenames, completion validation, scoring, and comparison.
- **Observed Behavior**: Normal-client Terra Low has verified scores `1` and `9.285714...` at `0` and `90` reasoning tokens plus an incorrect scan at score/token `0/0`. Its aggregate `1000 * sum(score) / sum(tokens) = 114.285714...`; removing the failed scan yields exactly the same value. Terra High analogously yields `97.035...` from 106 tokens.
- **Root Responsibility**: `evaluator/score.py` defines efficiency as a ratio of totals. A zero-score/zero-token task is the additive identity in both totals, so the statistic cannot observe the failure even though `task_score()` correctly returns zero.
- **Working Hypothesis**: Confirmed. Tagged task outcomes and paired Pareto comparison retain task identity, so a zero-score/zero-token failure cannot disappear into pooled totals.

---

## 2. Targeted Evidence & Symbols
- `benchmark/run_codex.py:334-398`: timeout capture, log persistence, and the `error is None` gates that skip candidate parsing/evaluation.
- `evaluator/verify.py:86-168`: independent 60-second evaluator-tool deadlines map to `evaluator_error`.
- `evaluator/contracts.py:17-50`: exact result contract has a free-text `error` but no typed failure provenance.
- `.codex/0/logs/timeout-expired-types.txt`: focused reproduction shows captured stdout/stderr are bytes and `Path.write_text` raises `TypeError`.
- `.codex/0/logs/timeout-results.tsv`: bounded scan found zero timeout-tagged historical result rows.
- `.codex/0/logs/milestone15-focused-tests.txt`: 34 focused runner, scorer/contract, and verifier tests pass.
- `.codex/0/logs/milestone15-schema-validation.txt`: 147 current-version historical rows and both timeout variants validate; mismatched timeout/status pairs are rejected.
- `.codex/0/logs/milestone15-existing-run-score.json`: existing completed run still scores unchanged.
- `benchmark/run_codex.py:192-226`: complete runner argument list; no repeats/samples option, and duplicate model/effort pairs are rejected.
- `benchmark/run_codex.py:296-308`: exactly one invocation and one artifact path per model/effort/task.
- `evaluator/score.py:33-53`: duplicate attempt identity is rejected and mixed run IDs cannot be scored together.
- `.codex/0/logs/run-codex-help.txt`: captured bounded CLI help output.
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
- [x] Implement approved Strategy 1 and preserve the hard-timeout/zero-score policy.
- [x] Add model-timeout end-to-end persistence and evaluator-timeout JSON regressions.
- [x] Validate schema compatibility, existing-run scoring, compilation, and diff hygiene.
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
