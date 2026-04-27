# DreamServer 75 PR Review - Complete Reference

Date: 2026-04-27

This is the consolidated reference for the 75 open DreamServer PR audit. It is intended to be read later without needing to reconcile separate files by hand.

## How To Read This

- The **Final Verdict Index** below is authoritative.
- The **Detailed First-Pass Audit Ledger** covers all 75 PRs in the original batch order, including notes and proof logs.
- The **Approved PR Re-Audit Ledger** supersedes first-pass details for the 38 PRs that were originally approved.
- Four PRs changed verdict in the second pass: #1055, #750, #1032, and #1027.

## Coverage Check

| Item | Count |
|---|---:|
| Unique PRs in final index | 75 |
| Expected PRs | 75 |

## Final Accounting

# DreamServer 75 PR Review - Final Accounting

Date: 2026-04-27

This file summarizes the final verdicts after the full 75-PR deep audit and the second-pass re-audit of the PRs that were originally marked approved.

## Final Totals

| Status | Count |
|---|---:|
| Total PRs audited | 75 |
| Approved / mergeable | 34 |
| Needs work | 25 |
| Keep draft / dependency blocked | 11 |
| Rebase / conflict before merge | 4 |
| Close / superseded | 1 |
| Unaudited | 0 |

## Second-Pass Changes

The approved pool dropped from 38 to 34 after re-auditing the originally approved PRs.

| PR | First-pass verdict | Final verdict | Reason |
|---:|---|---|---|
| #1055 | Approved | Needs work | Native API development docs break the dashboard nginx `/api` proxy path if the `dashboard-api` container is stopped. |
| #750 | Approved | Needs work | AMD multi-GPU resolver call sites omit `--gpu-count`, allowing install/CLI refreshes to drop multi-GPU compose overlays. |
| #1032 | Approved | Dependency blocked | Compose `depends_on` is correct, but the branch still has the host-agent install path using `up -d --no-deps`; merge after #1021 or include that fix. |
| #1027 | Approved | Dependency blocked | Bind-address sweep requires the scanner parser update from #1044; otherwise dashboard installs reject `${BIND_ADDRESS:-127.0.0.1}` ports. |

## Files In This Review Set

- `PR_AUDIT_ROLLING.md` - original 75-PR batch audit ledger.
- `PR_AUDIT_APPROVED_RECHECK.md` - second-pass audit of the originally approved PRs.
- `PR_AUDIT_FINAL_ACCOUNTING.md` - this summary.

## Practical Merge Guidance

34 PRs remain good merge candidates, subject to normal CI and merge-order hygiene.

The remaining 41 should not be merged as-is:

- 25 need implementation or test fixes.
- 11 are draft or dependency-blocked.
- 4 need rebase/conflict cleanup.
- 1 should be closed or treated as superseded.


## Final Verdict Index

