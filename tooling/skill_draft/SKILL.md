---
name: mmbt-bench
description: >-
  Drive a full MMBT microbench run end-to-end with the self-healing autopilot:
  launch a target-N run, monitor it live via the dashboard, auto-recover the
  endpoint and stuck cells, grade + summarize, then hand off to publish on the
  MMBT repo. Use when the user wants to run or resume the microbench, take a
  model to N replicates, watch the bench grid, or publish bench results.
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

Wraps the self-healing supervisor + dashboard into one launch → monitor →
recover → grade → summarize → publish flow.

Two tool sets exist in `tooling/`:
- ORIGINAL (a live run may be using these — never edit in place):
  `bench_autopilot.py`, `bench_dashboard.py`.
- ENRICHED (backward-compatible supersets; same status.json schema + same CLI,
  only added flags/keys) — prefer these for this skill:
  `bench_autopilot_enriched.py` (adds always-on Pushover milestones via
  `~/dream-fleet-test/lib/notify.sh`, per-cell wall/tok-s metrics, richer
  status.json keys `eta_secs`/`recent_cells`/`fails`/`started_at`/`elapsed_secs`,
  resume double-drive guard, and a `--once` snapshot flag);
  `bench_dashboard_enriched.py` (adds `--oneline`, `--no-events`,
  `--no-sparkline`, plus a baseline-delta + sparkline + events feed in the grid).
The enriched scripts are safe to run side-by-side against the same
`/tmp/bench-autopilot/status.json` as a live original run.

## Resolve paths first (do NOT hardcode)

```bash
REPO="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
TOOLING="$REPO/tooling"
test -f "$TOOLING/bench_autopilot.py" || { echo "not an MMBT clone under $REPO"; exit 1; }
AUTOPILOT="$TOOLING/bench_autopilot_enriched.py"   # falls back to bench_autopilot.py
DASH="$TOOLING/bench_dashboard_enriched.py"        # falls back to bench_dashboard.py
[ -f "$AUTOPILOT" ] || AUTOPILOT="$TOOLING/bench_autopilot.py"
[ -f "$DASH" ] || DASH="$TOOLING/bench_dashboard.py"
```

The status/log files are fixed at `/tmp/bench-autopilot/` on every clone:
`status.json`, `autopilot.log`, `run-<arm>.log`, `grade-<arm>.log`,
`summary-<arm>.txt`. Do not relocate them.

## Steps

1. **Confirm parameters.** Model, the two reasoning arms (`397b-nothink` /
   `397b-think` by default), and target N (ask if unstated — N=3 quick,
   N=10–20 canonical). Optional `--config <cfg.json>` overrides model/port/gguf/
   container/arms/stuck_secs.

2. **Check for a live run first (idempotent — safe to attach).** If
   `/tmp/bench-autopilot/status.json` exists, `phase` is a `run:`/`passN` value,
   and `updated` is fresh (compare `stat -c %Y` of the file vs `date +%s`, not
   `ls`/mtime eyeballing), an autopilot is already running — do NOT launch a
   second one (two supervisors fight over the endpoint container + sandboxes).
   Just monitor (step 4).

3. **Launch the autopilot** (only if none is live), in the background; it is
   idempotent and re-entrant — completed cells are skipped, so relaunch after a
   crash resumes:
   ```bash
   nohup python3 "$AUTOPILOT" --target-n 20 \
       > /tmp/bench-autopilot/launch.log 2>&1 &
   echo "autopilot pid $!"
   ```
   The enriched autopilot's Pushover milestones (start / endpoint restart /
   arm complete / run done|incomplete) are always-on, gated only by the presence
   of `~/dream-fleet-test/lib/notify.sh` + `~/.pushoverrc` (no-op if absent), so
   no flag is needed. Other knobs: `--config <cfg.json>` (model/port/gguf/
   container/arms/stuck_secs), `--max-passes N` (default 6), and `--once` (write
   one status snapshot and exit — for an external monitor, does not drive a run).
   The autopilot itself handles endpoint (re)launch, the stuck-cell watchdog, and
   grade+summarize per arm. It also guards against double-drive: on start it
   aborts if a prior autopilot heartbeat is fresh (<120s).

4. **Monitor — sample substance, don't hold a watch loop.** Take a one-shot read
   each check; reserve `--watch` for a human terminal:
   ```bash
   python3 "$DASH" --oneline          # one compact status line (enriched)
   python3 "$DASH" --no-color         # full grid, one-shot
   python3 "$DASH" --no-color --no-events --no-sparkline   # bare grid
   python3 "$DASH" --html /tmp/bench-autopilot/dashboard.html
   python3 "$DASH" --watch            # live, for a human terminal
   tail -n 30 /tmp/bench-autopilot/autopilot.log   # recent supervisor activity
   ```
   Dashboard flags: `--oneline --no-events --no-sparkline --html --watch
   --no-color`. There is no `--json` — for machine-readable status read
   `/tmp/bench-autopilot/status.json` directly (it carries the enriched keys
   `eta_secs`/`recent_cells`/`fails`/`elapsed_secs`), e.g.
   `jq -r '.phase,.pct,.eta_secs' /tmp/bench-autopilot/status.json`. The original
   `bench_dashboard.py` lacks `--oneline`; fall back to status.json + jq if you
   must use it.

