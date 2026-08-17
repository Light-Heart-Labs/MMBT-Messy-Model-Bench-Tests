# PREREGISTRATION — Amendment 1

**Status: committed BEFORE any quant-pilot observation.** Verified firsthand on the campaign
host at **2026-08-17T10:46:14Z** (and re-verified immediately before this commit): **zero
`quant-pilot` cells exist** in the campaign ledgers.

- `logs/corrective/cell_outcomes.jsonl` — distinct arms: `official-nothink`, `official-think` only.
- `logs/corrective/manifest-mid-campaign.jsonl` — distinct arms: `official-nothink`,
  `official-think`, `diag-t03` only.
- No quant-pilot preflight record exists under `logs/corrective/`, no cell log directory
  matches any quant-pilot label (`*quantpilot*`, `*q80*`, `*q8_0*`), and no quant-pilot
  serving container is or has been running. The bounded Tower2 pilot window
  (PREREGISTRATION.md section 7) has not opened.

This amendment is **insertion-only**: `PREREGISTRATION.md` is not edited. The sentences it
supersedes are listed below by section; where a listed sentence conflicts with this amendment,
the amendment governs. Everything not listed is unchanged.

---

## Amendment 1a — the conditional BF16 arm is a preregistered exception to the no-new-arms rule (audit finding A6)

1. **Exception, stated as such.** Section 2 rules "No other arm may be added after this
   commit." The conditional BF16 arm of section 7 is hereby a **preregistered exception** to
   that rule — the only one. No other arm may be added.

2. **Exact decision rule (mechanical, no operator discretion).** The BF16 arm is triggered if
   and only if, **within either model**, the Q4_K_XL-vs-Q8_0 comparison from the completed
   quant pilot satisfies **BOTH**:
   - |paired delivery delta| >= 15 pp (pairs = family x seed on the pilot grid), **AND**
   - exact McNemar p < 0.05 on the discordant pairs of that within-model comparison.

   The trigger is evaluated once, from the completed pilot ledger, by the same mechanical
   tooling that computes every other delivery contrast. A trigger in either model opens one
   new bounded Tower2 window.

3. **Fixed N.** If triggered, the BF16 arm is **12 families x 2 seeds (101, 211) x 2 models
   at BF16 = 48 cells**, run under the section 7 window discipline (drain, restore, verify).
   No optional stopping, no extension, no partial run counts as evidence.

4. **Identical analysis.** The BF16 arm is analyzed exactly as the pilot: paired exact
   McNemar on discordant pairs plus the family-cluster randomization test by **exact
   enumeration** (Amendment 1b), same primary outcome definition, terminators, delivery
   validator, and evidence manifest as sections 4-5. No new metrics.

5. **Claim-language constraint.** A **triggered** BF16 arm **reopens** the quant question; it
   does not settle it. From the moment the trigger fires until the BF16 arm completes its
   fixed N, the only permitted quant language is "quantization implicated at pilot; BF16 arm
   pending." No claim may treat the quant question as resolved in either direction during
   that interval. Only after the BF16 arm completes may quant-causal language be used, and
   then only under the section 6 claim-language contract.

**Superseded/qualified sentences (listed by section):**
- Section 2, closing paragraph: "No other arm may be added after this commit." — now carries
  the single exception defined in 1a.1-1a.3 above.
- Section 7, decision-rule sentence: "if Q4-vs-Q8 paired delivery difference within either
  model has |delta| >= 15 pp with McNemar p < 0.05, quantization is implicated and a BF16 arm
  is added for that model (new bounded window); otherwise the quant-causal question is
  reported from the pilot alone." — formalized by 1a.2-1a.5 (thresholds unchanged; the
  conjunction of both conditions is explicit; fixed N and claim constraint added; the arm
  runs both models when triggered).
- The mirror text in `tooling/corrective/configs/quant-pilot.json` (`_decision_rule`) remains
  in place as descriptive text; this amendment governs on any divergence.

---

## Amendment 1b — family-cluster inference by exact enumeration (audit finding A7)

1. The family-cluster randomization test is computed by **EXACT enumeration of all
   2^12 = 4096 family sign assignments** (sign-flip at family level; statistic = mean paired
   difference). If `p3_market` is demoted to exploratory per section 3, enumeration is over
   **all 2^11 = 2048 assignments** on the remaining 11 families.