| PR | Final Verdict | Source | Detail |
|---:|---|---|---|
| #1057 | needs work | First pass | Narrows pull to the target extension, but pull can omit dependency compose files that `up` still uses; also conflicts in the integrated ready queue and should be dependency-aware/rebased. |
| #1056 | needs work | First pass | GPU scanner improvement is directionally right, but malformed `deploy.resources` can still 500; scanner threat model should be tightened before merge. |
| #1054 | needs work | First pass | Catalog/UI installability is fixed, but direct API install still accepts library entries without deployable `compose.yaml`. |
| #1045 | needs work | First pass | Moving config sync to the host-agent is the right boundary, but the copy contract can overwrite unrelated service config trees. |
| #1044 | Still approved | Approved recheck | Port-binding parser/security scanner fix is strong. The 23 new helper/regression tests pass. Full `test_extensions.py` has Windows-local baseline failures around symlink privilege and executable bits, not this PR's parser path. |
| #1039 | keep draft | First pass | Depends on #1030, which needs work; keep blocked until the install-state semantics are fixed. |
| #1038 | rebase/conflict | First pass | PR says it must merge after #1031, but #1031 is closed unmerged; needs rebase/retarget or an explicit replacement story. |
| #1037 | keep draft | First pass | Draft and also stacked on closed-unmerged #1031; useful UI idea, but not merge-ready. |
| #1030 | needs work | First pass | Adds useful bind precreation/state verification, but its own regression test fails and the running-only verifier breaks intentional one-shot extensions. |
| #1021 | Still approved | Approved recheck | Removing `--no-deps` from the install start path is necessary for sidecars/cross-extension deps, while recreate keeps `--no-deps`. `tests/test_host_agent.py` passes 40/40. |
| #1050 | Still approved | Approved recheck | Broad installer/host-agent fix remains directionally right. Syntax checks passed for Linux/macOS shell, PowerShell parse, and `dream-host-agent.py` compile. A stubbed macOS harness proved exFAT becomes fatal and Docker Desktop sharing errors are detected. No new blocking issue found; residual follow-ups remain test coverage and network FS nuance. |
| #1048 | Still approved | Approved recheck | Single heredoc comment fix is scoped and correct. `bash -n` passes and no backticks remain in the macOS env-generator heredoc output scan. |
| #1043 | needs work | First pass | Fixes custom-menu `n` answers for most services, but leaves `embeddings` enabled when RAG is disabled, so opt-out still pulls/starts a RAG service. |
| #1026 | Still approved | Approved recheck | All installers write `setup-complete.json` and syntax/PowerShell parse checks pass. Placement is after the install success path and write failure remains non-fatal, matching the dashboard's `.exists()` first-run contract. |
| #1013 | Still approved | Approved recheck | macOS upgrade upsert for `DREAM_AGENT_KEY` is present and `bash -n` passes. `.env.example` documents the key. Residual follow-up remains the stale `.env.schema.json` description that still mentions fallback to `DASHBOARD_API_KEY`. |
| #1012 | rebase/conflict | First pass | Refactor is safe by itself, but conflicts with #996 in the Windows env-generator return hash; resolve after deciding whether `DreamAgentKey` should remain returned. |
| #1005 | Still approved | Approved recheck | macOS install polish is scoped and sound: `DIM` is defined, `busybox` is pinned to `1.36.1`, and shell syntax passes. The healthcheck rewrite preserves host-native HTTP probes while using Docker health for containerized services. |
| #996 | Still approved | Approved recheck | Windows installer now generates and preserves `DREAM_AGENT_KEY` separately from `DASHBOARD_API_KEY`. PowerShell parser checks passed for all changed `.ps1` files, and static proof shows `DREAM_AGENT_KEY` is written to `.env` and returned as `DreamAgentKey` with stale `DashboardKey` output removed. |
| #988 | Still approved | Approved recheck | Loopback/default bind hardening is coherent. Shell syntax checks pass for macOS/bootstrap scripts, PowerShell parser checks pass for Windows launchers, and `dream-host-agent.py` compiles. Linux bridge detection still binds to the bridge IP when available and falls back to loopback with an explicit warning. |
| #974 | needs work | First pass | Replaces bare Docker calls in most places, but OpenClaw recreation can still invoke an empty compose command when no compose binary is available. |
| #1049 | Still approved | Approved recheck | Exec-form Jupyter command does solve the shell-splitting issue. `docker compose config --format json` with `JUPYTER_TOKEN='my token with spaces'` renders one argv element `--NotebookApp.token=my token with spaces` and preserves `--NotebookApp.password=`. |
| #1047 | Still approved | Approved recheck | Langfuse healthcheck sweep is coherent: only `NEXTAUTH_URL` keeps browser-facing `localhost`, while healthcheck URLs move off `localhost`. YAML parse/grep proof passed. |
| #1046 | Still approved | Approved recheck | `HOSTNAME=0.0.0.0` is present in Perplexica env and compose config passes with required stack secrets stubbed. This is the right level of fix for a container-internal Next.js bind mismatch. |
| #1040 | keep draft | First pass | Good Langfuse Linux UID hook and tests pass, but it is explicitly stacked on #1030, which needs work; keep draft until that base is fixed. |
| #1036 | Still approved | Approved recheck | Removing dead community `privacy-shield` is safer than keeping a rejected/inferior duplicate. Directory removal, README references, and generated catalog id scan all prove it is gone while the built-in service remains unaffected. |
| #1035 | Still approved | Approved recheck | OpenClaw post-install recreate is narrow and tested. `tests/test_host_agent.py` passes 43/43, and the compose diff removes only the stale named volume while preserving the workspace bind. |
| #1034 | Still approved | Approved recheck | Piper timeout and Milvus 9091 publication compose cleanly. `docker compose config` proves both Milvus ports render correctly and Piper config is valid. Residual adjacent gap: user-extension health scanning still ignores manifest `health_port`, so dashboard health for Milvus may need a separate PR. |
| #1033 | needs work | First pass | LibreChat guard is good, but the Jupyter half does not actually remove stack-level token poisoning and overlaps with #1049. Split/rebase and keep only the LibreChat fix. |
| #1032 | Dependency blocked | Approved recheck | The compose `depends_on` additions are correct, including Continue's Apple overlay, but the PR does not solve first-start dashboard installs by itself because the same branch still has host-agent `_handle_install` running `docker compose up -d --no-deps <service>`. Proof: source inspection reports `--no-deps-in-install=True`. Merge after #1021, or stack the host-agent change here. |
| #1028 | Still approved | Approved recheck | Embeddings healthcheck `start_period` renders as `10m0s` in `docker compose config`; this solves slow first-start TEI model download without delaying warm healthy starts. |
| #1051 | needs work | First pass | Better user-extension fallback than #1029, but it omits the `gpu_backends` filter for user extensions; an AMD-only user extension is still included on an NVIDIA stack. |
| #1029 | needs work | First pass | Dedupe direction is good and manifest-declared GPU filtering works, but the resolver now silently drops legacy/custom user extensions that have `compose.yaml` but no manifest. |
| #1024 | needs work | First pass | Array expansion reduces glob risk, but the claimed path-with-spaces fix is not real because `read -ra` still splits a flat `COMPOSE_FLAGS` string on whitespace. |
| #1023 | Still approved | Approved recheck | The `head` to `sed -n '1p'` sweep is the right pipefail-safe repair. Syntax checks passed on all changed scripts, and a `set -euo pipefail` reproduction with multi-line input returned the first line cleanly. |
| #1018 | needs work | First pass | Draft adds useful BATS coverage and several real fixes, but turning on `set -euo pipefail` still breaks the version fallback when `.env` lacks `DREAM_VERSION`. |
| #1016 | keep draft | First pass | Good Apple GPU/status polish and compose summary wrapper direction; keep draft while the focused split PRs (#1006/#1007/#1008/#1023) land first. |
| #1011 | keep draft | First pass | Bash 4 guard concept is reasonable and scripts parse, but it is still draft and should be reconciled with the larger pipefail/Bash compatibility stack before merge. |
| #1008 | Still approved | Approved recheck | Pipefail guards are the right prerequisite for strict-mode PRs. `bash -n` passes and a missing-key reproduction under `set -eo pipefail` returns empty without aborting. |
| #1007 | Still approved | Approved recheck | The RETURN trap fix solves the nounset crash path and syntax passes. Local reproduction of the nested RETURN trap exits cleanly. Still merge before any nounset-enabling PR. |
| #1006 | Still approved | Approved recheck | Moving `log()` / `warn()` to stderr is correct for captured command output and machine-readable stdout. `bash -n` passes and a direct helper call leaves stdout empty while diagnostics go to stderr. |
| #1025 | Still approved | Approved recheck | Apple Silicon `/api/gpu/detailed` wiring is clean. `pytest tests/test_gpu_detailed.py -k "not history"` passes 19/19, and the Apple aggregate-to-single-card mapping is constrained to `GPU_BACKEND=apple`. |
| #1022 | Still approved | Approved recheck | Async hygiene changes are well scoped. The three new narrowing/to-thread cleanup tests pass, and the old network-failure fallback behavior remains while programmer errors now surface. |
| #1020 | keep draft | First pass | Useful Apple GPU/doctor contract coverage, but still draft and overlaps with #1016; local Apple test script was blocked here by missing `jq`, while the Darwin contract correctly skipped off-macOS. |
| #1019 | needs work | First pass | Backend/frontend build pieces are directionally good, but the new frontend tests fail as written because mocks are consumed by step-2 fetches, and the new a11y assertion catches an unhidden `HardDrive` icon. |
| #1015 | keep draft | First pass | Good defensive follow-up to template status and JSON parse handling; dashboard build passes, but keep draft until it is stacked/rebased with #1003/#1019 decisions. |
| #1014 | Still approved | Approved recheck | Test-only grep repair is correct. `test-doctor-extension-diagnostics.sh` now passes 9/9 under Git Bash. |
| #1010 | Still approved | Approved recheck | Schema secret flips are correct and covered. Targeted pytest for all five provider-key flags passes 5/5. This also complements, but does not replace, the broader jq-absent masking gap found earlier in #994. |
| #1009 | Still approved | Approved recheck | Image generation default now behaves correctly: base renders `false`, NVIDIA/AMD overlays respect explicit `ENABLE_IMAGE_GENERATION=false`, and DreamForge standalone compose now validates without a pre-existing external network. |
| #1003 | Still approved | Approved recheck | Setup sentinel behavior is proven enough: dashboard Vitest suite passes 35/35; backend stream tests on this Windows host could only exercise failure sentinel because `bash` resolves to broken WSL, but the response still includes the machine sentinel. The primary script and frontend hardening remain coherent. |
| #1002 | needs work | First pass | Broad nounset/pipefail draft repeats the `DREAM_VERSION` grep-pipeline abort that #1008 fixes; keep out until that guard lands. |
| #1055 | Needs work | Approved recheck | The doc correctly identifies the baked `/app` trap, but the recommended native-uvicorn workflow falsely says the dashboard container will reach the host API through `host.docker.internal`. In current compose, the dashboard nginx proxy still targets `http://dashboard-api:3002`; after `docker compose stop dashboard-api`, the normal UI `/api` path is broken unless the contributor also runs the Vite dev server or changes the nginx/proxy path. Link checks passed (`links-ok 2`). |
| #1000 | needs work | First pass | JSON modes are useful, but `dream list --json` can be polluted by `sr_load` warnings on stdout when PyYAML is missing, making the JSON invalid. |
| #999 | Still approved | Approved recheck | Apple Silicon CLI/doctor branches are gated on `GPU_BACKEND=apple`; syntax passes for `dream-cli` and `dream-doctor.sh`, and static inspection confirms sysctl/df portability fixes plus the Apple GPU skip paths. |
| #998 | needs work | First pass | Draft pipefail/exit-code work repeats the `_check_version_compat` grep-pipeline abort fixed by #1008. |
| #997 | Still approved | Approved recheck | `dream shell` validation/preflight changes are sensible and syntax passes. The `perl alarm` timeout proof is not valid under Git Bash on Windows, but the targeted platforms are macOS/Linux/WSL2 where Perl is part of the host environment. |
| #994 | needs work | First pass | Schema-driven masking works only when `jq` is available; without `jq`, newly schema-secret user/email fields still print in clear. |
| #993 | Still approved | Approved recheck | CLI visual polish is safe. `bash -n dream-cli` passes, and `NO_COLOR= dream-cli help` redirected to a file emitted 5,361 bytes with zero ESC bytes, so non-TTY output stays clean. |
| #992 | Still approved | Approved recheck | `OPENCLAW_TOKEN=CHANGEME` is now documented in `.env.example`, satisfying OpenClaw's required interpolation. A base+SearXNG+OpenClaw compose config using `.env.example` passes; the standalone OpenClaw fragment still correctly needs base services for its `open-webui` override and SearXNG dependency. |
| #991 | Still approved | Approved recheck | Claude Code Action pin bump is mechanical. All three changed workflows reference the new pinned SHA, and YAML parsing passes for `ai-issue-triage.yml`, `claude-review.yml`, and `release-notes.yml`. |
| #990 | Still approved | Approved recheck | `actions/github-script` v9 pin bump is safe for the touched scripts: no `require('@actions/github')` / `getOctokit` pattern is present, scripts use the injected `github.rest`, and YAML parsing passes for both changed workflows. |
| #1053 | needs work | First pass | The OpenClaw CI gate catches unexpected write paths, but its positive assertion only warns when the expected `openclaw.json` write never happens; a crash-before-write can still false-green. |
| #1052 | keep draft | First pass | Useful structural guard for the Langfuse hook, but the PR branch fails its own tests until it is stacked on or retargeted to the hook implementation. |
| #1042 | needs work | First pass | Support bundle feature is useful and mostly works, but `--json` emits Windows paths under Git Bash that the PR's own Bash test cannot feed back to `tar`. |
| #1017 | keep draft | First pass | Security-doc update is the right follow-up to #988, but the branch carries the #988 code/docs stack; keep draft until #988 lands and this is rebased to the docs-only delta. |
| #973 | needs work | First pass | Good broad documentation pass, but it will be stale against the safer host-agent bind fallback from #988/#1017; rebase/update before merging after the security fix. |
| #966 | close/supersede | First pass | Current diff from the merge base is empty; the platform-doc content has effectively been absorbed or reverted in later work, so keeping the PR open adds queue noise. |
| #959 | Still approved | Approved recheck | Token Spy docs now clearly mark `resources/products/token-spy` as prototype/incubator material and point operators at the shipped extension for production behavior. This is documentation-only and reduces the earlier mismatch risk without touching runtime code. |
| #716 | needs work | First pass | The validation env-file approach is correct, but the PR also weakens real extension templates by replacing required secrets with known/empty defaults. |
| #364 | rebase/conflict | First pass | Large old runtime API feature is merge-dirty and also removes unrelated core/agents router test coverage; rebase and restore coverage before reconsidering. |
| #351 | rebase/conflict | First pass | Contains a literal conflict marker in `tests/test_routers.py`, so Python cannot parse the test module. |
| #983 | needs work | First pass | The p2p GPU toolkit is self-contained and shell syntax passes, but the advertised NVIDIA driver/library mismatch repair is not actually reachable because exit statuses are lost under `!` and `set -e`. Also has `git diff --check` whitespace failures. |
| #961 | needs work | First pass | Mobile preview dispatch and syntax are broadly coherent, but the Android localhost automation bridge lacks an origin/token gate on action POST endpoints; malicious local-browser pages can trigger automation requests. |
| #750 | Needs work | Approved recheck | AMD multi-GPU architecture is directionally right, and the dashboard AMD tests pass 16/16, `assign_gpus.py` handles a synthetic 4-GPU XGMI topology, and compose config for the AMD multi-GPU core stack passes. However, several resolver call sites added/used by the install and CLI paths omit `--gpu-count`, so a `GPU_COUNT=2` AMD stack resolves to only `docker-compose.base.yml + docker-compose.amd.yml` instead of also including `docker-compose.multigpu-amd.yml`. Phase 03/11 refreshes can therefore overwrite the correct Phase 02 flags and cache a non-multi-GPU stack. Local shell topology test could not run on this Windows host because `jq` is not installed. |
| #1027 | Dependency blocked | Approved recheck | The bind sweep itself is mechanically good (`test-bind-address-sweep.sh` passes and static scan finds no literal community `127.0.0.1` port entries), but on current main the dashboard scanner rejects `${BIND_ADDRESS:-127.0.0.1}`. Direct `_scan_compose_content` proof rejected Continue, Jupyter, and Milvus with 400s. Merge after #1044, or include the scanner update in this PR. |
| #1004 | Still approved | Approved recheck | Resolver skips `compose.local.yaml` on Apple while preserving it for non-Apple backends. Synthetic fixture proof: Apple output omitted `compose.local.yaml`; NVIDIA output included it. |

