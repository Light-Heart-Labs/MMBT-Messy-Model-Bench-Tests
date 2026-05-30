---
name: mmbt-bench
description: >-
  Drive a full MMBT microbench run end-to-end with the self-healing autopilot:
  launch a target-N run (optionally via a model preset), monitor it live via the
  dashboard (grid / oneline / html / trend / flips / json), auto-recover the
  endpoint and stuck cells, grade + summarize, then generate the findings doc and
  publish a scorecard on the MMBT repo. Use when the user wants to run or resume
  the microbench, take a model to N replicates, watch the bench grid, analyze
  replicate stability, or publish bench results.
trigger phrases:
  - /mmbt-bench
  - run the mmbt bench
  - run the microbench
  - take <model> to N=<n>
  - resume the bench autopilot
  - watch the bench dashboard
  - grade and summarize the bench
  - publish the bench results
---

# /mmbt-bench — MMBT microbench autopilot workflow

Wraps the self-healing supervisor + dashboard + report generator into one
launch → monitor → recover → grade → summarize → report → publish flow.

## The three tools (all in `tooling/`)

- **`bench_autopilot.py`** — multi-model self-healing supervisor. Drives a run to
  `--target-n N`, (re)launches the llama.cpp endpoint, runs the stuck-cell
  watchdog, grades + summarizes each arm, pushes Pushover milestones via
  `~/dream-fleet-test/lib/notify.sh`, and writes `/tmp/bench-autopilot/status.json`.
  Supports model presets (`--preset`), a complete-run scorecard + git commit
  (`--publish`), and a harness-break anomaly alert.
- **`bench_dashboard.py`** — read-only viewer/analyzer over the SAME status.json +
  per-cell `grade.json`. Color grid plus `--oneline`/`--watch`/`--html` rendering
  and three analysis flags `--json`/`--trend`/`--flips`. Never edits state.
- **`bench_report.py`** — standalone findings-markdown generator. Reads the
  per-cell logs (not status.json) up to `--n` and emits the full MMBT findings doc
  (scorecard + "what N reveals" stability + think-vs-no-think + finish-reason
  audit). Safe to run against a run in progress (partial data renders as-is).

> A LIVE N=20 run uses these exact files. Never edit them destructively — write
> new `*_v3` files if you must change behavior; only this SKILL and the html are
> freely editable.

## Resolve paths first (do NOT hardcode)

```bash
REPO="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
TOOLING="$REPO/tooling"
test -f "$TOOLING/bench_autopilot.py" || { echo "not an MMBT clone under $REPO"; exit 1; }
AUTOPILOT="$TOOLING/bench_autopilot.py"
DASH="$TOOLING/bench_dashboard.py"
REPORT="$TOOLING/bench_report.py"
```

State files are fixed at `/tmp/bench-autopilot/` on every clone: `status.json`,
`autopilot.log`, `heartbeat.json`, `scorecard.md`, `run-<arm>.log`,
`grade-<arm>.log`, `summary-<arm>.txt`. Do not relocate them.

## Ground truth

- **TASKS (12, fixed order):** `p1_bugfix, p1_testwrite, p1_refactor, p2_extract,
  p2_ci, p2_hallucination, p2_triage, p3_doc, p3_business, p3_market, p3_writing,
  p3_pm`.
- **Arms (label-keyed):** `397b-nothink` (thinking off) / `397b-think` (thinking on).
- **N=10 no-think baseline (82/120):** bugfix 10, testwrite 0, refactor 0,
  extract 10, ci 10, halluc 10, triage 10, doc 9, business 10, market 8,
  writing 0, pm 5. The dashboard/scorecard show Δ-vs-baseline only for the nothink arm.
- **Reference comparators (carried in `bench_report.py`):** Step low/med/high totals
  7/8/8; 27B and Coder ≈7/12.

## Steps

1. **Confirm parameters.** Model/preset, the two arms, and target N (ask if
   unstated — N=3 quick, N=10–20 canonical). Presets select model/container/gguf/
   ctx/arms: `397b` (default; byte-for-byte the live config), `qwen3.6-27b`
   (runnable llama.cpp path once its gguf is confirmed on disk), `step3p7` (vLLM
   STUB — `ensure_endpoint` raises NotImplementedError, do not launch it). A
   `--config <cfg.json>` is applied on top of the preset (config wins, additive).

