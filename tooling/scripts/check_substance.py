#!/usr/bin/env python3
"""Substance check for an in-flight or completed agent run.

Catches scroll-loops and runaway-generation that the harness's own
stuck-detector misses. See `tooling/FAILURE-TAXONOMY.md` § `scroll-loop`
and § `runaway-generation` for the failure-mode definitions.

Usage:
    check_substance.py <transcript.jsonl>
    check_substance.py <transcript.jsonl> --window 30 --stuck-streak 30 --stale-min 10

Exit codes:
    0 — substance check passed (no actionable signal)
    1 — scroll-loop detected: tail-streak of identical digit-stripped
        templates >= --stuck-streak. Operator should SIGTERM the harness PID.
    2 — runaway-generation suspected: transcript stale > --stale-min
        minutes with the most recent entry being a model response (no
        follow-up tool call). Wait or check vLLM health.

Detection logic:
    1. Read last N tool-call entries (default N=30).
    2. Digit-strip each command (replace runs of digits with `#`). This
       collapses scroll-loops where only a slice offset varies between
       iters into a single template hash.
    3. Compute (a) unique-template count over the window, (b) tail-streak
       of the most recent template.
    4. Check transcript mtime vs now. If the most recent entry is a
       `model` entry and the transcript hasn't grown in --stale-min
       minutes, suspect runaway-generation.

This implements the documented "substance > liveness" methodology rule
(>30 same-content writes → SIGTERM by exact PID). See
`benchmarks/microbench-phase-b-2026-05-02/findings.md` § "Two new
pathologies surfaced" for the canonical examples this script catches.
"""
import argparse
import json
import os
import re
import sys
import time


def digit_strip(s: str) -> str:
    return re.sub(r"\d+", "#", s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript", help="Path to transcript.jsonl")
    ap.add_argument("--window", type=int, default=30,
                    help="How many recent tool calls to inspect (default 30)")
    ap.add_argument("--stuck-streak", type=int, default=30,
                    help="Tail-streak of identical digit-stripped templates that triggers SIGTERM (default 30, matches the documented methodology rule)")
    ap.add_argument("--stale-min", type=int, default=10,
                    help="Minutes of transcript staleness to suspect runaway-generation (default 10)")
    args = ap.parse_args()

    if not os.path.exists(args.transcript):
        print(f"!! transcript not found: {args.transcript}", file=sys.stderr)
        return 3

    entries = []
    with open(args.transcript) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not entries:
        print("!! transcript is empty")
        return 3

    tool_calls = [e for e in entries if e.get("type") == "tool"]
    last_entry = entries[-1]
    mtime = os.path.getmtime(args.transcript)
    stale_s = time.time() - mtime
    stale_min = stale_s / 60.0

    print(f"transcript: {args.transcript}")
    print(f"  total entries: {len(entries)}; tool calls: {len(tool_calls)}")
    print(f"  last entry type: {last_entry.get('type')}, iter: {last_entry.get('iter')}")
    print(f"  staleness: {stale_min:.1f} min")

    if len(tool_calls) < 2:
        print(f"  too few tool calls ({len(tool_calls)}) for substance check")
        return 0

    window = tool_calls[-args.window:]
    templates = [digit_strip((e.get("args") or {}).get("command", "") or "")[:300]
                 for e in window]
    unique = len(set(templates))

    streak = 1
    for i in range(len(templates) - 2, -1, -1):
        if templates[i] == templates[-1]:
            streak += 1
        else:
            break

    print(f"  last-{len(window)} window: {unique} unique digit-stripped templates")
    print(f"  trailing identical-template streak: {streak}")

    if streak >= args.stuck_streak:
        print(f"\n>> SCROLL-LOOP DETECTED — streak {streak} >= threshold {args.stuck_streak}")
        print(f">> operator action: SIGTERM the harness PID (find via `ps -ef | grep harness.py`)")
        return 1

    if last_entry.get("type") == "model" and stale_min > args.stale_min:
        print(f"\n>> RUNAWAY-GENERATION SUSPECTED — last entry is `model`, transcript stale {stale_min:.1f} min")
        print(f">> if vLLM is healthy and harness is alive, model is generating a long response — wait or check vLLM logs")
        return 2

    print("\nOK — no scroll-loop or runaway signal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