---

# Detailed First-Pass Audit Ledger

# DreamServer PR Deep Audit

Scope: 75 open PRs in `Light-Heart-Labs/DreamServer`, audited in risk-aware batches.

Rubric for every PR:

- Claim check: what problem is claimed, and is it real on current `main`?
- Implementation review: does the diff actually solve the problem, including edge cases?
- Fit for DreamServer: does it match the architecture, trust model, platforms, and UX?
- Proof: what tests/commands prove it, and what remains unproven?
- Merge risk: what breaks if merged alone or with nearby PRs?
- Blind spots: what adjacent code paths were not considered?
- Verdict: `approved`, `needs work`, `rebase/conflict`, `keep draft`, or `close/supersede`.

## Rolling Totals

Last updated: Batch 8 complete.

| Metric | Count |
|---|---:|
| Total open PRs in scope | 75 |
| Deep-audited | 75 |
| Approved | 38 |
| Needs work | 23 |
| Rebase/conflict before merge | 4 |
| Keep draft / dependency blocked | 9 |
| Close / superseded | 1 |
| Not yet audited | 0 |

## Batch Plan

1. Extension Install / Host-Agent Lifecycle:
   #1057, #1056, #1054, #1045, #1044, #1039, #1038, #1037, #1030, #1021
2. Installer / Platform / Security:
   #1050, #1048, #1043, #1026, #1013, #1012, #1005, #996, #988, #974
