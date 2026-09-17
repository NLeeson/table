# Living Plan (SSoT)

**Objective**: Explain `--ephemeral` in the benchmark runner and determine whether `codex-bare` needs or supports it.
**Status**: Completed

---

## Active Milestone
- [x] **Complete handoff**: Verified the compatible command prefix and clarified the two Bare entry points.

---

## Milestone Backlog
- None.

---

## Completed Milestones
- [x] **Milestone 0**: Located the runner's unconditional `--ephemeral` argument and isolation metadata.
- [x] **Establish the CLI contract**: Confirmed standalone `codex-bare` has a minimal, incompatible CLI while `codex --bare --orch exec` exposes the full runner-required interface.
- [x] **Assess benchmark isolation**: Confirmed `--ephemeral` suppresses local session-file persistence and remains valid in the full `codex exec` path.
- [x] **Validate invocation**: The exact `--codex '/home/user/workspace/codex/codex-rs/target/release/codex --bare --orch'` dry run planned all 12 calls successfully.

---

## Decision Log & Deviations
- **2026-09-17**: Treat the built local binary and source as authoritative because the failure concerns a custom local `codex-bare` executable.
- **2026-09-17**: Recommend the full `codex --bare --orch` command prefix for the benchmark; it retains the standard `exec` automation contract.
