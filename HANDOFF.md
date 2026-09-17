You are continuing development of the `NLeeson/table` repository.

The project is a small deterministic benchmark for measuring how efficiently model reasoning budget converts into semantic-preserving LLVM IR optimization quality.

## Core benchmark contract

A model receives one LLVM IR function and must return a semantically equivalent but faster LLVM IR implementation.

Evaluation pipeline:

1. Candidate must parse with `llvm-as`.

2. Alive2 verifies semantic correctness/refinement.

3. Reference and candidate are lowered using the same frozen LLVM toolchain.

4. `llvm-mca` measures `Block RThroughput` for the fixed CPU model.

5. Verified task score:

   `score = baseline_throughput / candidate_throughput`

6. Any invalid, incorrect, unproven, or evaluator-error attempt gets:

   `score = 0`

Never remove failed attempts from aggregate statistics.

Current toolchain contract is pinned in `benchmark/manifest.json`.

Current target is x86-64 Haswell / AVX2 intent.

## Important scoring semantics

A major previous mistake was allowing failed attempts to disappear from an efficiency calculation. Never do this.

Every configured task remains part of the result set.

A failed attempt has score `0`.

The reasoning-efficiency direction ultimately desired is:

`score / reasoning_tokens`

Prefer displaying this as:

`score per 1000 reasoning tokens`

For a failed task:

`0 / reasoning_tokens = 0`

This is intentional.

Do not interpret large token consumption on a failed task as evidence of proportionally worse reasoning. The trajectory is censored: we do not know whether progress was efficient before the blocking failure or what additional token budget would have done.

The current scorer still contains reciprocal metrics such as `reasoning_tokens_per_score_all_attempts` and marginal token-per-score values. Do not silently alter historical raw data. Scoring code may be corrected later because all metrics are derived from immutable run records.

When revising scoring, preserve raw quantities and preferably report both directions with unambiguous names if useful, but make `score_per_reasoning_token` / `score_per_1k_reasoning_tokens` the primary reasoning-efficiency measure.

## Raw data is authoritative

Do not rewrite, normalize, purge, or retroactively modify existing benchmark run data.

`runs/*/results.jsonl`, candidate IR, event JSONL, stderr, run metadata, and completion attestations are primary experimental evidence.

Scoring output is derived and may be recomputed later.

Never change scoring semantics in the middle of an experimental comparison without preserving the old raw run.

## Existing benchmark tasks

Current POC contains six tasks from distinct families.

The three most discriminative tasks discovered so far are:

* `reductions_sum8_i32`
* `scans_prefix8_i32`
* `vector_arithmetic_clamp8_i32`

The scan task is especially useful because weaker configurations sometimes produce invalid or semantically incorrect IR.

The vector clamp task can expose very large optimizations.

The reduction task distinguishes stronger reasoning levels after easier transformations saturate.

## Codex runner

`benchmark/run_codex.py` drives Codex CLI.

It must:

* start a fresh ephemeral session for every task/configuration;
* explicitly pin model;
* explicitly pin reasoning effort;
* use a fresh temporary working directory;
* ignore user/project rules/config where supported;
* disable web search;
* forbid benchmark-relevant tool use;
* capture structured output;
* preserve Codex event JSONL;
* preserve candidate IR;
* record token usage and latency;
* evaluate candidate through the frozen evaluator;
* append canonical result rows;
* attest completed runs.

Forbidden agent actions such as shell execution, file edits, MCP/plugin usage, subagents, or web search must invalidate an attempt if they occur.

The model should reason only from the IR supplied in the prompt.

Previous run results on disk do not need to be purged because each model attempt is isolated in a fresh temporary working directory and tool access is prohibited.

Long-term benchmark contamination is a separate concern. Eventually generated hidden/random task instances should be used rather than relying indefinitely on public fixed tasks.

## CLI UX issue

Current behavior:

omitting `--task` means “run all tasks”.

This was found unintuitive.

Improve the interface later so full-suite execution is explicit, e.g.:

`--all-tasks`

Potentially require exactly one of:

* one or more `--task`
* `--all-tasks`

Do not make this change while an important experimental run is in progress.

## Current experimental findings

Do not encode these as benchmark assumptions; they are observations from very small samples.

On the three hard tasks, using the normal Codex client:

Luna:

* Low: many failures
* High: solved all three
* Max: solved all three with only modest quality improvement over High and substantially more reasoning tokens

Terra:

