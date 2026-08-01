# DeepSeek MMBT campaign supervision

These are the exact user-systemd units and sidecars used for the accepted
DeepSeek V4 Flash campaign.

- Canonical microbench: 12 task families x N=3 = 36 runs.
- Extended matrix: 4 suites x N=3 = 12 initial runs, started only after the
  canonical status reports exactly 36/36 complete. If a 75-PR replicate
  actually terminates at a convenience output cap below the served 1M context,
  preserve and exclude it, then add full-context replacement replicates until
  three valid outcomes exist.
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
only after the canonical 36 and initial extended 12 runs are complete. Restart
the telemetry and pathology sidecars for any full-context replacements; the
replacement supervisor publishes `RUNNING` status before inference and restores
the 12/12 `COMPLETE` fields only after the valid-replicate manifest is final.

Before starting, require clean canonical and extended worktrees, a healthy
`DeepSeek-V4-Flash-0731` endpoint, zero canonical result directories, and both
500 W GPU power caps. Clear or archive `/tmp/bench-autopilot` telemetry from any
non-canonical preflight so campaign attribution begins at a clean timestamp.

Install the units in `~/.config/systemd/user/`, run `systemctl --user
daemon-reload`, then start them. Do not enable automatic boot start until the
campaign is intentionally meant to resume after host reboot.

The authoritative replacement policy and selected valid run names are written
to `logs/_campaign_audit/75pr-valid-replicates.json`. A run that completes
normally below an older cap remains valid because the cap did not constrain its
outcome. A run that exhausts the dynamically calculated remaining 1M context is
a genuine model outcome; only termination at a smaller configured convenience
cap is infrastructure-invalid for the best-capability comparison.

For a replacement campaign, install and start
`mmbt-deepseek-v4-flash-75pr-fullctx.service`, then restart the telemetry and
pathology sidecars after the replacement supervisor has published
`FULLCTX_REPLACEMENTS_STARTING`. The five-second power logger is normally still
active because its unit uses `Restart=always`; verify it rather than assuming.
