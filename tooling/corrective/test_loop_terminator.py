#!/usr/bin/env python3
"""Unit tests for the loop terminator (synthetic transcripts + kill path)."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loop_terminator as lt  # noqa: E402


def tool_line(name, args, i=1):
    return json.dumps({"t": "2026-08-16T00:00:00Z", "iter": i, "type": "tool",
                       "name": name, "args": args, "wall_s": 0.1, "result_len": 10})


def model_line(i=1):
    return json.dumps({"t": "2026-08-16T00:00:00Z", "iter": i, "type": "model",
                       "wall_s": 1.0, "completion_tokens": 5, "prompt_tokens": 100,
                       "tool_calls": [{"name": "bash", "args_len": 40}],
                       "finish_reason": "tool_calls"})


def write_transcript(path, lines):
    Path(path).write_text("\n".join(lines) + "\n")


class TestMetric(unittest.TestCase):
    def compute(self, lines, threshold=30):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "transcript.jsonl"
            write_transcript(p, lines)
            return lt.compute_transcript_metrics(p, threshold)

    def test_true_identical_loop_flags(self):
        lines = []
        for i in range(35):
            lines.append(model_line(i + 1))
            lines.append(tool_line("bash", {"cmd": "ls /workspace"}, i + 1))
        m = self.compute(lines)
        self.assertEqual(m["longest_run"], 35)
        self.assertTrue(m["flagged"])
        self.assertEqual(m["longest_run_tool"], "bash")

    def test_digit_changing_copyfileobj_does_not_flag(self):
        # The known Qwen copy-loop pathology whose arguments differ by one
        # digit each call: args are NOT identical, so no exact run forms.
        lines = []
        for i in range(60):
            cmd = ("python3 -c \"import shutil; "
                   f"shutil.copyfileobj(open('part{i:04d}.bin','rb'), out)\"")
            lines.append(model_line(i + 1))
            lines.append(tool_line("bash", {"cmd": cmd}, i + 1))
        m = self.compute(lines)
        self.assertEqual(m["longest_run"], 1)
        self.assertFalse(m["flagged"])

    def test_identical_args_different_tool_does_not_flag(self):
        # Same canonical args alternating between two tools: signature
        # includes tool_name, so runs never exceed 1.
        lines = []
        for i in range(60):
            name = "read_file" if i % 2 == 0 else "write_file"
            lines.append(tool_line(name, {"path": "/workspace/notes.md"}, i + 1))
        m = self.compute(lines)
        self.assertEqual(m["longest_run"], 1)
        self.assertFalse(m["flagged"])

    def test_same_tool_identical_args_run_of_30_flags_29_does_not(self):
        base = [tool_line("bash", {"cmd": "cat x"}, i) for i in range(29)]
        m29 = self.compute(base)
        self.assertEqual(m29["longest_run"], 29)
        self.assertFalse(m29["flagged"])
        m30 = self.compute(base + [tool_line("bash", {"cmd": "cat x"}, 30)])
        self.assertEqual(m30["longest_run"], 30)
        self.assertTrue(m30["flagged"])

    def test_key_order_is_canonicalized(self):
        a = json.dumps({"t": "x", "type": "tool", "name": "bash",
                        "args": {"cmd": "ls", "timeout": 5}})
        b = json.dumps({"t": "x", "type": "tool", "name": "bash",
                        "args": {"timeout": 5, "cmd": "ls"}})
        m = self.compute([a, b])
        self.assertEqual(m["longest_run"], 2)

    def test_model_error_lines_neither_break_nor_extend_runs(self):
        lines = []
        for i in range(31):
            lines.append(tool_line("bash", {"cmd": "pwd"}, i))
            lines.append(model_line(i))
            lines.append(json.dumps({"type": "error", "error": "transient"}))
        m = self.compute(lines)
        self.assertEqual(m["longest_run"], 31)
        self.assertTrue(m["flagged"])

    def test_interrupted_run_resets(self):
        lines = [tool_line("bash", {"cmd": "a"}, i) for i in range(20)]
        lines.append(tool_line("bash", {"cmd": "b"}, 21))
        lines += [tool_line("bash", {"cmd": "a"}, i) for i in range(25)]
        m = self.compute(lines)
        self.assertEqual(m["longest_run"], 25)
        self.assertFalse(m["flagged"])

    def test_malformed_lines_are_skipped(self):
        lines = [tool_line("bash", {"cmd": "a"}, 1), "{not json", ""]
        m = self.compute(lines)
        self.assertEqual(m["total_tool_calls"], 1)


class TestWatchKill(unittest.TestCase):
    def test_watch_kills_explicit_pid_and_writes_label(self):
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "transcript.jsonl"
            label = Path(d) / "label.json"
            # Stand-in for the harness process (explicit pid path).
            victim = subprocess.Popen(["sleep", "300"])
            try:
                result_box = {}

                def run_watch():
                    result_box.update(lt.watch(
                        transcript, "synthetic_cell_v1", threshold=30,
                        grace_secs=5, poll_secs=0.05, pid=victim.pid,
                        label_path=label))

                t = threading.Thread(target=run_watch)
                t.start()
                # Feed 29 identical calls -> must stay alive.
                with open(transcript, "a") as f:
                    for i in range(29):
                        f.write(tool_line("bash", {"cmd": "spin"}, i) + "\n")
                time.sleep(0.5)
                self.assertIsNone(victim.poll(), "killed before threshold")
                # The 30th identical call crosses the preregistered threshold.
                with open(transcript, "a") as f:
                    f.write(tool_line("bash", {"cmd": "spin"}, 30) + "\n")
                t.join(timeout=20)
                self.assertFalse(t.is_alive())
                victim.wait(timeout=10)
                self.assertIsNotNone(victim.poll(), "harness stand-in not killed")
                self.assertTrue(result_box["fired"])
                self.assertEqual(result_box["longest_run"], 30)
                lab = json.loads(label.read_text())
                self.assertEqual(lab["primary"], "loop-run30")
                self.assertEqual(lab["metric"], "consecutive_exact_run")
                self.assertEqual(lab["value"], 30)
                self.assertIs(lab["automated"], True)
            finally:
                if victim.poll() is None:
                    victim.kill()

    def test_watch_ends_cleanly_without_flag_when_process_exits(self):
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "transcript.jsonl"
            victim = subprocess.Popen(["sleep", "0.3"])
            with open(transcript, "a") as f:
                for i in range(5):
                    f.write(tool_line("bash", {"cmd": f"step {i}"}, i) + "\n")
            out = lt.watch(transcript, "synthetic_cell_v1", threshold=30,
                           poll_secs=0.05, pid=victim.pid)
            victim.wait()
            self.assertFalse(out["fired"])
            self.assertEqual(out["total_tool_calls"], 5)
            self.assertFalse((Path(d) / "label.json").exists())

    def test_partial_trailing_line_is_not_processed_until_complete(self):
        with tempfile.TemporaryDirectory() as d:
            transcript = Path(d) / "transcript.jsonl"
            victim = subprocess.Popen(["sleep", "300"])
            try:
                full = tool_line("bash", {"cmd": "spin"})
                # 30 identical calls but the last has no newline yet.
                with open(transcript, "w") as f:
                    f.write(("\n".join([full] * 29)) + "\n" + full)
                stop = threading.Event()
                box = {}

                def run_watch():
                    box.update(lt.watch(transcript, "synthetic_cell_v1",
                                        threshold=30, poll_secs=0.05,
                                        pid=victim.pid, stop_event=stop))

                t = threading.Thread(target=run_watch)
                t.start()
                time.sleep(0.5)
                self.assertIsNone(victim.poll(), "fired on a partial line")
                with open(transcript, "a") as f:
                    f.write("\n")
                t.join(timeout=20)
                self.assertTrue(box["fired"])
            finally:
                if victim.poll() is None:
                    victim.kill()

    def test_label_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            label = Path(d) / "label.json"
            label.write_text(json.dumps({"primary": "identical-call-loop"}))
            ok = lt.write_label(label, 30, ("bash", "{}"), 30)
            self.assertFalse(ok)
            self.assertEqual(json.loads(label.read_text())["primary"],
                             "identical-call-loop")

    def test_find_harness_pid_matches_only_real_harness_argv(self):
        # A process whose argv merely CONTAINS the run name must not match.
        self.assertIsNone(lt.find_harness_pid("no_such_run_name_zzz"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
