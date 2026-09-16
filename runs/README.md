# Runs

Store raw experiment outputs here, preferably one directory per run id.

Recommended shape:

```text
runs/<run_id>/
  run.json
  results.jsonl
  candidates/
    <task_id>.ll
```

`run.json` should freeze the model/config matrix, benchmark manifest commit, generated task set, toolchain versions, pricing snapshot (if cost is reported), and invocation parameters.

Do not overwrite prior runs. New benchmark/toolchain/model settings should produce a new run id so historical comparisons remain auditable.
