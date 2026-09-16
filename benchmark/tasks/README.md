# Tasks

Generated benchmark instances live here.

Each task directory should contain enough information to reproduce the exact prompt and evaluation input without relying on mutable external state. A recommended layout is:

```text
<task_id>/
  reference.ll
  task.json
```

`task.json` should record:

- task id and family
- generator version
- seed
- semantic parameters (width, lane count, signedness, permutation, constants, etc.)
- prompt template/version
- any task-specific evaluator constraints

The model should receive the reference IR plus a fixed instruction such as:

> Return only a semantically equivalent LLVM IR replacement for the supplied function. Optimize for the benchmark target. Do not add globals, external calls, inline assembly, or target-specific intrinsics.

Generated instances used in an experiment must be frozen before model calls begin. All model/effort configurations in the same experiment receive the same instances.
