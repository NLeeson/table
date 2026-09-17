# table

A small, deterministic benchmark for measuring how efficiently reasoning budget turns into coding/optimization quality.

The first benchmark target is **semantic-preserving LLVM IR optimization**. A model receives a self-contained LLVM IR function and returns a semantically equivalent, faster function. Correctness is a hard gate; performance is scored with a fixed LLVM toolchain and CPU model.

## Goals

- **Quantifiable** — one numeric optimization score per task.
- **Straightforward evaluation** — parse, verify, prove/refute equivalence, lower, estimate throughput.
- **Deterministic** — fixed toolchain, flags, target CPU, generated task seeds, and static throughput model.
- **Contamination-resistant** — task families generate fresh concrete instances from seeds.
- **Fast** — small pure functions; no application harness or noisy wall-clock timing.
- **Reasoning-efficiency aware** — retain reasoning-token usage so quality can be normalized by inference budget.

## Evaluation pipeline

For each task:

1. `llvm-as` / verifier accepts the candidate IR.
2. `alive-tv` checks candidate refinement/equivalence against the reference using the manifest's explicit input-domain flags. The evaluator requires exactly one correct transformation and rejects counterexamples, failures-to-prove, Alive2 errors, malformed summaries, and zero matched functions.
3. Reference and candidate are lowered with the same frozen LLVM version and flags.
4. `llvm-mca` estimates throughput for the same fixed CPU model.
5. Incorrect/invalid candidates receive a score of `0`.

For a correct candidate:

```text
task_score = baseline_throughput / candidate_throughput
```

Aggregate optimization quality uses `geomean_task_score_verified`, the geometric mean of verified task scores only. `mean_score_with_failures` is the separate failure-inclusive quality metric; it averages every derived task score, including zero for every non-verified attempt.

## Reasoning-efficiency metrics

The raw run records retain input, reasoning, and output tokens for successful and failed attempts. The primary reciprocal efficiency metric is:

```text
reasoning_tokens_per_score_all_attempts =
    sum(reasoning_tokens for every attempt) / sum(normalized task scores)
```

Lower is better. Failed attempts therefore retain their token cost in the numerator. The metric is `null` if any attempt lacks reasoning-token usage or if the total earned score is zero; `reasoning_token_coverage` reports completeness. Across adjacent available reasoning tiers we also track:

```text
marginal_reasoning_tokens_per_score =
    delta(mean reasoning tokens) / delta(mean score with failures)
```

This makes diminishing returns from Medium -> High -> xHigh -> Max directly visible.

## Repository layout

```text
benchmark/
  manifest.json                benchmark/toolchain contract
  codex_output.schema.json     structured Codex response contract
  codex_matrix.example.json    example model/reasoning matrix
  run_codex.py                 Codex CLI experiment runner
  tasks/                       generated task instances
  generators/                  task-family generators

evaluator/
  verify.py                    LLVM + Alive2 correctness gate
  mca.py                       llvm-mca parsing/helpers
  score.py                     result aggregation and efficiency metrics
  smoke_all.py                 reference-vs-reference smoke gate

runs/                          raw model outputs / run JSONL
results/
  schema.json                  run-result schema
```

## Smoke gate

Before model runs, verify all six current references against themselves:

```bash
python3 evaluator/smoke_all.py
```

The expected result is `6/6` correct with score `1.0`.

## Minimal Codex POC: one call

Do **not** start with the full matrix. First exercise exactly one already-smoke-tested task, one model, and one reasoning level:

```bash
python3 benchmark/run_codex.py \
  --model gpt-5.6-luna \
  --effort high \
  --task bitops_popcount32 \
  --run-id poc-luna-high-bitops \
  --dry-run
```

The dry run should report exactly `1` planned Codex call. If that looks right, remove `--dry-run`:

```bash
python3 benchmark/run_codex.py \
  --model gpt-5.6-luna \
  --effort high \
  --task bitops_popcount32 \
  --run-id poc-luna-high-bitops
```

Then inspect only:

```text
runs/poc-luna-high-bitops/
  run.json
  results.jsonl
  candidates/
  responses/
  events/
  stderr/
```

This single-call POC is the gate before spending time on multiple efforts, models, or tasks.

## Codex CLI runner

`benchmark/run_codex.py` starts a fresh ephemeral Codex session for every task/configuration. It pins the model and reasoning effort explicitly, ignores user/project config and rules, disables web search, runs from a fresh temporary directory, captures the final answer through a JSON schema, and invalidates an attempt if the Codex JSONL stream shows shell commands, file edits, MCP/plugin calls, subagents, or web search.

Use `--codex` to select an alternative Codex executable and supply fixed arguments. The value is parsed with shell-style quoting and used as the command prefix for both `--version` and `exec` invocations:

```bash
python3 benchmark/run_codex.py \
  --codex '/path/to/codex1 --foo --bar baz' \
  --model gpt-5.6-luna \
  --effort high \
  --task bitops_popcount32 \
  --dry-run
```

Quote an executable path or argument again inside the value when it contains spaces, for example `--codex '"/path/with spaces/codex" --foo "two words"'`. Shell operators and expansions are not evaluated.

After the one-call POC passes, multiple `--model` and `--effort` flags form a Cartesian product. To inspect a larger plan without spending inference:

```bash
python3 benchmark/run_codex.py \
  --model gpt-5.6-luna \
  --model gpt-5.6-terra \
  --effort high \
  --effort max \
  --dry-run
```

Or use the example matrix:

```bash
python3 benchmark/run_codex.py \
  --matrix benchmark/codex_matrix.example.json \
  --dry-run
```

Each `results.jsonl` row contains verification and measurement source facts plus Codex token usage, including `reasoning_output_tokens` when exposed by the installed CLI. Aggregate a completed run with:

```bash
python3 evaluator/score.py runs/<run_id>/results.jsonl
```

The runner writes `completed.json` only after every `(model, reasoning effort, task)` in `run.json` has produced exactly one validated result row. The scorer requires that attestation, exact plan coverage, and a matching `results.jsonl` digest. An interrupted or partial run raises an error and is never aggregated; a completed non-verified attempt remains a derived zero-score result.

## Result record

Each model/task attempt records source facts rather than derived mirrors:

- model
- reasoning effort
- task id
- verification status (`verified`, `incorrect`, `unproven`, `invalid`, or `evaluator_error`)
- baseline and candidate throughput for verified attempts
- input tokens
- reasoning tokens
- output tokens
- latency
- cost, when available
- raw candidate IR path or content hash

Correctness (`verification_status == verified`) and task score are derived when results are consumed; neither is persisted in attempt rows.

See `results/schema.json`.

## v0 task families

The initial target is 24 tasks: four generated instances each of reductions, prefix/scan, sorting/selection, bit manipulation, vector arithmetic, and permutation/data movement.

Functions should remain pure and bounded: no globals, no external calls, no inline assembly, and no hidden work outside the function. v0 should prefer generic LLVM IR over target-specific intrinsics.

## Tooling contract

The benchmark is only comparable when these are pinned and recorded:

- LLVM version
- Alive2 version/commit
- Alive2 invocation flags (including the defined-input policy)
- target triple
- `llc` flags
- `llvm-mca` CPU model
- benchmark manifest version
- generator seed

`benchmark/manifest.json` is the canonical experiment contract.

## Status

The six-task proof-of-concept, deterministic evaluator, smoke gate, and Codex CLI runner are scaffolded. The immediate gate is the one-call `bitops_popcount32` Luna/High POC above; only after that succeeds should the experiment expand to additional efforts, models, or tasks.
