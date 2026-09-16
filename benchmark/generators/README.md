# Generators

Task generators make benchmark contamination harder and let each experiment use fresh, reproducible IR instances.

## v0 families

- reductions
- scans / prefix operations
- sorting / selection
- bit manipulation
- vector arithmetic
- permutations / data movement

## Generator requirements

A generator must be deterministic for `(generator_version, seed, parameters)` and should emit both `reference.ll` and `task.json`.

Prefer variations that materially alter the concrete SSA/dataflow graph while preserving a recognizable optimization problem: lane counts, integer widths, signedness, constants, permutations, initial DAG shape, and legal operation ordering.

Generators must not use wall-clock randomness. Seeds are chosen before model evaluation and recorded in the run manifest.

The generated reference should remain within the v0 evaluator envelope: one bounded pure function, no globals, no external calls, no inline assembly, and no target-specific intrinsics.
