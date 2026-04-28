# market-research — Qwen3.6-27B-AWQ

**Run name:** `p3_market_27b_v1` (1 of 3 — all 3 STRUCTURAL_PASS)
**Wall:** 17.3 minutes (1037s), 71 iterations
**Cost upper:** $0.0225
**Verdict:** **STRUCTURAL_PASS** (citation validity is hand-grading placeholder — see caveat in [task README](../README.md))

## What this run did

Drove a multi-step internet-research workflow against the live web. Read documentation pages, vendor pricing pages, comparison articles. Wrote three structured deliverables (`recommendation.md`, `comparison.md`, `sources.md`) plus working notes and decisions.

Specific structural results from `grade.json`:

| Check | Result |
|---|---|
| Required files exist | ✓ all 3 (recommendation.md, comparison.md, sources.md) |
| Recommendation has named product | ✓ |
| Recommendation has tier name | ✓ |
| Recommendation has pricing | ✓ |
| Recommendation has 50-seat math | ✓ |
| Products evaluated in comparison | 5/5 (1Password, Bitwarden, Dashlane, Keeper, LastPass) |
| Inline citations | 18 |
| Distinct URLs cited | 33 |
| Recommendation word count | 1594 |

This is a **complete, structurally-correct deliverable** for an open-ended internet-research task — the kind of output you'd expect from a junior analyst given a few hours.

## What's in this folder

- [`recommendation.md`](deliverable/recommendation.md) — the named-product recommendation with pricing math
- [`comparison.md`](deliverable/comparison.md) — 5-product comparison table with feature/price/UX axes
- [`sources.md`](deliverable/sources.md) — citation list with URLs
- [`research/`](deliverable/research/) — agent's working notes from reading pages
- [`decisions/`](deliverable/decisions/) — ADRs explaining recommendation choices
- [`README.md`](deliverable/README.md) — the agent's own readme
- [`grade.json`](grade.json) — structural verdict + counts
- [`label.json`](label.json) — `success-shipped`
- [`receipt.json`](receipt.json), [`summary.json`](summary.json), [`cost.json`](cost.json), [`transcript.jsonl`](transcript.jsonl)

## What this entry doesn't claim

Citation validity is the open question. STRUCTURAL_PASS asserts 33 distinct URLs are cited and that the cite tags appear inline in `recommendation.md` and `comparison.md`. It does **not** assert that those URLs exist, that they say what the agent quoted from them, or that the pricing numbers are accurate as of run date.

For an external reader sample-grading this output, the easiest thing to check first is the URL existence (do they 404?). After that, spot-check 3-5 specific factual claims against the cited URL — if the agent says "1Password Business is $7.99 user/month per the pricing page" and the page actually says that as of run date, the citation is valid; if the page says something different, the agent fabricated.

This is the highest-value hand-grading step still pending across the published microbench entries. See `findings.md` for the full list of hand-rating placeholders.

## Comparison

The Coder-Next entry next door [(`../Qwen3-Coder-Next-AWQ/`)](../Qwen3-Coder-Next-AWQ/) is a **STRUCTURAL_FAIL** — none of the required files exist. Same task spec, same input, same harness config (modulo model). 27B drives the workflow; Coder-Next gets stuck reading sources without producing structured output.