3. Extension Compose / Service Library:
   #1049, #1047, #1046, #1040, #1036, #1035, #1034, #1033, #1032, #1028
4. Resolver / Scripts / CLI Foundations:
   #1051, #1029, #1024, #1023, #1018, #1016, #1011, #1008, #1007, #1006
5. Dashboard / Setup / API Workflows:
   #1025, #1022, #1020, #1019, #1015, #1014, #1010, #1009, #1003, #1002
6. CLI UX / Apple-GPU / CI-Deps / Docs Small:
   #1055, #1000, #999, #998, #997, #994, #993, #992, #991, #990
7. Docs / Support / CI Gates / Conflicting Older PRs:
   #1053, #1052, #1042, #1017, #973, #966, #959, #716, #364, #351
8. Large Feature PRs / Broad Blast Radius:
   #983, #961, #750, #1027, #1004

## Batch 1: Extension Install / Host-Agent Lifecycle

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1057 | needs work | Narrows pull to the target extension, but pull can omit dependency compose files that `up` still uses; also conflicts in the integrated ready queue and should be dependency-aware/rebased. |
| #1056 | needs work | GPU scanner improvement is directionally right, but malformed `deploy.resources` can still 500; scanner threat model should be tightened before merge. |
| #1054 | needs work | Catalog/UI installability is fixed, but direct API install still accepts library entries without deployable `compose.yaml`. |
| #1045 | needs work | Moving config sync to the host-agent is the right boundary, but the copy contract can overwrite unrelated service config trees. |
| #1044 | approved | Accepts `${VAR:-127.0.0.1}` without weakening the no-LAN-bind policy; targeted loopback/default-variable tests pass. |
| #1039 | keep draft | Depends on #1030, which needs work; keep blocked until the install-state semantics are fixed. |
| #1038 | rebase/conflict | PR says it must merge after #1031, but #1031 is closed unmerged; needs rebase/retarget or an explicit replacement story. |
| #1037 | keep draft | Draft and also stacked on closed-unmerged #1031; useful UI idea, but not merge-ready. |
| #1030 | needs work | Adds useful bind precreation/state verification, but its own regression test fails and the running-only verifier breaks intentional one-shot extensions. |
| #1021 | approved | Correctly removes `--no-deps` from install `up`, so extension sidecars/dependencies start; targeted regression tests pass. |