5. **Optional extra Pushover from the skill** (the autopilot already pushes
   milestones automatically):
   ```bash
   source "$HOME/dream-fleet-test/lib/notify.sh"   # reads ~/.pushoverrc
   notify_push "MMBT bench" "started N=20 on $(hostname)" 0   # priority 1 bypasses DND
   ```

6. **Auto-recover** — the autopilot does this on its own (endpoint restart,
   stuck-cell kill, idempotent resume). Only intervene by hand if it is wedged
   AND you confirmed it by substance, not a stale mtime. Use the surgical kill
   recipe in the gotchas — never broaden it.

7. **Grade + summarize** — produced per arm automatically when an arm finishes.
   To (re)run on demand (idempotent), once per arm:
   ```bash
   bash "$TOOLING/scripts/grade_microbench.sh" 397b-nothink
   bash "$TOOLING/scripts/summarize.sh"        397b-nothink   # prints PASS/FAIL table
   ```
   The summary table is the headline artifact for the writeup.

8. **Hand off to publish** when `status.json` `phase == "COMPLETE"` (all cells
   present for every arm) — see Publish / reclaim.

## Known gotchas

- **`--reasoning-format none` for the think arm.** The llama.cpp endpoint MUST
  launch with `--reasoning-format none` (the autopilot's `ensure_endpoint`
  already does) so the think arm's reasoning is returned in-band and the grader
  sees the real answer. Keep that flag on any manual relaunch or the think arm
  scores garbage.
- **Arm mode must be in the label.** Run names are keyed by label only.
  `--thinking off`/`on` (and `--reasoning-effort`) MUST be encoded in the label
  (`...-nothink` / `...-think`) or the second arm is silently skipped as
  "already complete". `run_microbench.sh` fails fast on this — heed the error.
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
- **Market cells are slow + stuck-prone.** `p3_market` has no input mount and
  does live-ish research; it runs long and is the most common stuck cell. The
  watchdog fires on transcript-freeze (`stuck_secs`, default 1200s), not wall
  time — a long-but-progressing market cell is NOT stuck. Cross-check
  `current.frozen_secs` vs the threshold before killing.
- **p1 cells make bench.py CPU calls.** `p1_bugfix/testwrite/refactor` run
  `bench.py`/test commands in the sandbox that are CPU-bound, so CPU wall time
  and power spike there even though the model is the GPU workload — expected, not
  a hang and not a thermal failure.
- **Don't trust mtime alone.** Use `stat -c %Y` vs `date +%s` (Unix epoch) for
  freshness; sample `autopilot.log` / the transcript content. `--watch` refresh
  ≠ progress.
- **One autopilot at a time.** Check status.json freshness before launching.

## Publish / reclaim

When `phase == "COMPLETE"`:

1. **Capture headlines** — rerun `summarize.sh` per arm, keep the tables; render
   a static grid: `python3 "$DASH" --html /tmp/bench-autopilot/dashboard.html`.
2. **Publish to the MMBT repo** (this clone's `origin`,
   `Light-Heart-Labs/MMBT-Messy-Model-Bench-Tests`) — branch, commit the new
   `logs/<run>/` artifacts + a findings doc written for an external audience,
   push, open a PR:
   ```bash
   cd "$REPO"
   git checkout -b mmbt-<model>-n<N>-$(date +%Y%m%d)
   git add logs/   # plus the RESULTS/findings doc
   git commit -m "MMBT <model> N=<N>: <one-line headline>"
   git push -u origin HEAD
   gh pr create --fill
   ```
   Follow repo methodology: drift via harness sha256 (not git_sha); keep the
   think-block / market STRUCTURAL_PASS caveats noted.
3. **Reclaim the box** when fully done — free GPU + scratch:
   ```bash
   docker ps -aq --filter name=bench-sandbox- | xargs -r docker rm -f
   docker rm -f llama-397b        # endpoint container (name from config)
   sudo rm -rf "$TOOLING"/workspace/*_v* /tmp/grade_*_v*
   ```
   Leave `/tmp/bench-autopilot/` for the record unless the user wants it gone.
4. **Notify** (optional): `notify_push "MMBT published" "PR opened for <model> N=<N>" 1`.
