# Preregistration — Qwen3.6-27B vs Qwen3.8-27B corrective MMBT study

**Status: FROZEN upon commit.** This protocol is committed *before* any new result ingestion.
Cells generated before this commit (the 802-cell freeze of 2026-08-16T14:23:09Z, PR #46, now
draft) are **exploratory evidence only** and feed no confirmatory claim. Any deviation from this
protocol must be recorded in `DEVIATIONS.md` with a timestamp and rationale before the affected
analysis runs.

## 1. Verified sampler ground truth (the defect this study corrects)

Verified 2026-08-16 against the pinned card revisions by fetching the raw files:

| source (pinned) | thinking | non-thinking |
|---|---|---|
| `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, README L635-637 | T1.0 / top_p 0.95 / top_k 20 / min_p 0 / pp 0 / rp 1 (T0.6 variant for precise coding) | **T0.7 / top_p 0.80 / top_k 20 / min_p 0 / pp 1.5 / rp 1** |
| `Qwen/Qwen3.8-27B` @ `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, README L252-253, worked example L452-460 | T1.0 / top_p 0.95 / top_k 20 / min_p 0 / pp 0 / rp 1; `reasoning_effort` ∈ {xhigh (default), medium, low}; `preserve_thinking` default on | **identical: T0.7 / top_p 0.80 / top_k 20 / min_p 0 / pp 1.5 / rp 1** |

Both models' `generation_config.json` (T1.0/0.95/top_k20) encodes the *thinking* defaults.
Consequences for the prior corpus: its "3.6 vendor no-think" arm (T1/0.95/pp0, thinking
disabled) ran 3.6 at its thinking sampler in non-thinking mode — off-spec — so the prior
"vendor vs vendor" contrast is mode/sampler-confounded, and **no prior cell exists for 3.6
non-thinking at its official sampler.** The prior thinking arms were at the correct official
thinking sampler for both models but pooled 3.8 reasoning-effort levels.

## 2. Arms

All arms: UD-Q4_K_XL GGUF unless stated, llama.cpp image digest pinned in §5, `--parallel 1`,
ctx 262144, identical flags across models except `--model`/`--alias`.

| arm id | models | sampler | thinking | role |
|---|---|---|---|---|
| `official-nothink` | both | **T0.7 / top_p 0.80 / top_k 20 / min_p 0 / pp 1.5 / rp 1** | off (`enable_thinking=false`) | **PRIMARY** |
| `official-think` | both | T1.0 / top_p 0.95 / top_k 20 / min_p 0 / pp 0 / rp 1 | on; **Qwen3.8: `reasoning_effort=xhigh` ONLY, `preserve_thinking=true`; Qwen3.6: normal thinking** | secondary (confirmatory, Holm) |
| `diag-t03` | both | T0.3 / top_p 0.8 / top_k 20 / min_p 0 / pp 0 / rp 1 | off | **diagnostic, explicitly off-spec for both** — exploratory only |
| `quant-pilot` | both × {Q4_K_XL, Q8_0} | official-nothink sampler | off | quant crossover pilot (§7) |

No other arm may be added after this commit. `reasoning_effort` levels other than xhigh are out
of scope. The Qwen3.6 T0.6 coding-thinking variant is NOT run (secondary at best; excluded to
protect fixed N).

## 3. Design

- **12 task families** (the existing MMBT set), with `p3_market` converted to a **frozen
  offline fixture** (snapshot of its web targets committed in-repo, harness network access to
  the live web disabled for that family). If the fixture fails its determinism check before
  campaign start, `p3_market` is demoted to exploratory and the primary proceeds on 11 families
  — decided before Phase B, recorded in DEVIATIONS.md.
- **Six seeds**, fixed and distinct: **101, 211, 307, 401, 503, 601.** Seed is set per cell.
- **N is fixed**: 12 families × 6 seeds × 2 models per confirmatory arm (`official-nothink`,
  `official-think`) = 144 cells per arm, 288 confirmatory cells. `diag-t03` runs 3 seeds
  (101, 211, 307) = 72 cells, exploratory. No optional stopping; the campaign ends when the
  ledger is complete, not when a result looks good.
- **Host crossover (Towers 1/3, both capped 500 W):** seeds 101/211/307 — Tower1 serves
  Qwen3.8, Tower3 serves Qwen3.6; seeds 401/503/601 — the exact model artifacts swap hosts.
  Task order interleaved (family-major, alternating model start). Tower1's second (ODS) inference
  process is drained for the duration of clean runs and restored after.
- **Tower2 / DSV4:** DSV4 remains serving throughout, except one **bounded maintenance window**
  for the quant pilot (§7), after which DSV4 is restored and verified against the captured
  baseline.

## 4. Outcomes, termination, and metrics

- **Primary outcome: end-to-end successful delivery** — the cell terminates via the model's own
  `done` signal AND produces `summary.json` + `workspace_final.tar.gz` AND its deliverable
  passes the deterministic artifact-delivery validator (existence/schema, not quality).