Proof log:

- #1021: `pytest tests/test_host_agent.py::TestInstallStartCommandNoDeps -q` passed, 2 tests.
- #1044: `pytest tests/test_extensions.py -k "loopback or bind_address or split_port_host" -q` passed, 15 tests.
- #1030: targeted PR regression test was run earlier and fails as written; integrated dashboard-api host-agent/extension suite also exposes the same failing assertion plus local Windows symlink/chmod portability failures.

## Batch 2: Installer / Platform / Security

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1050 | approved | Good platform preflight: blocks non-POSIX install paths before secrets are written and adds Docker Desktop bind-mount probes. Broad, but bounded to installer/host-agent FS handling. |
| #1048 | approved | Correct one-line macOS heredoc fix: prevents backtick command substitution while writing the `.env` comment. |
| #1043 | needs work | Fixes custom-menu `n` answers for most services, but leaves `embeddings` enabled when RAG is disabled, so opt-out still pulls/starts a RAG service. |
| #1026 | approved | Pre-marking setup complete matches dashboard-api's first-run check and is non-fatal on write failure; installer contract grep checks pass. |
| #1013 | approved | Correct macOS upgrade-path fix: existing `.env` files get a missing `DREAM_AGENT_KEY` without rotating existing secrets. |
| #1012 | rebase/conflict | Refactor is safe by itself, but conflicts with #996 in the Windows env-generator return hash; resolve after deciding whether `DreamAgentKey` should remain returned. |
| #1005 | approved | macOS health-check rewrite and busybox pin are reasonable; shell syntax passes. |
| #996 | approved | Windows installer now writes and preserves `DREAM_AGENT_KEY`; PowerShell parser checks pass. |
| #988 | approved | Security fix binds native llama-server and host-agent fallbacks to loopback by default while preserving explicit `BIND_ADDRESS`; parse/compile checks pass. |
| #974 | needs work | Replaces bare Docker calls in most places, but OpenClaw recreation can still invoke an empty compose command when no compose binary is available. |

Proof log:

