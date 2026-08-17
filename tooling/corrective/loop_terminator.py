#!/usr/bin/env python3
"""Automated identical-call loop terminator (PREREGISTRATION.md section 4, terminator b).

Primary repeat metric, implemented exactly as documented in the protocol:
the longest EXACT consecutive run over ``(tool_name, canonical_json(arguments))``
across the transcript's tool-call stream. At ``value >= threshold`` (30,
preregistered) the watcher mechanically SIGTERMs the harness process for the
cell and writes ``label.json``::

    {"primary": "loop-run30", "metric": "consecutive_exact_run",
     "value": N, "automated": true, ...}

No operator judgment is involved anywhere in this file.

Two entry points:

  recompute  offline recompute of the metric from a finished transcript.
             The exact same functions the live watcher uses (single
             implementation; documentation and implementation identical).
  watch      live-tail a cell's transcript.jsonl; kill + label at threshold.

Design notes (verified against tooling/harness.py at this checkout):
  * ``transcript.jsonl`` "tool" events carry the PARSED arguments dict in
    ``args`` (harness.py agent_loop). Canonicalisation is
    ``json.dumps(args, sort_keys=True, separators=(",", ":"))`` so key order
    never matters and any digit change in any value breaks the run.
  * Arguments larger than 50 KB are stored by the harness as
    ``{"_truncated_at_bytes": N}``; two such calls compare equal only if their
    byte counts are equal. Recorded limitation, exploratory impact only.
  * Consecutive means consecutive in the tool-call stream. "model"/"error"/
    "abort" transcript lines are not tool calls and neither extend nor break
    a run.

stdlib only.
"""

import argparse
import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path

DEFAULT_THRESHOLD = 30
LABEL_PRIMARY = "loop-run30"
LABEL_METRIC = "consecutive_exact_run"


def canonical_json(obj):
    """Canonical JSON text for tool-call arguments (sorted keys, no spaces)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def signature(tool_name, args):
    """The preregistered identity of one tool call."""
    return (tool_name, canonical_json(args))


def args_sha256(canonical_args_text):
    return hashlib.sha256(canonical_args_text.encode("utf-8")).hexdigest()


def iter_tool_signatures(lines):
    """Yield signatures for every complete ``type == "tool"`` transcript line.

    Malformed lines are skipped (they cannot be a tool call); partial lines
    must be filtered by the caller (the watcher only feeds complete lines).
    """
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") != "tool":
            continue
        yield signature(ev.get("name"), ev.get("args"))


class RunTracker:
    """Incremental longest-exact-consecutive-run tracker."""

    def __init__(self):
        self.current_sig = None
        self.current_run = 0
        self.max_run = 0
        self.max_sig = None
        self.total_tool_calls = 0

    def feed(self, sig):
        self.total_tool_calls += 1
        if sig == self.current_sig:
            self.current_run += 1
        else:
            self.current_sig = sig
            self.current_run = 1
        if self.current_run > self.max_run:
            self.max_run = self.current_run
            self.max_sig = sig
        return self.current_run

    def metrics(self, threshold=DEFAULT_THRESHOLD):
        name, cargs = (self.max_sig if self.max_sig else (None, None))
        return {
            "metric": LABEL_METRIC,
            "total_tool_calls": self.total_tool_calls,
            "longest_run": self.max_run,
            "longest_run_tool": name,
            "longest_run_args_sha256": args_sha256(cargs) if cargs is not None else None,
            "threshold": threshold,
            "flagged": self.max_run >= threshold,
        }


def longest_exact_run(sigs):
    """(max_run, max_sig) over an iterable of signatures. Offline helper."""
    t = RunTracker()
    for s in sigs:
        t.feed(s)
    return t.max_run, t.max_sig


def compute_transcript_metrics(transcript_path, threshold=DEFAULT_THRESHOLD):
    """Offline recompute over a finished transcript. Same code path as watch."""
    t = RunTracker()
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for sig in iter_tool_signatures(f):
            t.feed(sig)
    out = t.metrics(threshold)
    out["transcript"] = str(transcript_path)
    return out


# ----- process control ---------------------------------------------------

def find_harness_pid(run_name, exclude_pids=()):
    """Find the live ``python3 .../harness.py <run_name>`` process.

    Matches only a cmdline where some argv entry is harness.py (basename
    match) AND the immediately following argv entry equals the run name.
    That cannot match supervisors, greps, or this process.
    """
    me = os.getpid()
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == me or pid in exclude_pids:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                argv = f.read().decode("utf-8", "replace").split("\0")
        except OSError:
            continue
        for i, a in enumerate(argv[:-1]):
            if os.path.basename(a) == "harness.py" and argv[i + 1] == run_name:
                return pid
    return None


def pid_alive(pid):
    """True only for a live, non-zombie process.

    A dead child that its parent has not yet reaped (zombie) still passes
    ``os.kill(pid, 0)``; check /proc state so a watcher never spins on one.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    try:
        with open(f"/proc/{pid}/stat") as f:
            stat = f.read()
        state = stat.rpartition(")")[2].split()[0]
        return state != "Z"
    except (OSError, IndexError):
        return False


