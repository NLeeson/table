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
2. `alive-tv` checks candidate refinement/equivalence against the reference.
3. Reference and candidate are lowered with the same frozen LLVM version and flags.
4. `llvm-mca` estimates throughput for the same fixed CPU model.
5. Incorrect/invalid candidates receive a score of `0`.

For a correct candidate:

```text
speedup = baseline_throughput / candidate_throughput
score   = speedup
```

Aggregate optimization quality should use the geometric mean across tasks, with failed tasks contributing zero to correctness reporting and being tracked separately from the geomean of valid speedups.

## Reasoning-efficiency metrics

The raw run records retain input, reasoning, and output tokens. The primary reciprocal efficiency metric is:

```text
tokens_per_score = reasoning_tokens / score
```

Lower is better. Across adjacent reasoning tiers we also track:

```text
marginal_tokens_per_score = delta(reasoning_tokens) / delta(score)
```

This makes diminishing returns from Medium -> High -> xHigh -> Max directly visible.

## Repository layout

```text
benchmark/
  manifest.json          benchmark/toolchain contract
  tasks/                 generated task instances
  generators/            task-family generators

evaluator/
  verify.py              LLVM + Alive2 correctness gate
  mca.py                 llvm-mca parsing/helpers
  score.py               result aggregation and efficiency metrics

runs/                    raw model outputs / run JSONL
results/
  schema.json            run-result schema
```

## Result record

Each model/task attempt should record at least:

- model
- reasoning effort
- task id
- correctness
- baseline and candidate throughput
- speedup / score
- input tokens
- reasoning tokens
- output tokens
- latency
- cost, when available
- raw candidate IR path or content hash

See `results/schema.json`.

## v0 task families

The initial target is 24 tasks: four generated instances each of reductions, prefix/scan, sorting/selection, bit manipulation, vector arithmetic, and permutation/data movement.

Functions should remain pure and bounded: no globals, no external calls, no inline assembly, and no hidden work outside the function. v0 should prefer generic LLVM IR over target-specific intrinsics.

## Tooling contract

The benchmark is only comparable when these are pinned and recorded:

- LLVM version
- Alive2 version/commit
- target triple
- `llc` flags
- `llvm-mca` CPU model
- benchmark manifest version
- generator seed

`benchmark/manifest.json` is the canonical experiment contract.

## Status

Early scaffold. The next milestone is a 4-6 task proof-of-concept that can run end-to-end before expanding to the full generated suite.