- #1050: Git Bash `bash -n` passed for changed shell scripts; PowerShell parser passed for Windows preflight; local `DriveInfo` probe works with a non-root Windows path.
- #1048, #1013, #1005, #1043, #974: Git Bash `bash -n` passed for changed shell files.
- #996, #1012, #988: PowerShell parser checks passed for changed Windows scripts.
- #988: `python -m py_compile dream-server/bin/dream-host-agent.py` passed.
- #1026: changed shell scripts parse; specific setup-complete contract grep checks pass. Full contract script was not runnable in this environment because Git Bash lacks `jq`.

## Batch 3: Extension Compose / Service Library

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1049 | approved | Jupyter exec-form command is the better fix for shell splitting; compose config passes with `JUPYTER_TOKEN` set. |
| #1047 | approved | Langfuse healthchecks correctly avoid `localhost` ambiguity; merged config passes when the LiteLLM fragment and expected secrets are present. |
| #1046 | approved | Perplexica gets the needed container-internal `HOSTNAME=0.0.0.0`; compose config with SearXNG passes. |
| #1040 | keep draft | Good Langfuse Linux UID hook and tests pass, but it is explicitly stacked on #1030, which needs work; keep draft until that base is fixed. |
| #1036 | approved | Removes only the dead community-library privacy-shield duplicate; production privacy-shield remains. |
| #1035 | approved | OpenClaw install now recreates Open WebUI so overlay env applies; targeted host-agent tests pass and merged config has no stale `openclaw-home` volume. |
| #1034 | approved | Piper timeout and Milvus health-port publication compose-validate cleanly; watch merge order because this file conflicted in the integrated queue. |
| #1033 | needs work | LibreChat guard is good, but the Jupyter half does not actually remove stack-level token poisoning and overlaps with #1049. Split/rebase and keep only the LibreChat fix. |
| #1032 | approved | Mirrors manifest dependencies into compose without deadlocking Apple; nvidia/apple/localai/anythingllm compose configs pass. |
| #1028 | approved | Embeddings start period increase is low-risk and matches slow TEI cold-start behavior; compose config passes. |

Proof log:

- #1049, #1046, #1047, #1034, #1033, #1032, #1028: `docker compose config --quiet` passed for the changed fragments with required env/dependency fragments supplied.
- #1035: `pytest tests/test_host_agent.py -q` passed, 43 tests; compose config contains no `openclaw-home`.
- #1040: `pytest tests/test_host_agent.py -q` passed, 44 tests; hook/reproducer shell syntax and host-agent `py_compile` pass.
- #1036: verified community-library `privacy-shield` path is gone while production `dream-server/extensions/services/privacy-shield/manifest.yaml` remains.

## Batch 4: Resolver / Scripts / CLI Foundations

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1051 | needs work | Better user-extension fallback than #1029, but it omits the `gpu_backends` filter for user extensions; an AMD-only user extension is still included on an NVIDIA stack. |
| #1029 | needs work | Dedupe direction is good and manifest-declared GPU filtering works, but the resolver now silently drops legacy/custom user extensions that have `compose.yaml` but no manifest. |
| #1024 | needs work | Array expansion reduces glob risk, but the claimed path-with-spaces fix is not real because `read -ra` still splits a flat `COMPOSE_FLAGS` string on whitespace. |
| #1023 | approved | SIGPIPE-safe `sed -n '1p'` replacements are narrow and parse cleanly across the touched scripts. |
| #1018 | needs work | Draft adds useful BATS coverage and several real fixes, but turning on `set -euo pipefail` still breaks the version fallback when `.env` lacks `DREAM_VERSION`. |
| #1016 | keep draft | Good Apple GPU/status polish and compose summary wrapper direction; keep draft while the focused split PRs (#1006/#1007/#1008/#1023) land first. |
| #1011 | keep draft | Bash 4 guard concept is reasonable and scripts parse, but it is still draft and should be reconciled with the larger pipefail/Bash compatibility stack before merge. |
| #1008 | approved | Correctly makes missing `.env` keys safe under future `pipefail`; targeted reproduction survives with an empty `DREAM_VERSION`. |
| #1007 | approved | Narrow trap-quoting fix for `gpu reassign`; syntax passes and blast radius is tiny. |
| #1006 | approved | Routing `log` and `warn` to stderr is the right contract for command substitution/capture sites; syntax passes. |

Proof log:

- #1051/#1029: synthetic resolver fixtures with manifestless, NVIDIA-only, and AMD-only user extensions proved the regressions: #1029 dropped the manifestless extension, while #1051 included the AMD-only extension on `--gpu-backend nvidia`.
- #1024: direct `read -ra` reproduction split `-f /tmp/path with spaces/compose.yml` into four arguments, so the flat-string contract remains unsafe for paths with spaces.
- #1018: exact `_check_version_compat` pipeline under `set -euo pipefail` exited when `.env` lacked `DREAM_VERSION`, before `.version` fallback could run. The included `test-validate-env.sh` was attempted but could not complete because this Git Bash environment lacks `jq`.
- #1023/#1024/#1016/#1011/#1008/#1007/#1006: Git Bash `bash -n` passed for touched shell scripts; #1018 dashboard-api setup router also passed `py_compile`.