2. **Check for a live run first (idempotent — safe to attach).** If
   `status.json` exists, `phase` is a `run:`/`passN` value, and it is fresh
   (`stat -c %Y` of the file vs `date +%s`, NOT `ls`/mtime eyeballing), an
   autopilot is already driving — do NOT launch a second one (two supervisors
   fight over the endpoint container + sandboxes). The autopilot also self-guards:
   on start it aborts (`AUTOPILOT_ABORTED_DOUBLE_DRIVE`, exit 3) if another
   heartbeat is <120s fresh. Just monitor (step 4).

3. **Launch the autopilot** (only if none is live), backgrounded; it is
   re-entrant — completed cells are skipped, so relaunch after a crash resumes:
   ```bash
   nohup python3 "$AUTOPILOT" --target-n 20 \
       > /tmp/bench-autopilot/launch.log 2>&1 &
   echo "autopilot pid $!"
   ```
   With a preset and publish-on-complete:
   ```bash
   nohup python3 "$AUTOPILOT" --target-n 20 --preset 397b --publish \
       > /tmp/bench-autopilot/launch.log 2>&1 &
   ```
   Pushover milestones (start / endpoint restart / arm complete / run
   done|incomplete / harness-anomaly) are always-on, no-op without
   `~/dream-fleet-test/lib/notify.sh` + `~/.pushoverrc`. Other knobs:
   `--config <cfg.json>`, `--max-passes N` (default 6), `--once` (write one
   status snapshot and exit — for an external monitor, does not drive a run).
   The autopilot prints `AUTOPILOT_COMPLETE` / `AUTOPILOT_INCOMPLETE` at the end.

4. **Monitor — sample substance, don't hold a watch loop.** Take a one-shot read
   each check; reserve `--watch` for a human terminal:
   ```bash
   python3 "$DASH" --oneline          # one compact status line
   python3 "$DASH" --no-color         # full grid, one-shot
   python3 "$DASH" --no-color --no-events --no-sparkline   # bare grid
   python3 "$DASH" --html /tmp/bench-autopilot/dashboard.html
   python3 "$DASH" --watch            # live (15s refresh), for a human terminal
   python3 "$DASH" --json             # compact machine-readable status (from grade.json)
   python3 "$DASH" --trend            # per-task cumulative pass-rate over v1-3/5/10/20 windows
   python3 "$DASH" --flips            # per-task cells differing from the modal verdict (variance)
   tail -n 30 /tmp/bench-autopilot/autopilot.log
   ```
   `--json` is the machine-readable path (derived from grade.json, works even on a
   partial run); `--trend` reveals where a small-N read was misleading; `--flips`
   surfaces high-variance cells. All three are read-only and exit rc=0 on sparse
   data. Render flags: `--oneline --no-events --no-sparkline --html --watch
   --no-color`. status.json also carries `eta_secs`/`recent_cells`/`fails`/
   `started_at`/`elapsed_secs`/`preset`/`model`/`engine` for direct `jq`.

5. **Auto-recovery — the autopilot does this itself.** Endpoint restart (down
   >90s during a run → relaunch with `--reasoning-format none` etc.; loud Pushover
   on a load failure), stuck-cell kill (transcript frozen > `stuck_secs`, default
   1200s → exact-PID SIGTERM/SIGKILL + drop sandbox), idempotent resume across
   passes, and a priority-1 anomaly alert when ≥3 consecutive freshly-graded cells
   are `GRADER_FAILED`/`MISSING_OUTPUT` (a harness/grader break, distinct from
   model-quality fails). Only intervene by hand if it is wedged AND you confirmed
   it by substance, not a stale mtime — use the surgical kill recipe in gotchas.

6. **Grade + summarize** — produced per arm automatically when an arm finishes.
   To (re)run on demand (idempotent), once per arm:
   ```bash
   bash "$TOOLING/scripts/grade_microbench.sh" 397b-nothink
   bash "$TOOLING/scripts/summarize.sh"        397b-nothink   # prints PASS/FAIL table
   ```
   The summary table is the headline artifact for the writeup.

7. **On completion** (`status.json` `phase == "COMPLETE"`, all cells present for
   every arm) → generate the findings doc, then publish.

## Completion → report + publish

