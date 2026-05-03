# market-research — Qwen3-Coder-Next-AWQ

**Run name:** `p3_market_coder_v1` (1 of 3 — all 3 STRUCTURAL_FAIL across the series; this is the structural-fail entry, not a cherry-pick)
**Wall:** ~25 minutes (stuck-detector eventually fired)
**Cost upper:** ~$0.034
**Verdict:** **STRUCTURAL_FAIL** — no `recommendation.md`, no `comparison.md`, no `sources.md`

## Why this entry is here

The kept-as-failure-mode-evidence convention used elsewhere in this repo (e.g. [`dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ`](../../../dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/), [`dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ`](../../../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/)) applies. This entry doesn't ship a usable deliverable, but **the failure shape is the comparison data** — Coder-Next can't drive the kind of multi-step internet-research workflow that 27B drives [(see the 27B entry)](../Qwen3.6-27B-AWQ/).

This run is `v1`, which entered stuck-in-research. The other two runs failed similarly:
- v2: stuck-in-research (same shape)
- v3: vLLM api_error at 65 iters (probable context overflow)

## What's in this folder

- [`deliverable/README.md`](deliverable/README.md) — the only file the agent wrote into its deliverable folder; no structured outputs (no `recommendation.md`, `comparison.md`, `sources.md`, no `research/` notes, no `decisions/` ADRs) were produced
- [`grade.json`](grade.json) — verdict + missing-files list
- [`label.json`](label.json) — `stuck-in-research`
- [`receipt.json`](receipt.json), [`summary.json`](summary.json), [`cost.json`](cost.json), [`transcript.jsonl`](transcript.jsonl)

The transcript is the most useful artifact for understanding the failure. The agent reads the same kinds of pages 27B does (vendor pricing, comparison articles), takes notes inside the transcript, but never moves to the "produce the structured `recommendation.md` + `comparison.md` + `sources.md`" stage — and the working-notes/ADR scaffolding never lands on disk either. The workspace_state_hash detects no progress eventually and the stuck-detector fires.

## How to read this

The point isn't "Coder-Next is bad at password-manager research" — it's that **Coder-Next doesn't drive multi-stage write-out workflows on this shape of task**. On tasks where the deliverable shape is tight enough that the agent can produce it in one or two write_file calls (extraction, triage, business memo), Coder-Next ships fine. On tasks where the deliverable is several distinct files that each need their own pass (recommendation, comparison, sources), the agent reads, takes notes, but can't get out of the research phase.

This is task-shape data, not raw-capability data. For deployment design: if you're using Coder-Next on internet-research tasks, structure the workflow so each output is its own task with a tight scope, rather than asking for a multi-file deliverable bundle.