## Batch 5: Dashboard / Setup / API Workflows

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1025 | approved | Correctly wires Apple Silicon into `/api/gpu/detailed` as a single aggregate GPU and includes endpoint coverage. |
| #1022 | approved | Moves blocking host-agent log/health calls off the async path and narrows swallowed exceptions; targeted async-hygiene tests pass. |
| #1020 | keep draft | Useful Apple GPU/doctor contract coverage, but still draft and overlaps with #1016; local Apple test script was blocked here by missing `jq`, while the Darwin contract correctly skipped off-macOS. |
| #1019 | needs work | Backend/frontend build pieces are directionally good, but the new frontend tests fail as written because mocks are consumed by step-2 fetches, and the new a11y assertion catches an unhidden `HardDrive` icon. |
| #1015 | keep draft | Good defensive follow-up to template status and JSON parse handling; dashboard build passes, but keep draft until it is stacked/rebased with #1003/#1019 decisions. |
| #1014 | approved | Test-only repair is correct: the doctor script now has the two summary counters on separate lines, so the assertion should not require same-line text. |
| #1010 | approved | Schema secret flips are appropriate for provider credentials; JSON/schema-targeted tests pass. |
| #1009 | approved | Image generation default now matches platform capability: base/CPU/Apple default off, AMD/NVIDIA default on; compose config passes, including DreamForge network normalization. |
| #1003 | approved | Sentinel-based setup success detection is a real improvement and dashboard build passes; later drafts add tests/edge hardening but this PR is mergeable on its own. |
| #1002 | needs work | Broad nounset/pipefail draft repeats the `DREAM_VERSION` grep-pipeline abort that #1008 fixes; keep out until that guard lands. |

Proof log:

- #1025: `pytest tests/test_gpu_detailed.py -q` passed, 23 tests.
- #1022: `pytest tests/test_extensions.py::TestCallAgentErrorNarrowing -q` passed, 3 tests.
- #1010: `pytest tests/test_settings_env.py -q` passed, 16 tests; `.env.schema.json` parses as JSON.
- #1014: `tests/test-doctor-extension-diagnostics.sh` passed, 9 checks.
- #1009: `docker compose config --quiet` passed for base, base+nvidia, base+amd, and base+DreamForge with `WEBUI_SECRET` set; config output shows `ENABLE_IMAGE_GENERATION=false` in base and `true` in AMD/NVIDIA overlays.
- #1003/#1015/#1019: dashboard `npm ci` and `npm run build` passed where run. #1019's Vitest suite failed: 5 failing tests across `SetupWizard.test.jsx` and `TemplatePicker.a11y.test.jsx`; backend sentinel pytest also failed in this Windows checkout because the generated test scripts use `/bin/bash`.
- #1020: shell syntax passed for changed scripts/tests; `test-gpu-apple.sh` could not run here because Git Bash lacks `jq`, and `tests/contracts/test-dream-doctor.sh` skipped because this is not macOS.
- #1002: Git Bash `bash -n` passed, but the same `set -euo pipefail` version-lookup failure reproduced in Batch 4 applies.

## Batch 6: CLI UX / Apple-GPU / CI-Deps / Docs Small

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1055 | approved | Useful contributor documentation for the dashboard-api bake-vs-bind-mount trap; no code risk. |
| #1000 | needs work | JSON modes are useful, but `dream list --json` can be polluted by `sr_load` warnings on stdout when PyYAML is missing, making the JSON invalid. |
| #999 | approved | Apple Silicon CLI/doctor branches are directionally correct; targeted Apple `gpu validate` fixture returns the intended 0/0 skip. |
| #998 | needs work | Draft pipefail/exit-code work repeats the `_check_version_compat` grep-pipeline abort fixed by #1008. |
| #997 | approved | `dream shell` now validates service IDs and Docker responsiveness before `docker exec`; unknown-service behavior is clearer and syntax passes. |
| #994 | needs work | Schema-driven masking works only when `jq` is available; without `jq`, newly schema-secret user/email fields still print in clear. |
| #993 | approved | Color/no-color and separator polish is low-risk; help output no longer contains literal `\033` when redirected. |
| #992 | approved | `.env.example` now includes `OPENCLAW_TOKEN` with the correct generator guidance. |
| #991 | approved | Pinned SHA resolves to `anthropics/claude-code-action` tag `v1.0.104`; workflow usage remains on the same major line. |
| #990 | approved | Pinned SHA resolves to `actions/github-script` tag `v9.0.0`; release notes were checked and current workflows do not use the broken `require('@actions/github')` pattern. |

Proof log:

- #1000/#999/#998/#997/#994/#993: Git Bash `bash -n` passed for changed shell files.
- #1000: `dream list --json` in a no-PyYAML environment emitted warning text on stdout before JSON; parsing failed.
- #999: temporary install fixture with `GPU_BACKEND=apple` returned the intended `gpu validate` message: single integrated GPU, `0 check(s) passed, 0 failed`.
- #994: `dream config show` with `.env.schema.json` present but no `jq` masked passwords but leaked `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL`; `test-validate-env.sh` could not complete here because Git Bash lacks `jq`.
- #997: unknown-service `dream shell definitely-not-a-service` returns an explicit unknown-service error before Docker exec.
- #993: redirected `dream-cli help` output checked clean for literal `\033` sequences.
- #990/#991: GitHub API tag dereference confirms the pinned SHAs match the advertised tags; `actions/github-script` v9 release notes were checked for breaking script-context changes.

