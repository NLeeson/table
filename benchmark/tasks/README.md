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

## Frozen v0 inventory

The v0 suite contains 24 tasks, four per family:

- reductions: `reductions_sum8_i32`, `reductions_xor8_i32`, `reductions_smin8_i32`, `reductions_umax8_i32`
- scans: `scans_prefix8_i32`, `scans_prefix8_xor_i32`, `scans_prefix8_smax_i32`, `scans_prefix4_i64`
- sorting/selection: `sorting_selection_median3_i32`, `sorting_selection_minmax4_i32`, `sorting_selection_second4_i32`, `sorting_selection_sort4_i32`
- bit operations: `bitops_popcount32`, `bitops_bitreverse32`, `bitops_bswap64`, `bitops_parity64`
- vector arithmetic: `vector_arithmetic_clamp8_i32`, `vector_arithmetic_abs8_i32`, `vector_arithmetic_affine8_i16`, `vector_arithmetic_smin8_i32`
- permutations/data movement: `permutations_reverse8_i32`, `permutations_rotate8_i32`, `permutations_swap_pairs8_i32`, `permutations_interleave4_i32`

The original six smoke tasks are unchanged; the 18 additional frozen instances complete the manifest's declared four instances per family.