- **Termination is fully automated.** No operator judgment in outcome assignment. Terminators:
  (a) harness stuck detector (unchanged thresholds, preregistered);
  (b) **loop terminator**: exact consecutive run ≥ 30 of identical `(tool_name,
  canonical_json(arguments))` → mechanical kill + machine-written label;
  (c) wall-clock ceiling 3 h/cell → `timeout` label.
- **Primary repeat metric** (documentation and implementation identical): longest exact
  consecutive run over `(tool_name, canonical_json(arguments))`, flagged at ≥ 30.
  `max_freq≥30` and digit-normalized variants are **exploratory** and labelled as such wherever
  they appear. Delivery flags and loop flags are distinct columns; a cell can loop and still
  deliver.
- Full tool-signature streams (name + canonical args hash + wall + result_len per call) are
  stored per cell sufficient to recompute every metric from committed evidence.

## 5. Pinning

Committed in `manifest/` before Phase B: model file sha256s (both GGUFs; Q8_0 files for the
pilot), base revisions (`6a9e13bd…`, `1d4bf0f2…`), llama.cpp image digest, llama binary
version string, harness sha256, grader sha256s (v2, post-fix), task + fixture sha256s, host
inventory (GPU model/driver/power cap), endpoint map, and the two README sha256s fetched at the
pinned revisions. The two legacy cells on harness `fdbc1584…` (prior corpus) are excluded from
every table of this study mechanically by harness-hash filter — stated once, applied everywhere.

## 6. Statistical analysis plan

- **One preregistered primary contrast:** P(delivery | Qwen3.8) − P(delivery | Qwen3.6) at
  `official-nothink`, **paired by family × seed** (72 pairs). Inference: exact McNemar on
  discordant pairs, plus a family-cluster randomization test (sign-flip at family level,
  10,000 permutations, statistic = mean paired difference). Cluster bootstrap (families) for the
  CI; wild-cluster as robustness. Effect size: paired risk difference with 95% CI.
- **Secondary contrasts (Holm-adjusted, in this order):** (1) delivery at `official-think`
  (xhigh-only vs normal thinking); (2) loop-flag rate at `official-nothink` (primary metric).
- **Cell-level Fisher exact appears only as descriptive sensitivity analysis**, labelled
  "treats cells as independent; anti-conservative under family/seed clustering."
- **Equivalence claims require TOST** against a preregistered margin of **±10 pp** on paired
  delivery difference; power for the margin at n=72 pairs is reported alongside. Where the TOST
  does not reject, the only permitted language is **"no detected difference (CI −x to +y)"**.
- Conditional-on-delivery quality is **survivor/post-treatment analysis**: reported, labelled,
  never a headline.
- **Claim language contract:** effects are described as "suite/build/mode/sampler-specific
  delivery effects." Prohibited without their stated evidence: general capability regression
  claims; quant causal claims (needs §7 crossed evidence); equivalence claims (needs TOST);
  "thinking restores delivery" as causal (needs clean within-model paired design — the
  think/no-think contrast here differs in sampler too, and is labelled accordingly).

## 7. Quant crossover pilot (bounded Tower2 window)

Both models × {UD-Q4_K_XL, Q8_0} at `official-nothink`, seeds 101/211, 12 families
= 96 cells, on Tower2's two RTX PRO 6000s with **GPU↔model assignment crossed between the two
seeds**. DSV4 is drained at window open and restored + verified at window close; the window is
bounded to this pilot only. Decision rule, preregistered: if Q4-vs-Q8 paired delivery difference
within either model has |Δ| ≥ 15 pp with McNemar p < 0.05, quantization is implicated and a
BF16 arm is added for that model (new bounded window); otherwise the quant-causal question is
reported from the pilot alone. No quant claim of any kind is made from single-model evidence.

## 8. Grader and fixture fixes (committed with this protocol, before results)

- **Word-counter contract (D1):** graders count words with the same command the task briefs now
  name explicitly (`wc -w`), with a ±3% tolerance band at the ceiling; the brief text states the
  counter and the band.
- **D2 (`p3_pm`):** semantic risk matching (the repo's R3-equivalence rule) replaces literal
  keyword matching; unit tests cover contracted/uncontracted forms.
- **D3 (`p2_triage`):** ground truth aligned to the brief (`n/a` credited for the three
  noise/spam tickets; ticket 029's extortion classification resolved consistently between brief
  and ground truth); grader vocabulary parsed from the brief.
- Graders are versioned (`graders/v2/`), sha-pinned in the manifest; the prior campaign's v1
  graders and overlay remain untouched for longitudinal comparability.
- **Row-level evidence manifest + deterministic artifact-delivery validator** ship with this
  commit and are CI-enforced (`make verify-study`).

## 9. Prior-corpus labelling

The 802-cell freeze remains in the repository as exploratory evidence with its receipts intact,
relabelled per the above: its "vendor" 3.6 no-think arm is annotated *thinking-sampler,
off-spec*; contradictory historical receipts (host and GGUF-ftype differences) are preserved and
labelled, never rewritten. No same-rig/same-quant language survives anywhere in the entry.