1. **Findings doc** — `bench_report.py` builds the full markdown (read-only;
   does not touch status.json/autopilot/dashboard):
   ```bash
   python3 "$REPORT" --n 20 --out /tmp/bench-autopilot/findings.md
   python3 "$REPORT" --n 10            # markdown to stdout for a quick look
   ```
   Flags: `--n` (target N, default 20), `--out FILE`, `--logs DIR`
   (default `~/bench/logs`).

2. **Scorecard + git commit** — the autopilot's `--publish` (on a COMPLETE run
   only) writes `/tmp/bench-autopilot/scorecard.md` (per-task pass/N for both arms
   + totals + Δ vs the N=10 nothink baseline) and `git add`+commits it to a
   `bench-results-<date>` branch in `~/bench` (NOT pushed; idempotent; never
   crashes the run on git failure). If the run already finished without
   `--publish`, re-run the autopilot at the same `--target-n` with `--publish` —
   all cells are done so it goes straight to the scorecard step.

3. **Publish to the MMBT repo** (`origin` =
   `Light-Heart-Labs/MMBT-Messy-Model-Bench-Tests`) for an external audience:
   ```bash
   cd "$REPO"
   git checkout -b mmbt-<model>-n<N>-$(date +%Y%m%d)
   git add logs/   # plus the findings doc + scorecard
   git commit -m "MMBT <model> N=<N>: <one-line headline>"
   git push -u origin HEAD
   gh pr create --fill
   ```
   Follow repo methodology: drift via harness sha256 (not git_sha); keep the
   think-block / market STRUCTURAL_PASS caveats noted.

4. **Reclaim the box** when fully done — free GPU + scratch:
   ```bash
   docker ps -aq --filter name=bench-sandbox- | xargs -r docker rm -f
   docker rm -f llama-397b        # endpoint container (name from config/preset)
   sudo rm -rf "$TOOLING"/workspace/*_v* /tmp/grade_*_v*
   ```
   Leave `/tmp/bench-autopilot/` for the record unless the user wants it gone.

5. **Notify** (optional): `notify_push "MMBT published" "PR opened for <model> N=<N>" 1`.

## Known gotchas

- **`--reasoning-format none` for the think arm.** The llama.cpp endpoint MUST
  launch with `--reasoning-format none` (the autopilot's `ensure_endpoint`
  already does) so the think arm's reasoning is returned in-band and the grader
  sees the real answer. Keep that flag on any manual relaunch or the think arm
  scores garbage.
- **Arm mode must be in the label.** Run names are keyed by label only. Thinking
  off/on MUST be encoded in the label (`...-nothink` / `...-think`) or the second
  arm is silently skipped as "already complete". `run_microbench.sh` fails fast on
  this — heed the error.
- **sudo cleanup of root-owned workspaces.** Sandboxes write
  `tooling/workspace/*<label>_v*` and `/tmp/grade_*<label>_v*` as root; clearing
  them needs `sudo rm -rf` scoped to the exact glob (the autopilot already does
  this). EPERM means root-owned — use sudo, never a bare `rm -rf` of a parent.
- **Kill by EXACT PID, never `pkill -f`.** To clear a hung cell, match the exact
  harness invocation and kill only those PIDs, then drop its sandbox:
  ```bash
  CELL=p3_market_397b-think_v7
  pgrep -f "harness.py $CELL " | xargs -r kill -TERM ; sleep 3
  pgrep -f "harness.py $CELL " | xargs -r kill -KILL
  docker rm -f "bench-sandbox-$CELL"
  ```
  `pkill -f harness` would nuke every concurrent cell. `kill_stuck` follows this
  exact pattern.
- **Market cells are slow + stuck-prone.** `p3_market` has no input mount and does
  live-ish research; it runs long and is the most common stuck cell. The watchdog
  fires on transcript-freeze (`stuck_secs`, default 1200s), not wall time — a
  long-but-progressing market cell is NOT stuck. Cross-check `current.frozen_secs`
  vs the threshold before killing.
- **p1 cells make bench.py CPU spikes.** `p1_bugfix/testwrite/refactor` run
  `bench.py`/test commands in the sandbox that are CPU-bound, so CPU wall time and
  power spike there even though the model is the GPU workload — expected, not a
  hang and not a thermal failure.
