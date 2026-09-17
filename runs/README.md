# Runs

Store raw experiment outputs here, preferably one directory per run id.

Recommended shape:

```text
runs/<run_id>/
  run.json
  results.jsonl
  completed.json
  candidates/
    <task_id>.ll
```

`run.json` should freeze the model/config matrix, benchmark manifest commit, generated task set, toolchain versions, pricing snapshot (if cost is reported), and invocation parameters.

`completed.json` is written atomically after exact plan coverage is validated. It binds the run id, benchmark version, attempt count, and `results.jsonl` digest. Its absence means the run is incomplete; the scorer must raise instead of aggregating partial rows.

Do not overwrite prior runs. New benchmark/toolchain/model settings should produce a new run id so historical comparisons remain auditable.

## Invalid v0.1 results

All benchmark-version `0.1.0` runs in this repository are invalid for correctness and score comparison. Their evaluator treated `alive-tv` process success as proof, but the pinned Alive2 executable returns status zero for counterexamples, failures-to-prove, and zero matched functions. These runs must not be passed through the current scorer or presented as benchmark results.

Saved candidates may be re-verified under benchmark `0.2.0`, but that produces a new run/result record; historical JSONL files remain immutable audit artifacts.
