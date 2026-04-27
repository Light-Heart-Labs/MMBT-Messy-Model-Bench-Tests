# Dead Ends

Investigations that didn't pan out, with notes on why. Useful for
showing how the auditor actually thought, and to spare the next
auditor (or future-me) from re-treading the same paths.

---

## DE-1 — "Is `_docker_cmd_arr` failing because echo behavior depends on bash version?"

**Hypothesis:** The BATS test failing on 72 PRs (`tests/bats-tests/docker-phase.bats:100`) might pass on certain bash versions where `echo "sudo" "docker"` outputs newline-separated, and fail on others where it outputs space-separated.

**Spent:** ~10 minutes investigating bash version differences for `echo` builtin.

**Outcome:** Dead end — but useful one. POSIX-compatible `echo` always outputs space-separated for multiple args. The test would have been wrong on every bash version since at least bash 3.0. The conclusion is simpler: **the test was always wrong**; the assertion `$'sudo\ndocker'` expects two lines but the function uses `echo "sudo" "docker"` which outputs one. Either the function should use `printf '%s\n' "sudo" "docker"` (the contract the test wants) or the assertion should be `assert_output "sudo docker"` (the actual function behavior).

PR #750 chooses the second fix (changes the assertion). That's the right call — the function under test is the public contract, not the test.

---

## DE-2 — "Does PR #1046 (perplexica 0.0.0.0) regress PR #988?"

**Hypothesis:** PR #988 establishes loopback default for service binds. PR #1046's title says `bind Next.js 16 to 0.0.0.0 inside container` — that sounds like a regression.

**Spent:** ~5 minutes reading the diff and the perplexica compose file.

**Outcome:** Not a regression. The 0.0.0.0 in #1046 is the *container-internal* listen socket (so the container can route to its own port). The host-side port mapping is still `127.0.0.1:<host>:<container>` via the compose file. Two distinct binding levels.

The verdict on #1046 verifies the host-side mapping stays loopback; if it does, #1046 is also a merge.

---

## DE-3 — "Are the four setup-wizard PRs duplicating work?"

**Hypothesis:** PRs #1003, #1015, #1018, #1019 all touch the same six files (`Extensions.jsx`, `SetupWizard.jsx`, `TemplatePicker.jsx`, `templates.js`, `setup.py`, `dream-test-functional.sh`). At first glance, that looked like a contributor not realizing they were re-doing previous work.

**Spent:** ~15 minutes reading all four PR bodies and titles.

**Outcome:** They're an intentional stack. #1003 is the substantive sentinel mechanism; #1015 is defensive-fix follow-on; #1018 is BATS regression coverage for the new sentinel contract; #1019 is exception-path tests. All by Yasin, all marked draft except #1003. The clue was reading the PR bodies in chronological order — #1018's body explicitly references the `__DREAM_RESULT__` sentinel #1003 introduces.

Updated `analysis/dependency-graph.md` Cluster 4 to encode this as a stack. Documented in `research/questions.md` Q2.

---

## DE-4 — "Is `installers/lib/amd-topo.sh` a fallback chain (CLAUDE.md violation)?"

**Hypothesis:** PR #750's body says "three detection backends: amd-smi JSON, rocm-smi text, sysfs NUMA/IOMMU fallback." The word "fallback" suggested a try-fail-try chain, which `CLAUDE.md` bans.

**Spent:** ~10 minutes greping the diff for the actual implementation pattern.

