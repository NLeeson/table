# Living Scratchpad (SSoT)

**Current Milestone Context**: Complete.
**Timestamp**: 2026-09-17

---

## 1. Shortest Causal Chain & Working Hypotheses
- **Observed Behavior**: The benchmark invokes `<codex command> exec --ephemeral ...`; `codex-bare` rejects `--ephemeral`.
- **Root Responsibility**: `benchmark/run_codex.py` unconditionally assumes the selected command implements the regular `codex exec` flag set.
- **Working Hypothesis**: Confirmed: the standalone binary is a separate minimal CLI; the full CLI Bare mode is benchmark-compatible.

---

## 2. Targeted Evidence & Symbols
- `benchmark/run_codex.py:293`: Unconditionally adds `--ephemeral` after `exec`.
- `benchmark/run_codex.py:260`: Records `codex_isolation.ephemeral` as true.
- `/home/user/workspace/codex/codex-rs/exec/src/cli.rs:36`: Regular `codex exec` declares the global `--ephemeral` flag.
- `/home/user/workspace/codex/codex-rs/bare/src/lib.rs:134`: Standalone `codex-bare` accepts only model/reasoning/prompt arguments.
- Local `codex --bare --orch exec --help`: exposes every automation option used by the runner, including `--ephemeral`, JSONL, schema, and last-message output.

---

## 3. Pending Actions & Edge Cases
- [x] Inspected both CLI surfaces.
- [x] Verified the full Bare orchestration prefix with the benchmark's dry-run path.
- [x] Preserve `--ephemeral` when using the full `codex exec` path.
