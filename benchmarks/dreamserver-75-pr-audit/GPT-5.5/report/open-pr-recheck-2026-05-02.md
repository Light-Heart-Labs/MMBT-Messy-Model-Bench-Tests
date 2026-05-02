# Rolling PR Audit - 2026-05-02

Live open PR count at start: 75.

## Batch 1: #351, #364, #716, #750, #961

### #351 - test: add comprehensive input validation and injection resistance tests

- Verdict: **Reject until rebased/resolved**.
- Value: Good target area. More security regression coverage would help DreamServer.
- Cleanliness: Not clean. Current branch contains a literal conflict marker in `dream-server/extensions/services/dashboard-api/tests/test_routers.py`.
- Safety: Not mergeable. Test module is unparsable.
- Proof: `python -m py_compile dream-server/extensions/services/dashboard-api/tests/test_routers.py` fails with `SyntaxError: invalid decimal literal` at the `>>>>>>> 8a44877...` marker.
- Guidance: Rebase onto current `main`, remove conflict marker, then re-evaluate the actual tests. Consider whether production validation changes belong in this test-only PR.

### #364 - feat(dashboard-api): add settings, voice runtime, and diagnostics APIs

- Verdict: **Revise / rebase**.
- Value: Potentially valuable. Settings, voice status, LiveKit token, and `/api/test/*` diagnostics are real dashboard/runtime gaps.
- Cleanliness: Not clean. GitHub reports `DIRTY`. The branch also deletes a large block of existing router tests while adding runtime tests.
- Safety: Not safe to merge as-is. New runtime router syntax compiles, but replacing existing coverage with unrelated tests is a regression risk.
- Proof: `python -m py_compile routers/runtime.py main.py` passes on the PR worktree; diff shows deletion of existing API/agents tests from `tests/test_routers.py`.
- Guidance: Rebase onto current `main`, keep existing tests, move new runtime tests into a dedicated file, and narrow broad exception handling in `_check_livekit`.

### #716 - fix(extensions-library): add sensible defaults for required env vars

- Verdict: **Revise**.
- Value: The validator fix is valuable. Supplying a generated `--env-file` for `docker compose config` is the right shape.
- Cleanliness: Partially cleaned up since the old audit. Most insecure defaults were reverted, but not all.
- Safety: Not safe as-is. `FRIGATE_RTSP_PASSWORD` still defaults to `frigate`, and `OPEN_INTERPRETER_API_KEY` defaults to empty in the real runtime compose files.
- Proof: `resources/dev/extensions-library/validate-compose.sh` passes 46/46 locally with the placeholder env file; combined diff still changes Frigate and Open Interpreter runtime secrets.
- Guidance: Keep the validation env-file change. Revert runtime secret weakening unless the service is explicitly documented as safe without that value.

### #750 - feat: AMD Multi-GPU Support

- Verdict: **Revise / maintainer hardware signoff**.
- Value: High. This is strategically important for AMD partnership and multi-GPU DreamServer installs.
- Cleanliness: Not clean. GitHub reports `DIRTY` and `CHANGES_REQUESTED`.
- Safety: Not merge-ready. The earlier `--gpu-count` overlay-drop finding appears addressed across resolver call sites, host agent, CLI, update, preflight, and installer refresh paths. But the PR is broad enough that it needs a clean rebase and actual AMD multi-GPU validation before merge.
- Proof: Python compile passes for `gpu.py` and `assign_gpus.py`; Bash syntax checks pass for AMD topology/resolver/installer scripts. `tests/test-amd-topo.sh` could not run locally because `jq` is unavailable in this Windows/Git-Bash environment.
- Guidance: Rebase, run on real AMD multi-GPU hardware, and verify installer, resolver, dashboard GPU API, and compose stack behavior end-to-end.

### #961 - feat: add mobile paths for Android Termux and iOS a-Shell

- Verdict: **Merge after rebase/checks if maintainer wants the placeholder contract**.
- Value: Modest but real. The current PR is no longer the risky local mobile automation server; it is platform detection plus a stub mobile installer that fails clearly.
- Cleanliness: Much improved from prior audit. GitHub still reports `BLOCKED` / `CHANGES_REQUESTED`, but the current diff is small and focused.
- Safety: Safe enough if the team accepts routing mobile platforms to an explicit "follow-up PR" failure.
- Proof: `bash -n` passes for touched shell scripts; `tests/smoke/mobile-dispatch.sh` passes under Git Bash.
- Guidance: Update the PR title/body to match current scope: "mobile platform dispatch contract", not full mobile install support.

## Batch 2: #973, #974, #983, #994, #998

### #973 - docs: sync documentation with codebase after 50+ merged PRs

- Verdict: **Revise**.
- Value: Useful if kept current; broad documentation sync is needed.
- Cleanliness: Not clean enough. GitHub reports `BLOCKED`. The diff still mixes many topics, and docs disagree with each other.
- Safety: Low runtime risk but high documentation trust risk.
- Proof: `SECURITY.md` now describes Linux host-agent binding as Docker-bridge autodetect with `127.0.0.1` fallback, while `docs/HOST-AGENT-API.md` still says the agent "binds to 127.0.0.1 only." That is internally inconsistent for Linux.
- Guidance: Split or rebase after the host-agent/systemd/bind-address PRs settle, then do one final docs pass against current code.

### #974 - fix(bootstrap): use $DOCKER_CMD for DreamForge restart

- Verdict: **Merge after rebase / CI**.
- Value: Real. It fixes bootstrap paths that still used bare `docker` despite the installer already detecting `DOCKER_CMD`.
- Cleanliness: GitHub reports `DIRTY` and previous changes requested, but the current diff directly addresses the known compose-command guard issue.
- Safety: Low. Changes are in a bootstrap-upgrade recovery path and include a focused guard test.
- Proof: `tests/test-bootstrap-openclaw-compose-guard.sh` passes locally: 6/6.
- Guidance: Rebase to clear `DIRTY`, then merge if CI matches the local focused test.

### #983 - feat(resources): add p2p-gpu deploy toolkit for Vast.ai GPU instances

- Verdict: **Revise / maintainer judgment**.
- Value: Potentially high for rented GPU deployments and Vast.ai-style installs.
- Cleanliness: Better than the prior audit on the NVML mismatch issue. Still broad: 34 files, new toolkit, CI, phases, subcommands, and GPU repair logic.
- Safety: Not routine-merge safe. This is a separate deploy surface with NVIDIA/AMD/CPU behavior, root/system package operations, networking, and public access implications.
- Proof: `resources/p2p-gpu/tests/test-nvml-mismatch.sh` exits 0 locally. The previous unreachable `if ! detect_nvml_mismatch; then mismatch_status=$?` pattern has been replaced with an `if detect...; else mismatch_status=$?` shape. No live GPU/Vast.ai test was run here.
- Guidance: Keep in a hardware/provider validation lane. Require one real Vast.ai/NVIDIA pass and one no-GPU/CPU dry-run before merge.

### #994 - fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation

- Verdict: **Revise small / rebase**.
- Value: High. Schema-driven secret masking and Bash 4 validation fix real CLI safety gaps.
- Cleanliness: GitHub reports `DIRTY`. The original no-`jq` secret leak is fixed in normal execution, but the branch's own new test is brittle under Git Bash.
- Safety: Mostly safe after rebase, but do not merge with a failing regression test.
- Proof: Normal manual run of `dream config show` masks `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL` correctly. However `tests/test-dream-config-secret-mask.sh` fails locally under Git Bash because its controlled PATH/symlink harness breaks CLI bootstrap (`lib/service-registry.sh` path resolution) and emits symlink errors.
- Guidance: Rebase, fix the test harness portability, then merge. The implementation direction is sound.

### #998 - fix(dream-cli): pipefail + surface LLM failures + exit-code contract

- Verdict: **Merge after rebase / CI**.
- Value: Real. `pipefail` plus explicit LLM failure surfacing improves CLI correctness.
- Cleanliness: GitHub reports `DIRTY`, but the old DREAM_VERSION fallback blocker is addressed.
- Safety: Moderate because this touches `dream-cli` strict mode; tests are important.
- Proof: `tests/test-dream-cli-version-compat-pipefail.sh` passes locally: 4/4. Diff adds `|| true` to the `DREAM_VERSION` grep pipeline and other fragile grep/jq sites.
- Guidance: Rebase, run the broader CLI smoke/BATS suite, then merge before dependent strict-mode PRs (#1002/#1011/#1018).

## Batch 3: #1000, #1002, #1011, #1017, #1018

### #1000 - feat(dream-cli): --json flag on list/status and document doctor --json

- Verdict: **Merge after rebase / CI**.
- Value: Real. `dream list --json` and `dream status --json` improve automation support and make the CLI easier to script.
- Cleanliness: GitHub reports `DIRTY`, but the current implementation is focused.
- Safety: Moderate. Machine-readable stdout must stay clean even when registry diagnostics fire.
- Proof: The PR's focused test skipped because PyYAML is unavailable in this Git-Bash environment. I manually ran `dream-cli list --json` in an environment where registry loading warns about missing PyYAML; stdout was exactly `[]`, stderr contained the PyYAML warnings, and exit code was 0. That fixes the prior JSON-pollution finding.
- Guidance: Rebase and run the focused test in CI with PyYAML available so it exercises the broken-manifest path instead of skipping.

### #1002 - refactor(dream-cli): enable set -u and add guards for conditional variables

- Verdict: **Do not merge; keep draft until rebased behind #998**.
- Value: Good direction. Nounset hardening is worthwhile, but only after the pipefail fixes land.
- Cleanliness: Draft and `DIRTY`.
- Safety: Not safe as-is. The current branch still has a bare `grep '^DREAM_VERSION=' ... | sed -n '1p' | ...` assignment under `set -euo pipefail`, so a missing `DREAM_VERSION` can abort before fallback.
- Proof: `bash -n dream-server/dream-cli` passes, but the combined diff lacks the `|| true` guard that #998 adds.
- Guidance: Merge/rebase #998 first, then re-run nounset smoke tests under minimal env before considering this PR.

### #1011 - chore(bash32): guard declare -A callers + route dream-cli validate through $BASH

- Verdict: **Revise / keep draft until dependency stack settles**.
- Value: Real for macOS users. Explicit Bash 4+ errors and routing validation scripts through `$BASH` are the right compatibility model.
- Cleanliness: Draft and `BLOCKED`. It overlaps the #994/#998/#1002 strict-mode and validation stack.
- Safety: Low once rebased, but it should not land while its dependencies are unstable.
- Proof: `bash -n` passes for `dream-cli`, `installers/phases/03-features.sh`, `lib/progress.sh`, `scripts/dream-test-functional.sh`, `scripts/pre-download.sh`, and `scripts/validate-env.sh`.
- Guidance: Rebase after #994 and #998; keep it as a narrow Bash 3.2 compatibility PR rather than bundling broader CLI changes.

### #1017 - docs(security): Linux host-agent fallback is 127.0.0.1 post-#988

- Verdict: **Revise / consolidate with #973**.
- Value: Useful security documentation once the host-agent binding behavior is settled.
- Cleanliness: Draft and `BLOCKED`. It substantially overlaps #973.
- Safety: Low runtime risk, but high documentation-trust risk.
- Proof: The diff adds the Docker-bridge/127.0.0.1 fallback explanation in `SECURITY.md`, but `docs/HOST-AGENT-API.md` still says the agent binds to `127.0.0.1` only. That is the same internal inconsistency found in #973.
- Guidance: Fold the corrected language into one docs PR after the host-agent binding/systemd changes settle.

### #1018 - test(dream-cli): BATS regression shield for 5 dream-cli / supporting behaviors

- Verdict: **Revise / keep draft until stacked dependencies merge**.
- Value: High as a regression shield. The BATS coverage captures several fragile CLI behaviors.
- Cleanliness: Draft and `DIRTY`. The PR is stacked and includes implementation changes from its dependencies, not just tests.
- Safety: Not merge-ready independently, but the tests themselves are valuable.
- Proof: Direct BATS run of the five new test files passed 53/53 using the PR's vendored BATS install. Some schema/registry cases skipped because this environment lacks `jq` and PyYAML. A first attempt through `tests/run-bats.sh` timed out because that wrapper always runs the whole existing BATS suite before appended paths.
- Guidance: After #994/#998/#1002/#1011 settle, rebase this so the diff is test-only and run the full BATS suite in a Linux CI environment with `jq` and PyYAML installed.

## Batch 4: #1024, #1039, #1040, #1051, #1052

### #1024 - fix(scripts): NUL-delimited compose-flags contract for path-with-spaces safety

- Verdict: **Revise**.
- Value: Good. Moving compose flag transport away from whitespace-split strings is the right fix class.
- Cleanliness: GitHub reports `DIRTY`.
- Safety: Not merge-ready because the PR's own regression is not green in this Windows/Git-Bash audit environment.
- Proof: `bash -n` passes for the touched scripts, but `tests/test-resolve-compose-null.sh` fails 8/9. The new `space ext` fixture expected `extensions/services/space ext/compose.yaml`, but the resolver emitted `extensions\services\space ext\compose.yaml`, so the path-with-spaces proof is still platform-sensitive.
- Guidance: Normalize emitted compose paths to POSIX-style forward slashes or make the contract explicitly platform-aware and covered on Windows/Git-Bash plus Linux.

### #1039 - fix(host-agent): retry install failure + DRY post_install hook executor

- Verdict: **Revise / rebase**.
- Value: Real. Retrying a failed install through the same `post_install` hook path is better than blindly starting a half-configured container.
- Cleanliness: GitHub reports `BLOCKED`. The diff is larger than the title suggests because it includes host-agent startup/pull behavior adjacent to other open PRs.
- Safety: Promising but not merge-ready without the host-agent test suite.
- Proof: `python -m py_compile` passes for `dream-host-agent.py`, `routers/extensions.py`, and `tests/test_host_agent.py`. I could not run the pytest tests because this Python environment does not have `pytest` installed.
- Guidance: Rebase after the narrower host-agent PRs settle (#1057/#1110/#1111 overlap this area), run `tests/test_host_agent.py`, and keep the post-install hook refactor separate from unrelated pull/start behavior if possible.

### #1040 - fix(langfuse): chown postgres/clickhouse data dirs to image uids on Linux

- Verdict: **Revise**.
- Value: High. Fixing Langfuse bind-mount ownership on native Linux is operationally important.
- Cleanliness: GitHub reports `BLOCKED`.
- Safety: Needs one small hardening fix before merge. The hook uses plain `sudo` for `mkdir`/`chown`; from the host-agent/systemd context this can fail opaquely or block until the hook timeout instead of failing immediately.
- Proof: `bash -n` passes for the hook and reproducer. The reproducer could not complete locally because Docker Desktop's Linux engine is not running. Static review shows `SUDO="sudo"` and `$SUDO chown -R ...` without `sudo -n` or an early non-interactive capability check.
- Guidance: Use `sudo -n` or preflight the privilege path before mutation, then run the reproducer on a native Linux Docker host.

### #1051 - fix(resolver): hoist yaml import, guard empty manifests, align user-ext loop

- Verdict: **Revise**.
- Value: Good target area. The resolver needs to keep legacy manifestless extensions while honoring manifest filters.
- Cleanliness: GitHub reports `BLOCKED`.
- Safety: Not safe as-is. The user-extension loop still includes an AMD-only YAML-manifest extension on an NVIDIA stack when PyYAML is unavailable.
- Proof: `bash -n resolve-compose-stack.sh` passes. A synthetic user extension with `manifest.json` and `gpu_backends: ["amd"]` is correctly excluded from `--gpu-backend nvidia`, but the same fixture as `manifest.yaml` is included because the PR sets `manifest = None` when PyYAML is missing and intentionally bypasses the filter.
- Guidance: Match the built-in loop behavior: if a YAML manifest exists but PyYAML is unavailable, skip or fail closed instead of falling back to unfiltered defaults.

### #1052 - test(langfuse): structural guard for setup_hook + hook file coexistence

- Verdict: **Do not merge; keep draft until #1040 or equivalent implementation lands**.
- Value: Good as a regression guard, but only when stacked on the Langfuse hook implementation.
- Cleanliness: Draft and `BLOCKED`.
- Safety: Merge would redline tests because it asserts files and manifest fields that are absent on this branch.
- Proof: `python -m py_compile test_hooks.py` passes. Static check shows `dream-server/extensions/services/langfuse/hooks/post_install.sh` is missing and the manifest has no `service.setup_hook`, while the new tests assert both exist.
- Guidance: Rebase this onto the implementation PR or fold the tests into #1040.

## Batch 5: #1053, #1057, #1059, #1065, #1066

### #1053 - ci(openclaw): filesystem-write gate to detect new openclaw write paths

- Verdict: **Merge after rebase / CI**.
- Value: Real. A CI write-path gate is exactly the right place to catch OpenClaw persistence drift.
- Cleanliness: GitHub reports `BLOCKED`, but the current diff is single-purpose.
- Safety: Low runtime risk; CI-only.
- Proof: Static workflow check shows the previous false-green gap is fixed: missing `openclaw.json` now emits `::error::` and exits 1, and unexpected files also exit 1.
- Guidance: Rebase and let Actions prove the workflow can pull/start the test image on GitHub-hosted runners.

### #1057 - fix(host-agent): runtime hygiene - narrow pull, surface failures, normalize bind volumes

- Verdict: **Merge after rebase / host-agent tests**.
- Value: High. It reduces unrelated extension pull failures, surfaces failed starts, and handles long-form bind mounts.
- Cleanliness: GitHub reports `DIRTY`, but this is now a focused host-agent runtime fix.
- Safety: Moderate. Host-agent install/start behavior is high-impact, but the earlier dependency-pruning concern is addressed.
- Proof: `python -m py_compile` passes for `dream-host-agent.py` and `tests/test_host_agent.py`. Static review confirms narrowed pull now validates with `docker compose ... config --services` and falls back to the full flag set if dependencies are missing.
- Guidance: Rebase, run `tests/test_host_agent.py`, and merge before broader host-agent PRs that depend on this behavior.

### #1059 - refactor(dashboard-api): extract pure settings helpers into settings.py

- Verdict: **Merge after rebase / API tests**.
- Value: Moderate. Pulling settings helpers out of `main.py` reduces the dashboard API monolith and makes later testing easier.
- Cleanliness: GitHub reports `BLOCKED`, but the diff is a refactor-only shape.
- Safety: Moderate because settings/env apply is user-facing and sensitive.
- Proof: `python -m py_compile main.py settings.py` passes. A direct import of `settings.py` could not run in this audit environment because `fastapi` is not installed, so behavior still needs the normal dashboard-api test environment.
- Guidance: Rebase and run the existing settings/API tests. Consider dropping the "pure" wording unless the module stops importing `fastapi.HTTPException` and config globals.

### #1065 - fix(dreamforge): pin platform to linux/amd64

- Verdict: **Merge after rebase / compose CI**.
- Value: Real for Apple Silicon and any host where Docker might otherwise choose an unsupported architecture.
- Cleanliness: GitHub reports `BLOCKED`, but the diff is one line.
- Safety: Low. The image is documented as amd64-only; pinning makes the contract explicit.
- Proof: `docker compose -f dream-server/extensions/services/dreamforge/compose.yaml config --quiet` passes locally without needing the Docker daemon.
- Guidance: Merge once rebased.

### #1066 - fix(chromadb): switch healthcheck from bash /dev/tcp to python3 urllib

- Verdict: **Merge after rebase / compose CI**.
- Value: Real. The Chroma image is a Python service, so a Python urllib healthcheck is more portable than relying on Bash `/dev/tcp`.
- Cleanliness: GitHub reports `BLOCKED`, but the diff is one line.
- Safety: Low.
- Proof: `docker compose -f resources/dev/extensions-library/services/chromadb/compose.yaml config --quiet` passes locally without needing the Docker daemon.
- Guidance: Merge once rebased, ideally with one container-level smoke check confirming `python3` exists in the selected Chroma image.

## Batch 6: #1067, #1068, #1069, #1070, #1071

### #1067 - fix(compose): drop CPU overlay AUDIO_STT_MODEL literal; make AMD memory limit env-driven

- Verdict: **Merge after rebase / compose CI**.
- Value: Real, and AMD-relevant. Making the AMD memory limit env-driven reduces hard-coded ROCm behavior.
- Cleanliness: GitHub reports `BLOCKED`, but the diff is only compose overlays.
- Safety: Low if compose validation stays green.
- Proof: With required secrets supplied as environment placeholders, `docker compose -f docker-compose.base.yml -f docker-compose.cpu.yml config --quiet` and the same command with `docker-compose.amd.yml` both pass.
- Guidance: Merge once rebased. This is a good early AMD-path cleanup.

### #1068 - fix(compose): drop unconditional depends_on: searxng from perplexica and openclaw

- Verdict: **Merge after rebase / compose CI**.
- Value: Real. Optional extensions should not force SearXNG into otherwise unrelated compose operations.
- Cleanliness: GitHub reports `BLOCKED`; the diff is narrow.
- Safety: Low. It removes a hard dependency that was too broad.
- Proof: With the base compose and required env placeholders supplied, both OpenClaw and Perplexica compose fragments parse with `docker compose config --quiet`.
- Guidance: Merge once rebased. This supports the same dependency hygiene goal as #1057.

### #1069 - fix(privacy-shield): authenticate /stats, minimize /health response, share SHIELD_API_KEY across services

- Verdict: **Revise small / then merge**.
- Value: High. This fixes a real privacy/security issue: `/stats` should not be unauthenticated, and unauthenticated `/health` should stay minimal.
- Cleanliness: GitHub reports `BLOCKED`; diff spans runtime, API, tests, and three installer env generators.
- Safety: Mostly good, but existing installs without `SHIELD_API_KEY` need an explicit upgrade/migration story.
- Proof: `python -m py_compile` passes for the dashboard privacy router, privacy-shield proxy, and new tests. Static review confirms `/stats` now depends on API-key auth and dashboard stats forwards `Authorization: Bearer $SHIELD_API_KEY`.
- Guidance: Add or document an update-path upsert for existing `.env` files. New installers generate the key, but an existing install that does not rerun env generation will get clear stats errors and may still have unusable privacy-shield proxy auth.

### #1070 - fix(windows-amd): add readiness sidecar gating open-webui on native inference

- Verdict: **Merge after Windows AMD smoke test**.
- Value: High and AMD-relevant. Gating Open WebUI on Lemonade or native `llama-server.exe` readiness addresses a real Windows AMD race.
- Cleanliness: GitHub reports `BLOCKED`; diff is two Windows installer files.
- Safety: Moderate because it affects Windows AMD startup ordering.
- Proof: `docker compose -f docker-compose.base.yml -f installers/windows/docker-compose.windows-amd.local.yml config --quiet` passes with required env placeholders. The installer only adds the local readiness overlay for non-cloud AMD, avoiding the obvious cloud-mode deadlock.
- Guidance: Run one Windows AMD install smoke with Lemonade/native inference before merge.

### #1071 - fix(installer): NVIDIA Container Toolkit keyring fail-loud + apt-only

- Verdict: **Merge after Linux NVIDIA installer smoke**.
- Value: Real. Failing loudly on an empty NVIDIA keyring is safer than continuing with a broken apt repo.
- Cleanliness: GitHub reports `BLOCKED`; one installer file.
- Safety: Low-to-moderate because it touches package installation on NVIDIA Linux hosts.
- Proof: `bash -n installers/phases/05-docker.sh` passes. Static review confirms the apt keyring download is no longer hidden behind `|| true` and errors if the keyring file is empty/missing.
- Guidance: Validate on one apt-based NVIDIA host. The non-apt branches still exist, so the title should avoid implying this removes dnf/pacman support.

## Batch 7: #1072, #1073, #1074, #1075, #1076

### #1072 - fix(installer): pre-create token-spy data dir + macOS extension parity

- Verdict: **Merge after rebase / installer smoke**.
- Value: Real. Pre-creating `data/token-spy` matches the container UID contract and avoids avoidable first-start crashes.
- Cleanliness: GitHub reports `BLOCKED`; two installer files.
- Safety: Low.
- Proof: `bash -n installers/phases/06-directories.sh installers/macos/install-macos.sh` passes.
- Guidance: Merge once rebased. On non-uid-1000 Linux installs, the non-fatal `chown` warning is acceptable but should be visible in installer logs.

### #1073 - fix(nvidia-overlay): allow .env override of AUDIO_STT_MODEL default

- Verdict: **Merge after rebase / compose CI**.
- Value: Real. NVIDIA should keep the strong default while still respecting a user's `.env` override.
- Cleanliness: GitHub reports `BLOCKED`; one compose file.
- Safety: Low.
- Proof: With required secrets supplied as placeholders, `docker compose -f docker-compose.base.yml -f docker-compose.nvidia.yml config --quiet` passes.
- Guidance: Merge once rebased.

### #1074 - fix: use 127.0.0.1 in installer + CLI healthcheck network calls

- Verdict: **Merge after rebase / smoke**.
- Value: Real. Avoiding `localhost` removes IPv6/IPv4 ambiguity in local health checks.
- Cleanliness: GitHub reports `BLOCKED`; broad but mechanical across CLI/install scripts.
- Safety: Low-to-moderate because it touches many healthcheck surfaces.
- Proof: `bash -n` passes for all 10 touched shell scripts.
- Guidance: Merge after one local healthcheck smoke on Linux or macOS.

### #1075 - fix(host-agent): surface docker-bridge detection failure cause

- Verdict: **Merge after rebase**.
- Value: Good. More actionable host-agent logs help diagnose Linux container-to-host reachability.
- Cleanliness: GitHub reports `BLOCKED`; one Python file.
- Safety: Low.
- Proof: `python -m py_compile bin/dream-host-agent.py` passes.
- Guidance: Merge once rebased.

### #1076 - fix(preflight): warn when UFW or firewalld is active on Linux

- Verdict: **Merge after rebase**.
- Value: Real. Active host firewalls are a common cause of container-to-host agent failures.
- Cleanliness: GitHub reports `BLOCKED`; two preflight scripts.
- Safety: Low. This warns only; it does not mutate firewall rules.
- Proof: `bash -n installers/phases/01-preflight.sh scripts/linux-install-preflight.sh` passes.
- Guidance: Merge once rebased. Longer-term, make the suggested port derive from `${DREAM_AGENT_PORT:-7710}`.

## Batch 8: #1077, #1078, #1079, #1080, #1081

### #1077 - fix(forge): disable bundled syncthing public-relay on default install

- Verdict: **Merge after rebase / compose CI**.
- Value: Real. Disabling a bundled public-relay sync service by default is a safer default posture.
- Cleanliness: GitHub reports `BLOCKED`; one compose file.
- Safety: Low.
- Proof: `docker compose -f resources/dev/extensions-library/services/forge/compose.yaml config --quiet` passes locally.
- Guidance: Merge once rebased.

### #1078 - fix(scripts): BSD-compat for memory-shepherd, llm-cold-storage, migrate-config

- Verdict: **Merge after rebase / BATS CI**.
- Value: Real for macOS. Removing GNU-only assumptions improves local maintenance scripts.
- Cleanliness: GitHub reports `BLOCKED`; three scripts plus one BATS file.
- Safety: Low.
- Proof: `bash -n` passes for the touched scripts and the new BATS file. I did not run the BATS file because this worktree has not installed `tests/bats`.
- Guidance: Run the new BATS test in CI or through `tests/run-bats.sh`, then merge.

### #1079 - fix(installer): clean orphans on up; use opencode serve (headless) on macOS

- Verdict: **Merge after rebase / installer smoke**.
- Value: Real. `opencode serve` is the right headless launch command, and orphan cleanup helps stale compose services disappear after config changes.
- Cleanliness: GitHub reports `BLOCKED`; two installer files.
- Safety: Moderate because `--remove-orphans` affects compose project state.
- Proof: `bash -n installers/macos/install-macos.sh installers/phases/11-services.sh` passes.
- Guidance: Merge after one install/update smoke confirming expected extension containers are still present in the resolved compose project.

### #1080 - fix(openclaw): drop dangerouslyAllowHostHeaderOriginFallback flag

- Verdict: **Merge after rebase / jq-backed test CI**.
- Value: High. Removing a dangerous host-header fallback from both static configs and persisted config migration is a worthwhile hardening fix.
- Cleanliness: GitHub reports `BLOCKED`; focused OpenClaw config/test diff.
- Safety: Low-to-moderate, because it changes OpenClaw runtime config but toward safer behavior.
- Proof: `node --check config/openclaw/inject-token.js` and `bash -n tests/test-openclaw-inject-token.sh` pass. The full test skipped locally because `jq` is unavailable.
- Guidance: Run `tests/test-openclaw-inject-token.sh` in CI with `jq`, then merge.

### #1081 - fix(litellm-amd): re-enable master-key auth + rotate sk-lemonade

- Verdict: **Revise**.
- Value: High and AMD-relevant. Re-enabling LiteLLM auth on AMD/Lemonade is important, and rotating the hard-coded Lemonade key is the right intent.
- Cleanliness: GitHub reports `BLOCKED`; 14 files across compose, env generation, host-agent, bootstrap, and tests.
- Safety: Not safe as-is. The host-agent still writes `sk-lemonade` when regenerating `config/litellm/lemonade.yaml` because it reads `os.environ.get("LITELLM_LEMONADE_API_KEY")` rather than the install `.env` file.
- Proof: `test-litellm-amd-auth-enforced.sh` passes 4/4 and Python compile passes, but a direct reproduction calling `_write_lemonade_config()` with `.env` containing `LITELLM_LEMONADE_API_KEY=sk-custom-from-envfile` still emitted `api_key: sk-lemonade`.
- Guidance: Read `LITELLM_LEMONADE_API_KEY` from the install env in both `_do_model_activate` and `_write_lemonade_config`; strengthen the test to assert the configured rotated key is actually emitted.

## Batch 9: #1082, #1083, #1085, #1086, #1087

### #1082 - harden(resolver): boundary-check compose_file against extension dir

- Verdict: **Merge after rebase / resolver CI**.
- Value: High. Preventing manifest `compose_file` traversal is the right security hardening.
- Cleanliness: GitHub reports `BLOCKED`; one script plus a focused regression test.
- Safety: Low once tests pass.
- Proof: After installing PyYAML in the audit environment, `tests/test-resolve-compose-resilient.sh` passes 13/13. Before PyYAML was available, YAML-manifest cases failed/skipped, so CI must keep PyYAML installed for this proof to remain meaningful.
- Guidance: Merge once rebased. Consider applying the same boundary check to user-extension manifest paths if a later PR has not already done it.

### #1083 - feat(preflight): warn when INSTALL_DIR is on networked filesystem

- Verdict: **Revise**.
- Value: Useful. Networked install directories are a real source of subtle permission and performance problems.
- Cleanliness: GitHub reports `BLOCKED`; multi-platform preflight change.
- Safety: Not merge-ready because the Windows preflight script is unparsable.
- Proof: Bash syntax passes for the Linux/macOS scripts. `powershell -ExecutionPolicy Bypass -File installers/windows/phases/01-preflight.ps1 -DryRun` fails with `The string is missing the terminator: '`. The new warning string contains mojibake for an em dash inside double quotes; PowerShell treats the embedded smart quote as a string delimiter, so `share's` starts an unclosed single-quoted string.
- Guidance: Replace the mojibake/em dash in the Windows warning with plain ASCII punctuation and add a PowerShell parse check to the PR.

### #1085 - a11y(dashboard): add aria-hidden to TemplatePicker HardDrive icon

- Verdict: **Merge after rebase / frontend test CI**.
- Value: Small but real. It fixes the exact accessibility gap found earlier in TemplatePicker.
- Cleanliness: GitHub reports `BLOCKED`; one JSX line.
- Safety: Very low.
- Proof: Static review confirms `<HardDrive size={10} aria-hidden="true" />`. I could not run Vitest locally because dashboard dependencies are not installed (`vitest` not found).
- Guidance: Merge once rebased and frontend CI is green.

### #1086 - fix(dashboard-api): wrap get_user_services_cached in asyncio.to_thread

- Verdict: **Merge after rebase / API tests**.
- Value: Real. Moving filesystem-heavy user-extension catalog reads off the event loop is the right async API hygiene.
- Cleanliness: GitHub reports `BLOCKED`; one router file.
- Safety: Low.
- Proof: `python -m py_compile routers/extensions.py` passes, and the diff changes both catalog/detail call sites to `await asyncio.to_thread(...)`.
- Guidance: Merge once rebased and dashboard-api tests are green.

### #1087 - fix(dashboard-api): tighten exception handling in updates/workflows/privacy

- Verdict: **Merge after rebase / API tests**.
- Value: Real. Narrower timeout/client-error handling improves operator-visible failure modes.
- Cleanliness: GitHub reports `BLOCKED`; three router files.
- Safety: Low-to-moderate because this changes HTTP error mapping.
- Proof: `python -m py_compile routers/privacy.py routers/updates.py routers/workflows.py` passes.
- Guidance: Merge once rebased and route tests confirm expected 503/504/500 responses.

## Batch 10: #1088, #1089, #1090, #1091, #1092

### #1088 - fix(dashboard-api): preserve explicit empty values for commented-default env keys

- Verdict: **Revise**.
- Value: The target bug is real: explicit empty values should not be dropped by the Settings UI.
- Cleanliness: GitHub reports `BLOCKED`; one API file plus tests.
- Safety: Not safe as written. The commented-assignment branch now uncomments every commented key from `.env.example` as `KEY=` even when that key is absent from the submitted values.
- Proof: Static review of `_render_env_from_values()` shows `commented_assignment` unconditionally `seen.add(key)` and emits `f"{key}={values.get(key, '')}"`. The new test explicitly documents absent commented keys becoming active empty assignments. Pytest could not complete locally because dashboard-api dependencies such as FastAPI are not installed, though Python compile passes.
- Guidance: Only uncomment a commented default when the key is explicitly present in `values`; otherwise preserve the comment. Keep the explicit-empty regression test.

### #1089 - fix(installer): rebuild locally-built images on macOS, Windows, and via dream-cli

- Verdict: **Revise**.
- Value: High. Rebuilding locally built images is important for contributor/dev installs and source edits.
- Cleanliness: GitHub reports `BLOCKED`; three installer/CLI files.
- Safety: Not merge-ready because the Windows installer does not parse.
- Proof: Bash syntax passes for `dream-cli` and macOS installer. `powershell -ExecutionPolicy Bypass -File installers/windows/install-windows.ps1 -DryRun` fails with parse errors around the new build loop. The new warning string contains mojibake `â€”`, whose embedded smart quote terminates the PowerShell string.
- Guidance: Replace the mojibake/em dash in Windows strings with ASCII punctuation and add a PowerShell parse check.

### #1090 - fix(host-agent,dashboard): surface one-shot CLI extensions as installed

- Verdict: **Merge after rebase / API + frontend CI**.
- Value: Real. One-shot CLI extensions such as Aider should not look stuck or failed just because their container exits 0 after initialization.
- Cleanliness: GitHub reports `BLOCKED`; schema, API, frontend, and manifest changes.
- Safety: Moderate because it introduces a new status state (`cli_installed`) across API and UI.
- Proof: Python compile passes for the extension router and tests. I could not run frontend syntax/tests because JSX support/Vitest dependencies are not installed in this worktree.
- Guidance: Merge after dashboard-api and frontend tests confirm the new status is counted, displayed, and toggleable correctly.

### #1091 - installer: curl retries, longer llama-server healthcheck grace, phase-state markers

- Verdict: **Revise / split**.
- Value: Curl retries and longer llama-server healthcheck grace are valuable. Phase-state markers are a larger architectural change.
- Cleanliness: GitHub reports `BLOCKED`; seven files and mixed concerns.
- Safety: Not safe as-is. The new phase-state marker wraps Phase 07, but Phase 07 installs and restarts the host agent. Once marked complete, a later reinstall/update can skip copying/restarting the host agent, leaving stale daemon code.
- Proof: `bash -n` passes. Static review shows `phase_should_skip "$INSTALL_PHASE" && return 0` at the top of `07-devtools.sh` and `phase_mark_done "$INSTALL_PHASE"` at the end, while the same phase contains the host-agent service template copy and forced restart logic.
- Guidance: Split the curl/healthcheck changes from phase-state. Do not mark Phase 07 skippable unless host-agent binary/template freshness is fingerprinted or moved to a non-skipped phase.

### #1092 - fix(installer): add INTERACTIVE/sudo-n guard to Phase 01 jq install

- Verdict: **Merge after rebase**.
- Value: Real. Non-interactive installs should fail clearly instead of hanging on a sudo password prompt.
- Cleanliness: GitHub reports `BLOCKED`; one installer file.
- Safety: Low.
- Proof: `bash -n installers/phases/01-preflight.sh` passes.
- Guidance: Merge once rebased.

## Batch 11: #1093, #1094, #1095, #1096, #1097

### #1093 - fix(installer): add sudo guard and replace silent || true on Phase 07 Node install

- Verdict: **Merge after rebase**.
- Value: Real. Node install failures should be visible, especially in non-interactive runs.
- Cleanliness: GitHub reports `BLOCKED`; one installer phase.
- Safety: Low.
- Proof: `bash -n installers/phases/07-devtools.sh` passes.
- Guidance: Merge once rebased.

### #1094 - fix(installer): subshell-scope .env umask, mkdir+warn openclaw chown, repoint missing tier configs

- Verdict: **Merge after rebase / installer smoke**.
- Value: Real. Creating `.env` as 0600 from inception is good hardening, and repointing missing OpenClaw tier configs avoids broken profile copies.
- Cleanliness: GitHub reports `BLOCKED`; Linux and Windows installer phases plus tests.
- Safety: Moderate because this touches `.env` generation and OpenClaw config selection.
- Proof: Bash syntax passes for Linux phases and the BATS file. Windows phase scripts parse far enough to run but cannot complete standalone because they rely on parent installer functions/variables, which is expected for these phase files.
- Guidance: Merge after one Linux and one Windows installer smoke, especially with OpenClaw enabled.

### #1095 - fix(installer): correct bash precedence trap in Phase 11 .env bootstrap patch

- Verdict: **Merge after rebase**.
- Value: Real. The `.env` bootstrap-model patch should only report success when all write steps succeed.
- Cleanliness: GitHub reports `BLOCKED`; one installer phase.
- Safety: Low.
- Proof: `bash -n installers/phases/11-services.sh` passes; static review shows the awk/cat/rm pipeline is grouped under one explicit success/failure branch.
- Guidance: Merge once rebased.

### #1096 - fix(memory-shepherd): add -e to set flags so failed cp/mv/scp aborts visibly

- Verdict: **Merge after rebase / script smoke**.
- Value: Real. Memory reset/archive operations should fail visibly instead of continuing after failed file copies.
- Cleanliness: GitHub reports `BLOCKED`; one script.
- Safety: Low-to-moderate because `set -e` can expose latent unguarded failures.
- Proof: `bash -n memory-shepherd.sh` passes. Static scan shows expected non-critical find cleanup is still guarded with `|| true`.
- Guidance: Merge after a quick local reset/archive smoke.

### #1097 - fix(opencode): use opencode serve in opencode-web.service so headless installs don't trigger browser open

- Verdict: **Merge after rebase**.
- Value: Real. Systemd services should launch the headless server command, not a UI-opening default.
- Cleanliness: GitHub reports `BLOCKED`; one unit file.
- Safety: Low.
- Proof: Static review confirms `ExecStart=__HOME__/.opencode/bin/opencode serve --port 3003 --hostname 127.0.0.1`.
- Guidance: Merge once rebased.

## Batch 12: #1098, #1099, #1100, #1101, #1102

### #1098 - fix(scripts): use 127.0.0.1 instead of localhost in bootstrap-upgrade and repair-perplexica

- Verdict: **Merge after rebase**.
- Value: Real. Completes the localhost-to-IPv4 cleanup for two leftover scripts.
- Cleanliness: GitHub reports `BLOCKED`; two scripts.
- Safety: Low.
- Proof: `bash -n scripts/bootstrap-upgrade.sh scripts/repair/repair-perplexica.sh` passes.
- Guidance: Merge once rebased.

### #1099 - test(dashboard): cover Extensions.jsx unhealthy UI render path

- Verdict: **Merge after rebase / frontend CI**.
- Value: Good. It adds coverage for the unhealthy-extension UI path that has caused regressions.
- Cleanliness: GitHub reports `BLOCKED`; test-only.
- Safety: Very low.
- Proof: Could not run locally because dashboard dependencies are not installed (`vitest` not found). Static review shows the test mocks catalog/template fetches and targets unhealthy badge/toggle/logs behavior.
- Guidance: Merge once frontend CI passes.

### #1100 - refactor(dream-cli): unify logging helpers and section-banner style

- Verdict: **Merge after rebase / CLI smoke**.
- Value: Moderate. Keeping CLI diagnostics consistently on stderr helps machine-readable commands remain parseable.
- Cleanliness: GitHub reports `BLOCKED`; one CLI file.
- Safety: Low-to-moderate because CLI output contracts matter.
- Proof: `bash -n dream-cli` passes and `dream-cli --version` exits 0 with clean stdout and empty stderr.
- Guidance: Merge after running JSON-mode CLI smoke (`list --json`, `status --json`) in CI.

### #1101 - test(dashboard-api): cover unhealthy/warnings/retry/catalog regression gaps

- Verdict: **Keep draft / merge after dependencies settle**.
- Value: Good test coverage for known extension regressions.
- Cleanliness: Draft and `BLOCKED`; test-only but appears stacked on behavior from earlier host-agent/API PRs.
- Safety: Not merge-ready as a standalone PR.
- Proof: Python compile passes for the changed test files. I did not run pytest because dashboard-api runtime dependencies are still incomplete in this audit environment.
- Guidance: Rebase after #1039/#1057/#1090-style extension status changes settle, then run dashboard-api tests.

### #1102 - test: behavioral host-agent install poll + bats resolver/preflight + pre-commit shellcheck

- Verdict: **Keep draft / split or rebase after dependencies settle**.
- Value: High as a regression suite, especially for host-agent install polling and resolver user-extension behavior.
- Cleanliness: Draft and `BLOCKED`; mixed Python tests, BATS, pre-commit config, and a new AWK hook.
- Safety: Not merge-ready independently.
- Proof: Python compile passes for `test_host_agent.py`. I could not run BATS/pre-commit locally because BATS and AWK are not installed in this worktree/environment; plain `bash -n` is not reliable for `.bats` syntax.
- Guidance: Rebase after resolver/user-extension fixes land, then run the full BATS + pre-commit suite on Linux.

## Batch 13: #1104, #1105, #1106, #1107, #1108

### #1104 - fix(extensions): probe unmonitored user exts; surface recreate warnings; activate-path progress

- Verdict: **Keep draft / rebase after extension-status PRs settle**.
- Value: High. It addresses real dashboard UX gaps around unmonitored user extensions and silent post-install recreate failures.
- Cleanliness: Draft and `BLOCKED`; touches host-agent, API router, and tests.
- Safety: Not merge-ready independently because it stacks on earlier extension-progress/status work.
- Proof: Python compile passes for the changed host-agent/API/test files.
- Guidance: Rebase after #1057/#1090/#1101-style extension state changes settle, then run the dashboard-api test suite.

### #1105 - refactor(dashboard): consolidate failure-counter into createRecoveryTracker

- Verdict: **Merge after rebase / frontend CI**.
- Value: Moderate. It removes duplicated polling failure-counter logic and adds unit tests for the tracker.
- Cleanliness: GitHub reports `BLOCKED`; one UI file plus a small utility and tests.
- Safety: Low-to-moderate because polling recovery banners are user-visible.
- Proof: Static review of `createRecoveryTracker` and its tests is sound. Could not run Vitest locally because dashboard dependencies are not installed.
- Guidance: Merge once frontend CI passes.

### #1106 - fix(host-agent): elevate bridge-detection failure log to WARNING

- Verdict: **Merge after rebase**.
- Value: Small but useful. Bridge detection failure affects container-to-host reachability and deserves warning-level visibility.
- Cleanliness: GitHub reports `BLOCKED`; one Python line.
- Safety: Low.
- Proof: `python -m py_compile bin/dream-host-agent.py` passes.
- Guidance: Merge once rebased.

### #1107 - fix(token-spy): standalone product binds 127.0.0.1, auth on by default

- Verdict: **Revise**.
- Value: Good hardening intent. Localhost binding for proxy/dashboard/db ports is a clear improvement.
- Cleanliness: GitHub reports `BLOCKED`; standalone product compose/env example only.
- Safety: Not merge-ready because the auth default produces a broken dashboard unless the user sets a password.
- Proof: `docker compose -f resources/products/token-spy/docker-compose.yml config --quiet` passes with `POSTGRES_PASSWORD` set. Static review shows `DASHBOARD_AUTH_ENABLED=true` but `DASHBOARD_PASSWORD=` in `.env.example`; dashboard code raises HTTP 500 when auth is enabled and password is missing.
- Guidance: Make `DASHBOARD_PASSWORD` a required `CHANGE_ME` value, generate one, or keep auth disabled until a password is set.

### #1108 - docs(forge): document RTX 30-series Mobile (sm_86) Torch+CUDA mismatch

- Verdict: **Merge after rebase**.
- Value: Useful. It prevents overgeneralizing a live-tested Forge failure and clearly separates confirmed vs inferred hardware impact.
- Cleanliness: GitHub reports `BLOCKED`; docs/manifest comments only.
- Safety: Low.
- Proof: Static review confirms the README calls out RTX 3070 Mobile sm_86 as confirmed, other hardware as untested, and WSL2 impact as inferred.
- Guidance: Merge once rebased.

## Batch 14: #1109, #1110, #1111, #1112, #1113

### #1109 - fix(localai): switch to non-AIO image to stop silent model download

- Verdict: **Merge after rebase / compose CI**.
- Value: Real. The non-AIO LocalAI image removes the surprise multi-GB startup download and the README now tells users models are not preconfigured.
- Cleanliness: GitHub reports `BLOCKED`; one extension compose plus README.
- Safety: Low-to-moderate because LocalAI still depends on the base `llama-server` service.
- Proof: `docker compose -f resources/dev/extensions-library/services/localai/compose.yaml config --quiet` fails alone because `llama-server` is undefined, which is expected for an extension fragment. The same fragment passes when combined with `dream-server/docker-compose.base.yml` and required placeholder env.
- Guidance: Merge after rebase and compose-fragment CI.

### #1110 - fix(host-agent): rewrite build.context to absolute path on staging

- Verdict: **Merge after rebase / API tests**.
- Value: Real. Build-backed library extensions such as Audiocraft and Open Interpreter need their Dockerfile context to resolve from the copied extension directory, not from `INSTALL_DIR`.
- Cleanliness: GitHub reports `BLOCKED`; API install path plus focused test and two extension READMEs/compose files.
- Safety: Moderate, but acceptable for current library state.
- Proof: `python -m py_compile` passes for `routers/extensions.py` and `test_install_from_library_build_context.py`. A static scan of current library build fragments found only `context: .`, which this helper handles correctly.
- Guidance: Merge once rebased and dashboard-api tests pass. Future hardening should preserve relative subdirectories if a later extension uses `build.context: ./subdir`; the current helper rewrites every relative context to the extension root.

### #1111 - fix(host-agent): start install worker thread before sending 202

- Verdict: **Revise for small fix**.
- Value: The bug is real: the host agent should not return 202 before the worker thread has actually started.
- Cleanliness: GitHub reports `BLOCKED`; one host-agent edit.
- Safety: Not merge-ready because the exception cleanup now releases a lock it may no longer own.
- Proof: `python -m py_compile bin/dream-host-agent.py` passes. Static review shows `_run_install()` releases `lock` in its `finally`, while the outer `try` starts the thread, calls `json_response(self, 202, ...)`, and then releases the same lock in `except Exception`. If the response write fails after the thread starts, the outer handler releases the lock while the install thread is still running; the worker later double-releases and concurrent installs can slip through.
- Guidance: Transfer lock ownership explicitly after `Thread.start()` succeeds. Only release in the outer handler if thread creation/start fails before ownership transfers; do not release on response-write errors after the worker owns the lock.

### #1112 - fix(host-agent): rollback all three config backups on model-activate failure

- Verdict: **Revise for small fix**.
- Value: High. Rolling back `.env`, `models.ini`, and `lemonade.yaml` together is the right model-activation contract.
- Cleanliness: GitHub reports `BLOCKED`; one host-agent edit.
- Safety: Not merge-ready because success is marked after writing the response.
- Proof: `python -m py_compile bin/dream-host-agent.py` passes. Static review shows the success branch restarts services, calls `json_response(self, 200, {"status": "activated", ...})`, then sets `committed = True`. If the response write raises after the model has been activated, the outer `except` sees `committed == False` and rolls all three config files back despite the activation path having succeeded.
- Guidance: Set `committed = True` immediately after health checks/restarts have succeeded and before sending the HTTP response, or isolate response-write failures from activation rollback.

### #1113 - fix(dashboard-api): narrow broad except handlers in main.py per CLAUDE.md rule 1

- Verdict: **Merge after rebase / API tests**.
- Value: Good. It reduces broad exception swallowing in startup/config paths and keeps expected error classes explicit.
- Cleanliness: GitHub reports `BLOCKED`; small API change plus tests.
- Safety: Low-to-moderate because unexpected exceptions will now surface instead of being normalized.
- Proof: `python -m py_compile main.py test_main.py` passes. Static review shows the broad handlers are narrowed to JSON, OS, validation, and subprocess cases.
- Guidance: Merge once rebased and dashboard-api tests pass.

## Batch 15: #1114, #1115, #1116, #1117, #1118

### #1114 - fix(dashboard-api): make /api/update/dry-run non-blocking via httpx

- Verdict: **Revise for small fix**.
- Value: Real. Moving the dry-run GitHub release check from synchronous `urllib` to async `httpx` fixes an event-loop blocking path.
- Cleanliness: GitHub reports `BLOCKED`; one router and matching tests.
- Safety: Nearly merge-ready, but the migration does not preserve the old HTTP status error behavior.
- Proof: `python -m py_compile routers/updates.py tests/test_updates.py` passes. After installing dashboard-api requirements, `pytest tests/test_updates.py -q -k dry_run` passes 6/6. Full `test_updates.py` on Windows fails 5 unrelated tests because local Python decodes `main.py` as cp1252 and Windows cannot execute temporary `.sh` scripts directly.
- Finding: `httpx.AsyncClient.get()` does not raise on 4xx/5xx unless `resp.raise_for_status()` is called. The old `urllib.request.urlopen()` path raised `HTTPError`, so a GitHub 403/rate-limit response now becomes `latest_version: null` with no `version_check_error`.
- Guidance: Add `resp.raise_for_status()` before `resp.json()` and cover a non-2xx response in the dry-run tests, then merge after rebase.

### #1115 - fix(dashboard-api): allow built-in extensions to declare init-time root user

- Verdict: **Merge after rebase / API tests**.
- Value: Real. Built-in extensions are trusted repo content, and OpenClaw-style init-time `user: "0:0"` followed by privilege drop should not be blocked by the user-extension scanner path.
- Cleanliness: GitHub reports `BLOCKED`; small scanner parameter plus tests.
- Safety: Moderate but acceptable because the exemption is limited to paths resolved under `EXTENSIONS_DIR`; user/library extension installs still reject root users.
- Proof: `python -m py_compile routers/extensions.py tests/test_extensions.py` passes. After installing dashboard-api requirements, `pytest tests/test_extensions.py::TestScanComposeSkipRootUserCheck -q` passes 3/3.
- Guidance: Merge after rebase and full dashboard-api CI. Keep an eye on built-in extension review discipline, because built-ins now bypass root-user and GPU-passthrough scanner checks during activation.

### #1116 - refactor(host-agent): migrate systemd unit from user-mode to system-mode

- Verdict: **Revise for architectural rework / Linux smoke**.
- Value: The direction is valuable. A system-mode host-agent can survive logout without lingering and is more appropriate for a daemon that manages Docker.
- Cleanliness: GitHub reports `BLOCKED`; installer phase, CLI agent controls, uninstall, and systemd unit.
- Safety: Not merge-ready. This changes the service manager contract and needs a clean Linux install/upgrade/uninstall smoke.
- Proof: `bash -n installers/phases/07-devtools.sh dream-cli dream-uninstall.sh` passes. Static review shows the installer derives `User=` from `INSTALL_USER`/`SUDO_USER`, but renders `Environment=HOME=__HOME__` from the current shell. Under `sudo bash install.sh`, that can produce `User=<original user>` with `HOME=/root`; host-agent hook environments forward `HOME`, so post-install hooks can run as the user with the wrong home directory.
- Guidance: Resolve and render the home directory for `_agent_user` (for example via `getent passwd "$_agent_user"` or explicit `INSTALL_HOME`), then smoke install, `dream agent start/stop/logs/status`, reinstall, and uninstall on Ubuntu systemd. Also escape placeholder substitution values consistently before writing a root-owned unit.

### #1117 - ci(validate-compose): cover installer overlays via base+overlay merge

- Verdict: **Merge after rebase / CI**.
- Value: Good. The workflow now validates installer compose overlays in the same base+overlay shape Compose actually consumes, and the macOS LiteLLM host-gateway patch moves to a service-specific overlay.
- Cleanliness: GitHub reports `BLOCKED`; workflow plus macOS installer/compose overlay.
- Safety: Low-to-moderate because it touches Apple Silicon compose generation.
- Proof: `bash -n installers/macos/install-macos.sh` passes. `docker compose -f docker-compose.base.yml -f installers/macos/docker-compose.macos.yml config --quiet` passes with placeholder env. The actual macOS LiteLLM stack shape also passes when adding `extensions/services/litellm/compose.yaml` and `extensions/services/litellm/compose.apple.yaml`.
- Guidance: Merge after CI. A follow-up should include service GPU overlays such as `extensions/services/*/compose.apple.yaml` in compose validation triggers/discovery; this PR's workflow only scans `dream-server/installers`.

### #1118 - harden(resolver): scan user-extension and override compose content + boundary-check compose_file

- Verdict: **Keep draft / revise for architectural rework**.
- Value: High. The resolver should not blindly include tampered user-extension composes or manifest `compose_file` paths that escape their directory.
- Cleanliness: Draft and `BLOCKED`; very broad resolver hardening plus a large shell regression script.
- Safety: Not merge-ready. It changes runtime semantics for both user extensions and `docker-compose.override.yml`.
- Proof: `bash -n scripts/resolve-compose-stack.sh tests/test-resolve-compose-resilient.sh` passes, but `bash tests/test-resolve-compose-resilient.sh` fails 26/27 on this Windows Git-Bash environment. The failure is the PR's own loopback-default acceptance case: `${BIND_ADDRESS:-127.0.0.1}:9091:80` is excluded instead of included here. Even if Linux CI passes that portability issue, static review shows the resolver now applies the strict untrusted-extension scanner to `docker-compose.override.yml`, which can silently skip legitimate operator overrides that use absolute host mounts, `extra_hosts`, or other advanced Compose features.
- Guidance: Split the PR. First land compose_file boundary checks and user-extension content scanning. Treat `docker-compose.override.yml` separately with either warnings-only mode, an explicit strict flag, or a documented policy change. Then rerun the resolver tests on Linux and Windows Git-Bash.

## Final accounting

- Total open PRs audited from the refreshed May 2, 2026 list: **75**.
- Merge after stated gates/rebase/CI: **44**.
- Revise before merge: **24**.
- Keep draft until dependency stack settles or rework lands: **4**.
- Reject / do not merge as-is: **3**.

Merge-after-gates PRs:
#961, #974, #998, #1000, #1053, #1057, #1059, #1065, #1066, #1067, #1068, #1070, #1071, #1072, #1073, #1074, #1075, #1076, #1077, #1078, #1079, #1080, #1082, #1085, #1086, #1087, #1090, #1092, #1093, #1094, #1095, #1096, #1097, #1098, #1099, #1100, #1105, #1106, #1108, #1109, #1110, #1113, #1115, #1117.

Needs revision:
#364, #716, #750, #973, #983, #994, #1011, #1017, #1018, #1024, #1039, #1040, #1051, #1069, #1081, #1083, #1088, #1089, #1091, #1107, #1111, #1112, #1114, #1116.

Keep draft:
#1101, #1102, #1104, #1118.

Reject / do not merge:
#351, #1002, #1052.

Machine-readable copy:
`batch-audit-2026-05-02/verdicts-2026-05-02.csv`.