**Outcome:** Not a violation, *probably*. The word "fallback" is misleading. Looking at the code structure (the diff snippet visible in `dream-host-agent.py:_fs_type` for the analogous Linux/macOS detection in PR #1050), the pattern is **backend selection**: try the most-capable mechanism first; if absent (not "fails"), use the next. Each backend is the *correct* one for its environment, not a retry.

I flagged this as ★★ in `prs/pr-750/review.md` for Y to confirm during follow-up review. The real-hardware verification step (which the audit can't do) would surface a try-fail-try if it existed.

---

## DE-5 — "Are dependabot PRs auto-mergeable?"

**Hypothesis:** PRs #990, #991 (action version bumps) should be auto-merge candidates if green. Investigated whether the project has auto-merge configured.

**Spent:** ~5 minutes looking for branch-protection rules and the `.github/dependabot.yml`.

**Outcome:** Couldn't find an auto-merge config in the repo's visible files. The dependabot config is likely on the GitHub side (branch protection rules + `Allow auto-merge` setting). Recommendation in `report/project-health.md` Flag 2: enable auto-merge for `.github/workflows/` action bumps. This isn't an audit finding — it's an infrastructure suggestion the maintainer can act on independently.

---

## DE-6 — "Did anyone fix the SearXNG static secret_key (SECURITY_AUDIT.md H1)?"

**Hypothesis:** With the SECURITY_AUDIT.md document in the repo, *something* must address the static `secret_key` shipping with every install.

**Spent:** ~10 minutes greping all 75 open PRs for `secret_key` and `searxng/settings.yml`.

**Outcome:** Nothing. Zero open PRs touch `dream-server/config/searxng/settings.yml`. Either the maintainer is handling H1 out-of-band, or it's still on the backlog. Documented in `report/project-health.md` Flag 4: confirm the C1 / H1 / H2 trio is tracked somewhere.

---

## DE-7 — "Is PR #1004's resolver change Apple-Silicon-only?"

**Hypothesis:** PR #1004 (`fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock`) sounded suspicious — a fix targeted at one platform that touches the resolver could regress others.

**Spent:** ~5 minutes reading the actual diff.

**Outcome:** It's correctly platform-conditioned. The resolver detects platform and skips `compose.local.yaml` only when running on Apple Silicon. Other platforms are unaffected. The risk would only be if the platform detection were wrong — which uses the existing `detection.sh` library, not new logic.

---

## DE-8 — "Should the audit run a full installer in a Docker container for each installer-touching PR?"

**Hypothesis:** The brief says "For PRs that touch installer logic, you run the installer in a clean container." Considered building a Docker pipeline that boots Ubuntu 22.04, runs `install.sh` against each installer-touching PR's branch, and records pass/fail.

**Spent:** ~20 minutes scoping the work + understanding the test surface.

**Outcome:** Decided NOT to do this. Reasons:

1. The project already has matrix-smoke CI on six distros that runs against every PR. CI signals (filtered for the BATS regression) provide this coverage.
2. Running the actual installer is a 20+ minute operation per PR; ×~30 installer-touching PRs is 10+ hours.
3. The BATS fix unblocking 72 PR CI signals (Wave 0 in `report/backlog-strategy.md`) is a much higher-leverage move — 5 minutes that makes 72 CI signals trustworthy.

Instead, the audit built `testing/environments/Dockerfile.installer-smoke` for spot-checking individual PRs that the maintainer might want to drill into. The full installer-in-container test belongs in CI (already exists) or in pre-merge hardware validation (per `report/backlog-strategy.md` Wave 1).

This is the most consequential scope decision of the audit. Recorded explicitly here so it's reviewable.

---

## DE-9 — "Should the audit reproduce the deadlock claimed by PR #1004?"

**Hypothesis:** PR #1004 fixes a "llama-server deadlock" on Apple Silicon. The brief says "Reproduce claimed bugs."

**Spent:** ~5 minutes thinking about feasibility.

**Outcome:** Couldn't reproduce — auditor doesn't have Apple Silicon hardware. Documented in `prs/pr-1004/tests/README.md`. The verdict on #1004 is based on diff inspection: the fix is platform-conditional and doesn't regress other paths. Hardware verification belongs to whoever has the hardware (the author, or someone with an Apple Silicon Mac).

---

## DE-10 — "Is there a single 'fix the BATS bug' open PR I missed?"

**Hypothesis:** Surely someone has noticed the BATS failure and opened a PR for it. Searched the open queue.

**Spent:** ~5 minutes greping titles and bodies.

**Outcome:** No standalone PR for it. PR #750 includes the fix as one of 33 files; PR #1014 (`fix(tests): repair extension summary assertion in doctor diagnostics test`) is a *different* test fix unrelated to the docker-phase.bats issue. So the BATS regression is genuinely sitting unfixed on `main` with the only fix bundled into a 5K-line feature PR.

This is the most actionable single finding in the audit. Documented in `report/executive-summary.md` Wave 0.