2. **P-values from this test are exact.** There is no sampling, no Monte Carlo draw, no
   permutation count, and no randomization seed anywhere in this test.
3. This **replaces the 10,000-sample wording everywhere it appears**. Verified: within this
   branch that wording appears in exactly one place —

   **Superseded sentence (listed by section):** Section 6, first bullet: "plus a
   family-cluster randomization test (sign-flip at family level, 10,000 permutations,
   statistic = mean paired difference)" — now reads: "plus a family-cluster randomization
   test (sign-flip at family level, **exact enumeration of all 2^12 = 4096 sign assignments**
   — 2^11 = 2048 if `p3_market` is demoted per section 3 — statistic = mean paired
   difference; p-values exact)."
4. The same exact-enumeration rule applies to every family-cluster randomization test in this
   study, including the quant pilot and, if triggered, the BF16 arm (Amendment 1a.4).

---

## Amendment 1c — CI enforcement status: what is gated NOW vs the Phase D `verify-study` gate (audit finding A3)

1. **The present-tense claim, corrected.** Section 8 states that the row-level evidence
   manifest and the deterministic artifact-delivery validator "ship with this commit and are
   CI-enforced (`make verify-study`)." The artifacts do ship with this branch. The CI claim
   was ahead of the wiring: **no `make verify-study` target exists yet** — there is no
   Makefile on this branch — and no CI job reproduces the study ledger. This amendment
   replaces that present-tense claim with the precise enforcement status below.

2. **Enforced NOW, by `.github/workflows/verify-methodology.yml`** (added with this
   amendment; runs on `push` and `pull_request` for the methodology paths — `tooling/**`,
   this benchmark entry, `.gitattributes`, and the workflow itself). The gates are exactly:
   - **Unit suites, all green:** every grader-v2 test (`tooling/graders/v2/tests/`), the
     loop-terminator suite, the delivery-validator suite, and the evidence-manifest suite
     (`tooling/corrective/test_{loop_terminator,delivery_validator,evidence_manifest}.py`),
     with a floor asserting at least the 64 audited tests are collected (65 at the time of
     this amendment).
   - **Fixture-mirror determinism:** `serve_fixtures.py` is started in the runner and
     `check_fixture_determinism.py` must pass twice against it (byte-identical double-fetch
     of all 36 snapshots + catalog pages, sha256s matching `index.json`).
   - **Syntax gates:** `python3 -m py_compile` over all tooling Python;
     `bash -n` over all tooling shell.
   - **Hermetic corrective dry-runs:** `dryrun_argv_capture.sh` and
     `dryrun_v2_wiring_capture.sh` (fake-transport argv capture; each asserts its own
     post-run worktree cleanliness). `dryrun_request_body.sh` is **not** run in CI — it
     needs the campaign host's docker sandbox image — and stays a campaign-host preflight;
     its exit-0 and cleanliness contract is asserted inside the script itself.
   - **Hygiene:** `git diff --check` against the merge-base with `main` (under the
     `.gitattributes` fixture-pin policy of this branch), plus a guard failing the build if
     anything under `benchmarks/qwen36-vs-qwen38-27b-2026-08/` (the held exploratory results
     entry) exists on this branch.

3. **Deferred to Phase D (before any results PR merges).** The full `verify-study`
   reproduction gate — regenerating the row-level evidence manifest from the completed
   study ledger, running the delivery validator over every cell, and failing CI on any
   mismatch — requires a completed campaign ledger and therefore lands in **Phase D**, wired
   into CI **before the results PR merges**. Until then, evidence-manifest and
   delivery-validator enforcement in CI is at unit-test level only (point 2), and no results
   claim may cite `verify-study` as an already-operating gate.

**Superseded/qualified sentences (listed by section):**
- Section 8, final bullet: "**Row-level evidence manifest + deterministic
  artifact-delivery validator** ship with this commit and are CI-enforced
  (`make verify-study`)." — now reads per 1c.1–1c.3: they ship with this branch; CI
  enforcement today is `verify-methodology.yml` at unit-test level; the full
  `verify-study` reproduction gate is Phase D scope, in place before the results PR merges.