## Batch 7: Docs / Support / CI Gates / Conflicting Older PRs

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #1053 | needs work | The OpenClaw CI gate catches unexpected write paths, but its positive assertion only warns when the expected `openclaw.json` write never happens; a crash-before-write can still false-green. |
| #1052 | keep draft | Useful structural guard for the Langfuse hook, but the PR branch fails its own tests until it is stacked on or retargeted to the hook implementation. |
| #1042 | needs work | Support bundle feature is useful and mostly works, but `--json` emits Windows paths under Git Bash that the PR's own Bash test cannot feed back to `tar`. |
| #1017 | keep draft | Security-doc update is the right follow-up to #988, but the branch carries the #988 code/docs stack; keep draft until #988 lands and this is rebased to the docs-only delta. |
| #973 | needs work | Good broad documentation pass, but it will be stale against the safer host-agent bind fallback from #988/#1017; rebase/update before merging after the security fix. |
| #966 | close/supersede | Current diff from the merge base is empty; the platform-doc content has effectively been absorbed or reverted in later work, so keeping the PR open adds queue noise. |
| #959 | approved | Narrow Token Spy product-doc clarification; correctly distinguishes incubator/prototype docs from the shipped extension behavior. |
| #716 | needs work | The validation env-file approach is correct, but the PR also weakens real extension templates by replacing required secrets with known/empty defaults. |
| #364 | rebase/conflict | Large old runtime API feature is merge-dirty and also removes unrelated core/agents router test coverage; rebase and restore coverage before reconsidering. |
| #351 | rebase/conflict | Contains a literal conflict marker in `tests/test_routers.py`, so Python cannot parse the test module. |

Proof log:

- #1052: `pytest tests/test_hooks.py -q` failed 2/13 because Langfuse does not yet declare `service.setup_hook` and the hook file is absent on this branch.
- #1042: `bash -n` passed, and the support bundle command produced a redacted archive with Docker disabled; `tests/test-support-bundle.sh` failed when `tar -tzf` consumed the Windows-style `archive` path emitted by `--json`.
- #716: `bash -n resources/dev/extensions-library/validate-compose.sh` passed; diff review shows the validator now generates placeholders for `${VAR:?}` values, so weakening the production compose secrets is unnecessary.
- #351: `python -m py_compile tests/test_routers.py` failed with a syntax error at the conflict marker.
- #364: `python -m py_compile routers/runtime.py tests/test_routers.py` passed on the branch content, but GitHub merge state is dirty and the diff replaces unrelated tests.
- #973/#1017/#966/#959: `git diff --check` passed where applicable; #966 has no current three-dot diff, while #973/#1017 overlap with the host-agent bind/security-doc queue.

## Batch 8: Large Feature PRs / Broad Blast Radius

Status: complete.

| PR | Verdict | Notes |
|---:|---|---|
| #983 | needs work | The p2p GPU toolkit is self-contained and shell syntax passes, but the advertised NVIDIA driver/library mismatch repair is not actually reachable because exit statuses are lost under `!` and `set -e`. Also has `git diff --check` whitespace failures. |
| #961 | needs work | Mobile preview dispatch and syntax are broadly coherent, but the Android localhost automation bridge lacks an origin/token gate on action POST endpoints; malicious local-browser pages can trigger automation requests. |
| #750 | approved | AMD multi-GPU support is large but internally consistent: assignment JSON includes AMD indices, compose validates with required env, Python GPU tests pass, and stale multigpu cache handling is present. Fixture whitespace should be cleaned if diff-check is enforced. |
| #1027 | approved | Correctly swaps community extension host bindings to `${BIND_ADDRESS:-127.0.0.1}` while preserving loopback defaults; regression sweep passes. |
| #1004 | approved | Narrow resolver fix avoids Apple Silicon local-overlay deadlocks without changing NVIDIA/AMD logic; shell syntax and diff-check pass. |

Proof log:

- #983: `bash -n` passed across `resources/p2p-gpu/**/*.sh`; `git diff --check` failed on trailing whitespace; code review found the mismatch-repair control-flow bug.
- #961: shell syntax passed for changed shell scripts, `android-local-server.py` passed `py_compile`, `tests/smoke/mobile-dispatch.sh` passed, and `git diff --check` passed. The BATS file needs the BATS harness and was not counted from a direct `bash` invocation.
- #750: shell syntax passed for changed installer/test scripts; `py_compile` passed for `assign_gpus.py` and `gpu.py`; `pytest extensions/services/dashboard-api/tests/test_gpu_amd.py -q` passed, 16 tests; AMD multi-GPU compose config passed with required secrets set. `tests/test-amd-topo.sh` could not run here because Git Bash lacks `jq`; `git diff --check` reports trailing whitespace in raw ROCm fixture tables.
- #1027: `bash tests/test-bind-address-sweep.sh` passed and `git diff --check` passed.
- #1004: `bash -n scripts/resolve-compose-stack.sh` and `git diff --check` passed; direct resolver counting was limited in this environment by the script's PyYAML dependency, but the one-line guard is in the correct extension overlay path.


---

# Approved PR Re-Audit Ledger

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