* Low/High failed scan
* Max solved all three
* Max appeared more justified for Terra than for Luna

A modified Codex client invoked roughly as:

`codex --bare --orch`

was compared against the normal client.

On identical model/effort/task configurations, it sometimes substantially reduced reasoning-token usage while preserving score.

Notably:

* Luna High achieved identical quality with roughly half the reasoning tokens in one paired run.
* Luna Max and Terra Max also used fewer reasoning tokens for identical quality.
* Luna Low with the modified client solved tasks that the normal-client Luna Low run failed.

These are single stochastic samples, not established causal conclusions.

Future comparisons should use paired configurations and repeated runs.

## Experimental methodology

For client comparisons:

Hold fixed:

* model
* reasoning effort
* benchmark tasks
* prompt version
* LLVM version
* Alive2 revision
* CPU target
* evaluation code

Change only the client implementation/configuration.

Prefer paired analysis per task instead of relying only on aggregates.

Record at minimum:

* verification status
* task score
* reasoning tokens
* input tokens
* output tokens
* latency
* candidate hash
* client version/configuration

Do not infer too much from one stochastic generation.

Repeated paired runs are preferable once infrastructure issues are resolved.

## Result-set invariants

The scorer should reject malformed datasets.

Maintain these invariants:

* one canonical result per `(run_id, model, effort, task)`;
* all compared configurations in one run use the same task set;
* result rows match `run.json`;
* benchmark version matches;
* result file completion hash matches;
* verified attempts require positive baseline and candidate throughput;
* non-verified attempts must not pretend to contain valid throughput measurements;
* non-verified task score derives to zero;
* no duplicate configurations;
* no partial run should silently appear as a complete benchmark result.

Do not replace explicit verification statuses with a generic boolean if richer status information already exists.

## Near-term development priorities

Work incrementally. Avoid spending minutes on large runs before testing changes on one task.

Recommended order:

1. Preserve all existing runs unchanged.

2. Add unit tests for scoring semantics:

   * verified task gets throughput ratio;
   * invalid task gets zero;
   * incorrect task gets zero;
   * failed task remains in aggregate;
   * score/token for failure is zero;
   * configurations with mismatched task sets are rejected;
   * missing reasoning-token data is surfaced explicitly.

3. Correct efficiency naming/orientation:

   * primary: score per reasoning token;
   * convenient display: score per 1k reasoning tokens;
   * define marginal efficiency carefully as `delta score / delta reasoning tokens`;
   * handle negative/zero token deltas explicitly instead of manufacturing a value.

4. Improve CLI task selection:

   * explicit `--all-tasks`;
   * no accidental six-task run from omission.

5. Add a comparison utility, for example:

   `evaluator/compare.py RUN_A/results.jsonl RUN_B/results.jsonl`

   It should pair rows by:
   `(model, reasoning_effort, task_id)`

   and report:

   * score A/B/delta
   * verification A/B
   * reasoning tokens A/B/delta/percentage
   * score per 1k reasoning tokens A/B
   * latency A/B
   * aggregate paired statistics

6. Make client identity first-class in metadata.
   Current model/effort are insufficient for comparing stock vs modified Codex.

   Add something like:

   * `client_label`
   * complete executable/version information
   * fixed client arguments

   Avoid encoding client identity only into `run_id`.

7. Add tests before expanding from 6 tasks to 24.

8. Once infrastructure is stable, implement generated task variants using seeds to improve contamination resistance.

## Development style

Prefer simple, auditable Python with minimal dependencies.

Do not introduce large frameworks unless they solve a demonstrated problem.

Every benchmark semantic decision should be explicit and machine-checkable.

Avoid “helpful” behavior that hides failures.

A benchmark failure is data.

Fail closed when correctness or provenance is uncertain.

Use tiny POC executions before expensive model sweeps.

When changing the benchmark contract, bump the appropriate benchmark/prompt/schema version rather than silently changing interpretation.

## Immediate recommended task

Before adding more benchmark families, implement and test the paired run comparison utility plus corrected score-per-token metrics.

Do not modify historical run files.

Run unit tests using synthetic result rows first.

Then validate on the existing normal-vs-`--bare --orch` hard-3 runs.

The desired output should make it immediately obvious whether one client/model/effort achieved:

* higher semantic success rate;
* higher optimization score;
* fewer reasoning tokens;
* higher score per 1k reasoning tokens;
* lower latency;

without collapsing these distinct dimensions into one opaque overall number.

