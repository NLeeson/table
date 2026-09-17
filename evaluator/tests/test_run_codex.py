from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmark import run_codex  # noqa: E402
from benchmark.run_codex import invoke_codex  # noqa: E402


class InvokeCodexTests(unittest.TestCase):
    @patch("benchmark.run_codex.subprocess.run")
    def test_timeout_decodes_partial_output_and_identifies_stage(self, run) -> None:
        run.side_effect = subprocess.TimeoutExpired(
            ["codex", "exec"],
            2.0,
            output=b'{"type":"turn.started"}\n',
            stderr=b"partial stderr\xff\n",
        )

        with tempfile.TemporaryDirectory() as tmp:
            stdout, stderr, returncode, error, timeout_stage = invoke_codex(
                ["codex", "exec"],
                prompt="prompt",
                cwd=Path(tmp),
                timeout=2.0,
            )

        self.assertEqual(stdout, '{"type":"turn.started"}\n')
        self.assertEqual(stderr, "partial stderr\ufffd\n")
        self.assertIsNone(returncode)
        self.assertEqual(error, "Codex timed out after 2s")
        self.assertEqual(timeout_stage, "model")


class RunnerTimeoutTests(unittest.TestCase):
    def test_model_timeout_is_persisted_as_a_completed_failed_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            benchmark_dir = root / "benchmark"
            task_dir = benchmark_dir / "tasks" / "task"
            task_dir.mkdir(parents=True)
            manifest_path = benchmark_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "benchmark": "timeout-test",
                        "benchmark_version": "0.2.0",
                        "toolchain": {
                            "llvm_version": "22.1.0",
                            "alive2_revision": "revision",
                            "alive2_args": ["--disable-undef-input"],
                            "target_triple": "x86_64-unknown-linux-gnu",
                            "mcpu": "haswell",
                        },
                    }
                )
            )
            (task_dir / "task.json").write_text(json.dumps({"seed": 1}))
            (task_dir / "reference.ll").write_text("define i32 @kernel() { ret i32 0 }\n")

            def fake_run(cmd, **kwargs):
                if "--version" in cmd:
                    return subprocess.CompletedProcess(cmd, 0, "codex-cli test\n", "")
                if cmd[:2] == ["git", "-C"]:
                    return subprocess.CompletedProcess(cmd, 0, "deadbeef\n", "")
                raise subprocess.TimeoutExpired(
                    cmd,
                    kwargs["timeout"],
                    output=b'{"type":"turn.started"}\n',
                    stderr=b"partial stderr\n",
                )

            with (
                patch.object(run_codex, "ROOT", root),
                patch.object(run_codex, "MANIFEST", manifest_path),
                patch.object(run_codex, "TASKS_DIR", benchmark_dir / "tasks"),
                patch.object(run_codex, "OUTPUT_SCHEMA", benchmark_dir / "output.json"),
                patch.object(run_codex, "VERIFY", root / "verify.py"),
                patch.object(run_codex.subprocess, "run", side_effect=fake_run),
                patch.object(
                    sys,
                    "argv",
                    [
                        "run_codex.py",
                        "--model",
                        "model",
                        "--effort",
                        "high",
                        "--task",
                        "task",
                        "--run-id",
                        "timeout-run",
                        "--timeout",
                        "2",
                    ],
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(run_codex.main(), 1)

            run_dir = root / "runs" / "timeout-run"
            row = json.loads((run_dir / "results.jsonl").read_text())
            run_meta = json.loads((run_dir / "run.json").read_text())
            self.assertEqual(row["verification_status"], "invalid")
            self.assertEqual(row["timeout_stage"], "model")
            self.assertEqual(row["error"], "Codex timed out after 2s")
            self.assertIsNone(row["candidate_ir_path"])
            self.assertEqual(run_meta["model_timeout_seconds"], 2.0)
            self.assertTrue((run_dir / "completed.json").is_file())
            self.assertEqual(
                (run_dir / "events" / "model__high__task.jsonl").read_text(),
                '{"type":"turn.started"}\n',
            )


if __name__ == "__main__":
    unittest.main()
