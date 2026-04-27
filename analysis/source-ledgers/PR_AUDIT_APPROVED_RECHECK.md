# DreamServer Approved PR Re-Audit

Scope: the 38 PRs previously marked **Approved** in `PR_AUDIT_ROLLING.md`.

Rubric: for each PR, re-check whether it actually solves the stated problem, whether the approach is the best fit for DreamServer, what proof exists or can be run, what breaks if merged, and what adjacent code paths might be missed.

## Rolling Totals

Last updated: after Batch 4

| Status | Count |
| --- | ---: |
| Re-audited | 38 |
| Still approved | 34 |
| Needs work after recheck | 2 |
| Rebase/conflict | 0 |
| Keep draft/dependency blocked | 2 |
| Close/superseded | 0 |
| Not yet re-audited | 0 |

## Batch Plan

| Batch | PRs | Status |
| --- | --- | --- |
| 1 | #1055, #1050, #1049, #1048, #1047, #1046, #1044, #1036, #1035, #1034 | Complete |
| 2 | #1032, #1028, #1027, #1026, #1025, #1023, #1022, #1021, #1014, #1013 | Complete |
| 3 | #1010, #1009, #1008, #1007, #1006, #1005, #1004, #1003, #999, #997 | Complete |
| 4 | #996, #993, #992, #991, #990, #988, #959, #750 | Complete |

## Batch 1

| PR | Recheck status | Notes / proof |
| --- | --- | --- |
| #1055 | Needs work | The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`). |
| #1050 | Still approved | Broad installer/host-agent fix remains directionally right. Syntax checks passed for Linux/macOS shell, PowerShell parse, and `dream-host-agent.py` compile. A stubbed macOS harness proved exFAT becomes fatal and Docker Desktop sharing errors are detected. No new blocking issue found; residual follow-ups remain test coverage and network FS nuance. |
| #1049 | Still approved | Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`. |
| #1048 | Still approved | Single heredoc comment fix is scoped and correct. `bash -n` passes and no backticks remain in the macOS env-generator heredoc output scan. |
| #1047 | Still approved | Langfuse healthcheck sweep is coherent: only `NEXTAUTH_URL` keeps browser-facing `localhost`, while healthcheck URLs move off `localhost`. YAML parse/grep proof passed. |
| #1046 | Still approved | `HOSTNAME=0.0.0.0` is present in Perplexica env and compose config passes with required stack secrets stubbed. This is the right level of fix for a container-internal Next.js bind mismatch. |
| #1044 | Still approved | Port-binding parser/security scanner fix is strong. The 23 new helper/regression tests pass. Full `test_extensions.py` has Windows-local baseline failures around symlink privilege and executable bits, not this PR's parser path. |
| #1036 | Still approved | Removing dead community `privacy-shield` is safer than keeping a rejected/inferior duplicate. Directory removal, README references, and generated catalog id scan all prove it is gone while the built-in service remains unaffected. |
| #1035 | Still approved | OpenClaw post-install recreate is narrow and tested. `tests/test_host_agent.py` passes 43/43, and the compose diff removes only the stale named volume while preserving the workspace bind. |
| #1034 | Still approved | Piper timeout and Milvus 9091 publication compose cleanly. `docker compose config` proves both Milvus ports render correctly and Piper config is valid. Residual adjacent gap: user-extension health scanning still ignores manifest `health_port`, so dashboard health for Milvus may need a separate PR. |

## Batch 2

| PR | Recheck status | Notes / proof |
| --- | --- | --- |
| #1032 | Dependency blocked | The compose `depends_on` additions are correct, including Continue's Apple overlay, but the PR does not solve first-start dashboard installs by itself because the same branch still has host-agent `_handle_install` running `docker compose up -d --no-deps <service>`. Proof: source inspection reports `--no-deps-in-install=True`. Merge after #1021, or stack the host-agent change here. |
| #1028 | Still approved | Embeddings healthcheck `start_period` renders as `10m0s` in `docker compose config`; this solves slow first-start TEI model download without delaying warm healthy starts. |
| #1027 | Dependency blocked | The bind sweep itself is mechanically good (`test-bind-address-sweep.sh` passes and static scan finds no literal community `127.0.0.1` port entries), but on current main the dashboard scanner rejects `${BIND_ADDRESS:-127.0.0.1}`. Direct `_scan_compose_content` proof rejected Continue, Jupyter, and Milvus with 400s. Merge after #1044, or include the scanner update in this PR. |
| #1026 | Still approved | All installers write `setup-complete.json` and syntax/PowerShell parse checks pass. Placement is after the install success path and write failure remains non-fatal, matching the dashboard's `.exists()` first-run contract. |
| #1025 | Still approved | Apple Silicon `/api/gpu/detailed` wiring is clean. `pytest tests/test_gpu_detailed.py -k "not history"` passes 19/19, and the Apple aggregate-to-single-card mapping is constrained to `GPU_BACKEND=apple`. |
| #1023 | Still approved | The `head` to `sed -n '1p'` sweep is the right pipefail-safe repair. Syntax checks passed on all changed scripts, and a `set -euo pipefail` reproduction with multi-line input returned the first line cleanly. |
| #1022 | Still approved | Async hygiene changes are well scoped. The three new narrowing/to-thread cleanup tests pass, and the old network-failure fallback behavior remains while programmer errors now surface. |
| #1021 | Still approved | Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40. |
| #1014 | Still approved | Test-only grep repair is correct. `test-doctor-extension-diagnostics.sh` now passes 9/9 under Git Bash. |
| #1013 | Still approved | macOS upgrade upsert for `DREAM_AGENT_KEY` is present and `bash -n` passes. `.env.example` documents the key. Residual follow-up remains the stale `.env.schema.json` description that still mentions fallback to `DASHBOARD_API_KEY`. |

