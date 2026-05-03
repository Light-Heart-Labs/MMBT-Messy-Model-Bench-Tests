# Roadmap

> Consolidated list of open questions, validation gaps, and contribution opportunities surfaced across the benchmark entries. Each item links to the source doc that motivated it.
>
> Items marked **[contributor-welcome]** are scoped so that an external contributor with the right hardware can take them end-to-end via the [`tooling/`](tooling/) reproduction pack and submit results as a PR.
>
> **Last reviewed**: 2026-05-03.

## Active follow-ups (in priority order)

### 1. FP8 re-run of the 12-cell microbench grid &nbsp; **[contributor-welcome]**

**Source**: [`KNOWN-LIMITATIONS.md` § Cyankiwi 4-bit AWQ field reports](KNOWN-LIMITATIONS.md#quantization-specificity), [`benchmarks/microbench-phase-b-2026-05-02/findings.md` § Recommended follow-ups](benchmarks/microbench-phase-b-2026-05-02/findings.md#recommended-follow-ups)

Multiple practitioners report that the Cyankiwi 4-bit AWQ quants underperform official Qwen FP8 of the same base models. Re-running the full 12-cell × N=10 grid on FP8 would let current findings generalize across quants or be bounded as quant-specific.

What to do: pull official Qwen FP8 quants, run the 4-command friendly path in [`tooling/ADDING-A-MODEL.md`](tooling/ADDING-A-MODEL.md) for each model arm, submit a PR with the results.

Hardware: needs FP8-capable GPU. RTX PRO 6000 / H100 / similar.

### 2. PASS-rate grader sweep on the no-think tarballs

**Source**: [`benchmarks/microbench-phase-b-2026-05-02/findings.md`](benchmarks/microbench-phase-b-2026-05-02/findings.md)

Current 95.8% headline for 27B-no-think is `done_signal` rate. Need to run the existing graders against the 120 no-think workspace tarballs to convert ship rate to PASS rate. The `p3_doc` 8/10 ship rate especially could be paying real PASS or could be shipping briefs over the 700-word limit.

Internal — uses the source bench's full transcripts, not just the published representatives.

### 3. M-series Mac sibling study &nbsp; **[contributor-welcome]**

**Source**: [`COMPARISON.md` § Other hardware classes](COMPARISON.md#other-hardware-classes)

The dense-vs-MoE compute tradeoff inverts on unified memory: Coder-Next (3B-active) wins on tokens-per-second; 27B (full-dense compute) becomes the bottleneck. Untested.

What to do: run the same 12 cells on M-series via MLX. Only the vLLM launch commands swap; harness is portable.

Hardware: M-series Mac with ≥48 GB unified memory.

### 4. Language-mix expansion for Phase 1 &nbsp; **[contributor-welcome — task-design first]**

**Source**: [`COMPARISON.md` § Languages other than Python](COMPARISON.md#languages-other-than-python)

Current Phase 1 cells (`p1_bugfix`, `p1_refactor`, `p1_testwrite`) all use a Python project (`logalyzer`). Adding C, JavaScript, or systems-programming starters would test whether Coder-Next's code specialization manifests differently outside Python.

This is task-design work first (find / write a starter project with planted bugs of comparable difficulty), then a benchmarking session. Not a one-command re-run.

### 5. Pairwise quality study extension to the 4 differential cells

**Source**: [`benchmarks/microbench-phase-b-2026-05-02/findings-pairwise-quality-three-model.md`](benchmarks/microbench-phase-b-2026-05-02/findings-pairwise-quality-three-model.md)

The hand-graded quality study covers the 3 both-ship cells (p2_ci, p2_extract, p2_triage). The 4 differential cells (p2_hallucination, p3_business, p3_doc, p3_market) where models ship at different rates haven't been hand-graded for substantive quality of the runs that *did* ship.

### 6. Re-run N=3 P1 cells for 27B-thinking on the current harness

**Source**: [`benchmarks/microbench-phase-b-2026-05-02/findings.md` § Caveats](benchmarks/microbench-phase-b-2026-05-02/findings.md#caveats)

The 27B-thinking 1/9 P1 ship rate may include harness-drift effects (older `file_sha256: 7698067...` vs current `7ea9592...`). Definitively settle whether it's drift or a real model regression.

### 7. Per-claim rubric pass on cloud entries

**Source**: [`KNOWN-LIMITATIONS.md` § Comparison-to-cloud caveats](KNOWN-LIMITATIONS.md#comparison-to-cloud-caveats)

Cloud Opus-4.7 / GPT-5.5 entries weren't graded with the same per-claim rubric used on the local entries. Cloud-vs-local comparison is currently *categorical* only ("cloud ships, local mostly doesn't"), not per-claim accuracy. Building a uniform rubric and applying it to both classes would let head-to-head claims go beyond shipping rates.

### 8. Citation-validity full sweep on `p3_market` 27B

**Source**: [`SCORECARD.md`](SCORECARD.md), [`COMPARISON.md` § What we don't know yet](COMPARISON.md#what-we-dont-know-yet)

Sampled 18/33 URLs (~55%) from one 27B market-research run; measured 75% valid in that sample. Remaining 15 URLs unverified. Full sweep would tighten the citation-validity number from sample to measured.

### 9. 27B-no-think on dreamserver-scope tasks

**Source**: [`COMPARISON.md` § What we don't know yet](COMPARISON.md#what-we-dont-know-yet)

The no-think arm hasn't been run against the 1-PR or 75-PR audits. The substance-monitoring methodology proven on phase-b would transfer; the verdict-production issue 27B-thinking had on PR #1057 *might* improve with no-think — hypothesis only.

### 10. 27B-no-think on the wallstreet investment-memo task

**Source**: [`COMPARISON.md` § What we don't know yet](COMPARISON.md#what-we-dont-know-yet)

Untested. Given the no-think mode's clean shipping on `p3_business` (8/10) and `p3_doc` (8/10), plausible it would handle the multi-section memo cleanly — but unmeasured.

## Welcomed contributions

Beyond the prioritized follow-ups above, contributions in these shapes are explicitly welcome:

- **New model entries** — any vLLM-supported local model with a working tool-call parser. End-to-end walkthrough: [`tooling/ADDING-A-MODEL.md`](tooling/ADDING-A-MODEL.md). Half-day to one-day operator time.
- **Same model, different quant** — official FP8, Unsloth UD4 GGUF, BF16, etc. Same friendly path; only the HuggingFace path + vLLM launch flags change.
- **Field reports** — anecdotal but specific reports of model behavior on real workflows. See [`FIELD-REPORTS.md`](FIELD-REPORTS.md) for the template; one example use case is the Cyankiwi-vs-FP8 quant divergence many practitioners have reported.
- **Methodology improvements** — better grader scripts, additional task families, refined failure-mode taxonomy entries. See [`tooling/FAILURE-TAXONOMY.md`](tooling/FAILURE-TAXONOMY.md) and [`tooling/graders/`](tooling/graders/).
- **Bug reports on harness, graders, or analysis** — open an issue.

## Methodology improvements (longer-horizon)

Items that would require larger structural work, not just a re-run:

- **Per-claim rubric** uniformly applied across local + cloud entries (item 7 above is one cell of this)
- **Larger N (N=30+) on highest-signal cells** to tighten Wilson CIs from "real failure shape" to "bounded rate"
- **More PR shapes for the dreamserver benchmark family** — current 1-PR audit pins to PR #1057 specifically. A docs-only PR, a security PR, and a refactor PR would give different complexity-ceiling data points
- **Higher-precision quantizations of 35B-A3B** — currently fails at 4-bit AWQ; FP8 / BF16 untested
- **Long-horizon agentic improvements** — both local arms find degenerate failure modes within 30-60 min on the 75-PR task. Methodology for keeping local agents productive past 30 min is an open research question

## How to use this doc

If you're picking work, start at the top of "Active follow-ups" — they're prioritized.

If you're contributing externally, look for **[contributor-welcome]** flags. Items 1, 3, and 4 are the highest-leverage external contributions because they unblock validity-boundary claims this benchmark can't make on its own hardware.

If you're maintaining: review this doc when major work lands. Items move from "Active" to "Done" via PRs that link back here; items added from new findings docs should also link back to their source.
