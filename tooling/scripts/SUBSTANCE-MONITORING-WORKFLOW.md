# Substance-monitoring workflow

> When to run [`check_substance.py`](check_substance.py), what the exit codes mean, what counts as "operator action."
>
> Surface area: any long-running agent-pilot bench chain (multi-hour, multi-cell, multi-model). The workflow catches `scroll-loop` and `runaway-generation` pathologies hours before the harness's own stuck-detector fires, saving GPU-hours per pathological run.

## When to run it

For any chain that runs > 1 hour, sample every active transcript every **5 minutes**. The check is read-only and ~10ms per transcript, so cost is negligible.

```bash
# minimal — single transcript
python3 tooling/scripts/check_substance.py /path/to/transcript.jsonl

# typical — every 5 min on every active harness in /tmp/chain_*.log
while sleep 300; do
  for log in /tmp/chain_*.log; do
    transcript=$(grep -oE '/agent-pilot/logs/[^ ]+/transcript.jsonl' "$log" | tail -1)
    [ -f "$transcript" ] && python3 tooling/scripts/check_substance.py "$transcript"
  done
done
```

Or scheduled via a cron job inside the chain orchestrator's "watchdog" loop.

## Exit codes

| Code | Meaning | Action |
|---|---|---|
| `0` | OK — no pathology signal | None |
| `1` | **Scroll-loop or rewrite-loop detected** — tail-streak ≥ 30 identical digit-stripped templates | **SIGTERM the harness PID by exact PID.** See "Operator action" below. |
| `2` | **Runaway-generation suspected** — last entry is `model`, transcript stale > 10 min | Wait. Verify vLLM is healthy via `curl /v1/models`. The harness's 3,600 s HTTP timeout will eventually fire if vLLM has stalled. SIGTERM only saves time vs natural completion of a long generation. |
| `3` | Transcript not found or unparseable | Investigate. Likely the harness hasn't started writing yet, or the run failed before iter 1. |

## Operator action — SIGTERM by exact PID

**Never `pkill -f`** — multiple harnesses may share a substring (e.g., `harness.py`). Always:

```bash
# Find the exact PID
ps -ef | grep "harness.py p3_market_27b-nothink_v8" | grep -v grep
# Output: michael 2702051 ... python3 agent-pilot/harness.py p3_market_27b-nothink_v8 ...

# SIGTERM by exact PID
kill -TERM 2702051
```

After SIGTERM:
- Transcript and receipt are preserved.
- `summary.json` and `workspace_final.tar.gz` are NOT written (harness teardown was bypassed). The shard orchestrator advances to the next cell automatically; the docker sandbox container may need manual cleanup if it survives the harness exit.
- **Drop a `label.json` next to the transcript** so the run is gradeable as a labeled-failure rather than missing data:

```bash
cat > agent-pilot/logs/p3_market_27b-nothink_v8/label.json <<EOF
{
  "primary": "identical-call-loop",
  "sub_labels": ["scroll-loop"],
  "notes": "Operator-SIGTERM at iter <N> per the documented >30 same-content writes methodology rule. <One-line root cause description>.",
  "labeler": "human-via-operator-monitoring",
  "labeled_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

Use the `scroll-loop` or `model-exceeded-max-tokens` sub-labels per [`../FAILURE-TAXONOMY.md`](../FAILURE-TAXONOMY.md) where applicable.

## Why this saves GPU-hours

The harness's `--stuck-threshold 500` workspace-hash check fires *only* after 500 iterations of unchanged workspace state. For `scroll-loop` pathologies (where each iter changes stdout content even if no real progress is being made), the workspace-hash check is unreliable — the run typically reaches the 500-iter threshold long after the loop is detectable.

Concrete numbers from the `microbench-phase-b-2026-05-02` chain:

- `p3_market_27b-nothink_v1` was operator-SIGTERM'd at iter 228 with no-progress = 205 / 500. The harness would have run another ~272 iters (~135 minutes at ~30 s/iter) before its own threshold fired.
- `p3_market_27b-nothink_v8` was operator-SIGTERM'd at iter 116 with no-progress = ~67 / 500. ~430 iters / ~215 minutes saved.
- 4 wall_killed runs in `p3_business` and `p3_doc` were *not* caught by this workflow (the scroll-loop subclass wasn't yet documented when those ran). Now that it is, future runs of those task families would be SIGTERM'd at ~iter 30 of the streak rather than running to 500.

**Aggregate savings on this chain**: roughly 10-14 GPU-hours that would otherwise have been wasted on stuck runs. At a 500 W power cap and $0.13 / kWh, that's roughly $0.65-0.91 in electricity per chain pass plus the schedule benefit (cells unblock sooner for the next run).

## What this workflow does NOT catch

- **`word-trim-loop` (alternating-template loops)**: tail-streak = 1 because the model alternates between write and read commands. Caught by the harness's 500-iter threshold, not this script. A future refinement could add a "low template diversity over 30-iter window" detector (e.g., ≤ 3 unique digit-stripped templates over 30 iters → flag) to catch this subclass.
- **Quality regressions** (e.g., the `p2_ci` test-rewrite-instead-of-prod-fix anti-pattern): substance-check sees the *transcript*, not the *deliverable*. Catching deliverable quality requires hand-grading or per-task grader extensions.
- **Floor-failures** (model emits no tool calls and exits): these have transcripts with < 30 tool calls, below the script's window. The harness's `model_stopped` finish_reason catches these.

## See also

- [`check_substance.py`](check_substance.py) — the script
- [`../FAILURE-TAXONOMY.md`](../FAILURE-TAXONOMY.md) — the labels (`identical-call-loop`, `scroll-loop`, `runaway-generation`, `model-exceeded-max-tokens`)
- [`../../benchmarks/microbench-phase-b-2026-05-02/findings.md`](../../benchmarks/microbench-phase-b-2026-05-02/findings.md) § "All identical-call-loops are not the same" — the wall-killed audit that surfaced the three subclasses
- [`../../benchmarks/microbench-phase-b-2026-05-02/market-research/Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/README.md`](../../benchmarks/microbench-phase-b-2026-05-02/market-research/Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/README.md) — canonical scroll-loop example
