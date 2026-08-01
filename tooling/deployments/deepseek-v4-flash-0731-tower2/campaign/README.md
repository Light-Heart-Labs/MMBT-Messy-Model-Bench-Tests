# DeepSeek MMBT campaign supervision

These are the exact user-systemd units and sidecars used for the accepted
DeepSeek V4 Flash campaign.

- Canonical microbench: 12 task families x N=3 = 36 runs.
- Extended matrix: 4 suites x N=3 = 12 runs, started only after the canonical
  status reports exactly 36/36 complete.
- GPU power is sampled every five seconds for both devices.
- The telemetry analyzer attributes samples to runs and writes per-run
  artifacts.
- The cost sidecar writes `cost.json` for every canonical completion.
- The pathology sidecar applies only deterministic MMBT taxonomy labels. It
  intentionally leaves ambiguous `model_stopped` cases for transcript and
  workspace inspection.

The canonical campaign, cost, power, telemetry, and pathology services are
started together. The extended service may also be started at that point; its
runner waits on the canonical 36/36 gate. Sidecars that span both worktrees exit
only after the canonical 36 and extended 12 runs are complete.

Before starting, require clean canonical and extended worktrees, a healthy
`DeepSeek-V4-Flash-0731` endpoint, zero canonical result directories, and both
500 W GPU power caps. Clear or archive `/tmp/bench-autopilot` telemetry from any
non-canonical preflight so campaign attribution begins at a clean timestamp.

Install the units in `~/.config/systemd/user/`, run `systemctl --use
daemon-reload`, then start them. Do not enable automatic boot start until the
campaign is intentionally meant to resume after host reboot.