## Batch 3

| PR | Recheck status | Notes / proof |
| --- | --- | --- |
| #1010 | Still approved | Schema secret flips are correct and covered. Targeted pytest for all five provider-key flags passes 5/5. This also complements, but does not replace, the broader jq-absent masking gap found earlier in #994. |
| #1009 | Still approved | Image generation default now behaves correctly: base renders `false`, NVIDIA/AMD overlays respect explicit `ENABLE_IMAGE_GENERATION=false`, and DreamForge standalone compose now validates without a pre-existing external network. |
| #1008 | Still approved | Pipefail guards are the right prerequisite for strict-mode PRs. `bash -n` passes and a missing-key reproduction under `set -eo pipefail` returns empty without aborting. |
| #1007 | Still approved | The RETURN trap fix solves the nounset crash path and syntax passes. Local reproduction of the nested RETURN trap exits cleanly. Still merge before any nounset-enabling PR. |
| #1006 | Still approved | Moving `log()` / `warn()` to stderr is correct for captured command output and machine-readable stdout. `bash -n` passes and a direct helper call leaves stdout empty while diagnostics go to stderr. |
| #1005 | Still approved | macOS install polish is scoped and sound: `DIM` is defined, `busybox` is pinned to `1.36.1`, and shell syntax passes. The healthcheck rewrite preserves host-native HTTP probes while using Docker health for containerized services. |
| #1004 | Still approved | Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it. |
| #1003 | Still approved | Setup sentinel behavior is proven enough: dashboard Vitest suite passes 35/35; backend stream tests on this Windows host could only exercise failure sentinel because `bash` resolves to broken WSL, but the response still includes the machine sentinel. The primary script and frontend hardening remain coherent. |
| #999 | Still approved | Apple Silicon CLI/doctor branches are gated on `GPU_BACKEND=apple`; syntax passes for `dream-cli` and `dream-doctor.sh`, and static inspection confirms sysctl/df portability fixes plus the Apple GPU skip paths. |
| #997 | Still approved | `dream shell` validation/preflight changes are sensible and syntax passes. The `perl alarm` timeout proof is not valid under Git Bash on Windows, but the targeted platforms are macOS/Linux/WSL2 where Perl is part of the host environment. |

## Batch 4

| PR | Recheck status | Notes / proof |
| --- | --- | --- |
| #996 | Still approved | Windows installer now generates and preserves `DREAM_AGENT_KEY` separately from `DASHBOARD_API_KEY`. PowerShell parser checks passed for all changed `.ps1` files, and static proof shows `DREAM_AGENT_KEY` is written to `.env` and returned as `DreamAgentKey` with stale `DashboardKey` output removed. |
| #993 | Still approved | CLI visual polish is safe. `bash -n dream-cli` passes, and `NO_COLOR= dream-cli help` redirected to a file emitted 5,361 bytes with zero ESC bytes, so non-TTY output stays clean. |
| #992 | Still approved | `OPENCLAW_TOKEN=CHANGEME` is now documented in `.env.example`, satisfying OpenClaw's required interpolation. A base+SearXNG+OpenClaw compose config using `.env.example` passes; the standalone OpenClaw fragment still correctly needs base services for its `open-webui` override and SearXNG dependency. |
| #991 | Still approved | Claude Code Action pin bump is mechanical. All three changed workflows reference the new pinned SHA, and YAML parsing passes for `ai-issue-triage.yml`, `claude-review.yml`, and `release-notes.yml`. |
| #990 | Still approved | `actions/github-script` v9 pin bump is safe for the touched scripts: no `require('@actions/github')` / `getOctokit` pattern is present, scripts use the injected `github.rest`, and YAML parsing passes for both changed workflows. |
| #988 | Still approved | Loopback/default bind hardening is coherent. Shell syntax checks pass for macOS/bootstrap scripts, PowerShell parser checks pass for Windows launchers, and `dream-host-agent.py` compiles. Linux bridge detection still binds to the bridge IP when available and falls back to loopback with an explicit warning. |
| #959 | Still approved | Token Spy docs now clearly mark `resources/products/token-spy` as prototype/incubator material and point operators at the shipped extension for production behavior. This is documentation-only and reduces the earlier mismatch risk without touching runtime code. |
| #750 | Needs work | AMD multi-GPU architecture is directionally right, and the dashboard AMD tests pass 16/16, `assign_gpus.py` handles a synthetic 4-GPU XGMI topology, and compose config for the AMD multi-GPU core stack passes. However, several resolver call sites added/used by the install and CLI paths omit `--gpu-count`, so a `GPU_COUNT=2` AMD stack resolves to only `docker-compose.base.yml + docker-compose.amd.yml` instead of also including `docker-compose.multigpu-amd.yml`. Phase 03/11 refreshes can therefore overwrite the correct Phase 02 flags and cache a non-multi-GPU stack. Local shell topology test could not run on this Windows host because `jq` is not installed. |