def terminate_pid(pid, grace_secs=30):
    """SIGTERM, wait up to grace_secs, then SIGKILL. Returns how it died."""
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return "already-gone"
    deadline = time.time() + grace_secs
    while time.time() < deadline:
        if not pid_alive(pid):
            return "sigterm"
        time.sleep(0.5)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return "sigterm"
    return "sigkill"


def now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_label(label_path, value, sig, threshold, extra=None):
    """Write the machine label. Never overwrites an existing label.json."""
    label_path = Path(label_path)
    if label_path.exists():
        return False
    name, cargs = sig if sig else (None, None)
    label = {
        "primary": LABEL_PRIMARY,
        "metric": LABEL_METRIC,
        "value": value,
        "automated": True,
        "threshold": threshold,
        "tool_name": name,
        "canonical_args_sha256": args_sha256(cargs) if cargs is not None else None,
        "written_at": now_iso(),
        "written_by": "tooling/corrective/loop_terminator.py",
    }
    if extra:
        label.update(extra)
    tmp = label_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(label, indent=2) + "\n")
    tmp.rename(label_path)
    return True


# ----- live watcher ------------------------------------------------------

def watch(transcript_path, run_name, threshold=DEFAULT_THRESHOLD, grace_secs=30,
          poll_secs=2.0, pid=None, label_path=None, stop_event=None,
          startup_wait_secs=900):
    """Tail transcript.jsonl for one cell; kill + label at run >= threshold.

    Returns a result dict. ``flagged`` True means the terminator fired.
    Ends cleanly (flagged False) once the harness process is gone and no
    unread complete lines remain.

    ``pid`` may be passed explicitly (tests); otherwise the harness process
    is located by cmdline. ``stop_event`` (threading.Event) allows a
    supervisor to end the watch.
    """
    transcript_path = Path(transcript_path)
    if label_path is None:
        label_path = transcript_path.parent / "label.json"
    tracker = RunTracker()
    buf = ""
    offset = 0
    started = time.time()
    fired = False
    kill_result = None
    target_pid = pid

    def read_new():
        nonlocal offset, buf
        new_lines = []
        try:
            with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(offset)
                chunk = f.read()
                offset = f.tell()
        except OSError:
            return new_lines
        if not chunk:
            return new_lines
        buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            new_lines.append(line)
        return new_lines

    while True:
        for line in read_new():
            for sig in iter_tool_signatures([line]):
                run = tracker.feed(sig)
                if run >= threshold and not fired:
                    fired = True
                    if target_pid is None:
                        target_pid = find_harness_pid(run_name)
                    if target_pid is not None:
                        kill_result = terminate_pid(target_pid, grace_secs)
                    else:
                        kill_result = "harness-pid-not-found"
                    write_label(label_path, run, sig, threshold, extra={
                        "run_name": run_name,
                        "harness_pid": target_pid,
                        "kill": kill_result,
                    })
            if fired:
                break
        if fired:
            break
        if stop_event is not None and stop_event.is_set():
            break
        if target_pid is None:
            target_pid = find_harness_pid(run_name)
        if target_pid is not None:
            if not pid_alive(target_pid):
                # Harness exited on its own; drain any final lines once.
                for line in read_new():
                    for sig in iter_tool_signatures([line]):
                        tracker.feed(sig)
                break
        elif time.time() - started > startup_wait_secs and not transcript_path.exists():
            break  # harness never produced a transcript; supervisor classifies
        time.sleep(poll_secs)

    result = tracker.metrics(threshold)
    result.update({
        "run_name": run_name,
        "transcript": str(transcript_path),
        "fired": fired,
        "harness_pid": target_pid,
        "kill": kill_result,
        "label_path": str(label_path) if fired else None,
    })
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    rc = sub.add_parser("recompute", help="offline metric recompute from a transcript")
    rc.add_argument("transcript")
    rc.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)

    wa = sub.add_parser("watch", help="live-tail a cell; kill harness + write label at threshold")
    wa.add_argument("--run-name", required=True)
    wa.add_argument("--transcript", required=True)
    wa.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    wa.add_argument("--grace-secs", type=int, default=30)
    wa.add_argument("--poll-secs", type=float, default=2.0)
    wa.add_argument("--pid", type=int, default=None,
                    help="explicit harness pid (tests); default: locate by cmdline")
    wa.add_argument("--label", default=None, help="label.json path (default: next to transcript)")

    args = ap.parse_args()
    if args.cmd == "recompute":
        out = compute_transcript_metrics(args.transcript, args.threshold)
        print(json.dumps(out, indent=2))
        return 0
    out = watch(args.transcript, args.run_name, threshold=args.threshold,
                grace_secs=args.grace_secs, poll_secs=args.poll_secs,
                pid=args.pid, label_path=args.label)
    print(json.dumps(out, indent=2))
    return 3 if out["fired"] else 0


if __name__ == "__main__":
    sys.exit(main())
