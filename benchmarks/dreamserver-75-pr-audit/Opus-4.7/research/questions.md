# Audit Questions Log

Append-only record of questions that came up during the audit. Each entry has
the question, when it was raised, and how it was resolved (or what assumption
was made).

---

## Q1 — Why are 72 of 75 PRs failing the same `integration-smoke` check?

**Raised:** 2026-04-27, during initial CI-failure clustering.

**Hypothesis 1:** A required CI secret is missing for fork PRs.
**Hypothesis 2:** A flaky test.
**Hypothesis 3:** A real broken test on `main`.

**Resolution:** Real broken test on `main`. The failing assertion is in
`dream-server/tests/bats-tests/docker-phase.bats:100`:

```bash
@test "_docker_cmd_arr: returns sudo docker when DOCKER_CMD is sudo docker" {
    run bash -c '
        DOCKER_CMD="sudo docker"
        _docker_cmd_arr() {
            case "${DOCKER_CMD:-docker}" in
                "sudo docker") echo "sudo" "docker" ;;
                *)             echo "docker" ;;
            esac
        }
        _docker_cmd_arr
    '
    assert_output $'sudo\ndocker'    # <-- expects two lines
}
```

`echo "sudo" "docker"` produces `sudo docker\n` — one line, space-separated.
The assertion `$'sudo\ndocker'` expects two separate lines. The test has been
wrong all along; either the function should be
`printf '%s\n' "sudo" "docker"` or the assertion should be
`assert_output "sudo docker"`.

**Implication for the audit:** CI red on `integration-smoke` is **not** a
per-PR failure signal. Verdicts that read CI status pull only the *other*
checks (lint, type-check, dashboard, validate-compose, etc.) and explicitly
note the integration-smoke failure as pre-existing.

Reproduction script: `testing/reproductions/repro-bats-docker-cmd-arr.sh`.

**Action for maintainer:** A trivial 1-line fix on `main` will turn 72 PRs
green-ish overnight. Documented in `report/project-health.md` and
`report/executive-summary.md` as a top-priority pre-merge action.

---

## Q2 — Are the four setup-wizard PRs (#1003 #1015 #1018 #1019) intentionally split?

**Raised:** 2026-04-27, during file-overlap clustering.

**Observation:** Four PRs from Yasin all touch `Extensions.jsx`,
`SetupWizard.jsx`, `TemplatePicker.jsx`, `templates.js`,
`dashboard-api/routers/setup.py`, and `scripts/dream-test-functional.sh`.

**Resolution:** Reading the titles and bodies, the four PRs split as:

- **#1003** (not draft) — sentinel-based success detection (the underlying mechanism)
- **#1015** (draft) — defensive fixes in the picker
- **#1018** (draft) — BATS regression coverage
- **#1019** (draft) — exception-path coverage and tests

The split is **intentional and clean** — #1003 is the substantive change,
#1015–#1019 are defense-in-depth and test coverage. They want to be merged in
order: #1003 first, then the test/refactor PRs which depend on the sentinel
contract being live. Documented in `analysis/dependency-graph.md`.

---

## Q3 — Does PR #988 (loopback for llama-server + host-agent) interact with the openclaw fix from PR #67 (closed)?

**Raised:** 2026-04-27, while reading SECURITY_AUDIT.md.

**Resolution:** They're complementary, not overlapping. PR #67 (closed)
fixed openclaw's `0.0.0.0` binding. PR #988 fixes llama-server and the host
agent — different services. The SECURITY_AUDIT file confirms openclaw was a
separate finding (H3) and llama-server/host-agent were not mentioned at audit
time, but the same loopback policy applies.

PR #988 also touches `installers/macos/install-macos.sh` and
`installers/windows/install-windows.ps1`, suggesting it's the cross-platform
follow-on to the openclaw fix. The verdict on #988 covers all three platforms.

---

## Q4 — Is `gabsprogrammer`'s mobile PR (#961, Termux + a-Shell) in scope for DreamServer?

**Raised:** 2026-04-27, during clustering.

**Observation:** PR #961 adds 6,891 lines across 30 files for Android Termux
and iOS a-Shell support. DreamServer's stated platform support is Linux,
Windows, macOS — mobile is not listed.

**Resolution:** Read the PR body (in raw/meta.json) and the project README's
roadmap section. Mobile is not on the roadmap. This is a **fit** question:
either DreamServer wants to add a mobile target (and #961 is the seed) or it
doesn't. This is a **HOLD — needs maintainer judgment** verdict, not a
reject. Detailed reasoning in `prs/pr-961/verdict.md`.

---

## Q5 — Does PR #983 (Vast.ai p2p-gpu toolkit) violate "no cloud" positioning?

**Raised:** 2026-04-27, while reading the PR body.

**Observation:** DreamServer's tagline is "No cloud, no subscriptions."
PR #983 adds tooling to deploy DreamServer onto Vast.ai cloud GPU instances
— which is, by definition, cloud.

**Resolution:** This is a positioning question for the maintainer. The PR
itself is well-structured (it adds *resources/*, not the core install path),
and offering a cloud-deploy *recipe* is different from making the product
itself cloud-dependent. But the README and marketing copy say no-cloud, and
this PR makes that messaging less crisp. **HOLD — needs maintainer judgment**
on whether the brand allows a cloud-deploy recipe. Detailed reasoning in
`prs/pr-983/verdict.md`.
