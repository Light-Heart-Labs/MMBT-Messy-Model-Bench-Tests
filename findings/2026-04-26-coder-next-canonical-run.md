# 2026-04-26 — Qwen3-Coder-Next-AWQ on the investment-memo task (canonical run)

> Coder-Next completed the investment-memo task end-to-end. Real iXBRL SEC filings, real Excel model, 4 granular ADRs, 19 real "why" commits, Bear/Base/Bull scenarios, confidence/limitations. Score ~80/100.

## Setup

- **Model**: `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` (MoE 80B / 3B activated, 4-bit AWQ via compressed-tensors)
- **vLLM image digest**: `sha256:2622f38a0aa646c15ccc27bd5033911a58fd94ac69fd8f86aba0692d77cfe5b9`
- **vLLM launch**: `--enable-auto-tool-choice --tool-call-parser qwen3_coder --max-model-len 262144 --gpu-memory-utilization 0.92` (no reasoning parser — Coder-Next is not a thinking model)
- **Harness git SHA at run**: post argv-length-fix commit
- **Receipt**: `agent-pilot/logs/coder_invest_memo_v5/receipt.json`
- **Task**: `agent-pilot/task_investment_memo.md` verbatim, no system prompt, `temperature=0`

## Outcome

| metric | value |
|---|---|
| Iterations | 95 |
| Wall time | 645 s (10.7 min) |
| Total completion tokens | 46,102 |
| Total prompt tokens (cumulative) | 4.65 M |
| Tool calls (bash / write_file / done) | 80 / 14 / 1 |
| Commits made (inner repo) | 19 |
| **finish_reason** | **`done_signal`** |

## What it produced

### Selected DocuSign (DOCU) — $8.98B, in target range ✓

ADR-001 only considered 2 alternatives (UiPath at $5.4B and DocuSign). Less thorough candidate selection than is ideal, but the chosen company is in range.

### Real iXBRL SEC filings ⭐

This is what makes the run credible:
- `10-K_20260318_full.html` — 2.0 MB **real iXBRL/Workiva-tagged 10-K**
- `10-Q_20250606_full.html` — 1.2 MB
- `10-Q_20250905_full.html` — 1.5 MB
- `10-Q_20251205_full.html` — 1.5 MB

(Each filing was bundled with a 70 KB EDGAR landing-page wrapper too — those are noise but the `_full.html` versions are genuine SEC filings with proper XBRL tagging.)

Notably: the 27B's run got 403-blocked from SEC.gov on the same task. Coder-Next either found a User-Agent that worked or accessed a path the 27B didn't try. Real primary-source advantage.

### Real Excel model (`docusign_three_statement_model.xlsx`, 3 sheets)

- **Income Statement** (30 × 5)
- **Balance Sheet** (49 × 5)
- **Cash Flow Statement** (35 × 5)

3 sheets vs the 27B's 6 — no separate Assumptions / Valuation / Scenarios sheets. The Scenarios analysis lives in the memo as a markdown table referencing the model.

### Real memo (1,296 words, `memo/docusign_investment_memo.md` — also rendered to HTML)

- BUY at $72 PT (30% upside from $55.40)
- Bear/Base/Bull scenarios ($77.48 / $104.82 / $132.36 with revenue growth + FCF margin assumptions)
- Multiples analysis vs Adobe (EV/Revenue 6.4x vs 4.1x, EV/EBITDA 8.5x vs 10.2x, P/E 31.2x vs 14.3x)
- Risk summary table with probability × impact × rating
- "Confidence and Limitations" section

**Inconsistency caught in audit**: the published 12-month PT is $72 (30% upside) but the base-case DCF in the same memo is $104.82 (89% upside). The agent never reconciled these. A real PM would catch this in 30 seconds.

### 4 granular ADRs

Exactly what the task spec hinted at — one per non-obvious choice:
- 001 Company Selection (DocuSign vs UiPath)
- 002 Multiple Selection (EV/Revenue 6.4x chosen over P/E "for growth company")
- 003 Discount Rate (WACC 9.0% chosen over 8.93% calculated "for margin of safety")
- 004 Terminal Growth (3% for agreement automation market)

### 4 dead-ends documented

- DocuSign IR site DNS unreachable
- Earnings call transcripts not freely available
- Customer metrics (NRR, CAC, LTV) not disclosed
- Detailed competitive pricing not public

Each entry has investigation / result / resolution / lesson. Substantive though shallower than the 27B's 5.

### Commit hygiene — strongest of any run

19 commits, all "why" not "what". Examples:
- `b3c38cb Document WACC selection: 9.0% chosen over 8.93% calculated for margin of safety`
- `5c6808f Document terminal growth selection: 3% chosen for sustainable growth in agreement automation market`
- `7e53f3b Document valuation multiple selection: EV/Revenue 6.4x chosen over P/E for growth company`

This is exemplary. The 27B made only 3 commits.

## Rubric score

| dimension | score | note |
|---|---|---|
| Repo structure | 90 | `{notes}` literal-dir bash bug recurred (Coder-Next-specific tic) |
| In-range company picked | 100 | DOCU @ $8.98B |
| ADR granularity | 80 | 4 ADRs covering each non-obvious choice |
| ADR alternatives depth | 65 | only 2 alts in 001 |
| Real primary data | 80 | 4 real iXBRL SEC filings |
| Source discipline | 75 | URLs + partial SHAs + dates |
| Memo content | 75 | 1.3K words; PT-vs-DCF inconsistency unreconciled |
| Financial model | 70 | 3 sheets (no Assumptions/Valuation/Scenarios sheet) |
| Numbers traceable | 75 | mostly traceable, but PT-vs-DCF mismatch |
| Dead ends | 80 | 4 substantive |
| Questions log | 90 | 5 substantive Qs resolved |
| Mispricing thesis | 75 | less explicit than 27B's |
| **Commit hygiene** | **95** | **19 commits, all real "why" messages** |
| **Overall** | **~80/100** | |

## What's docked

- **PT-vs-DCF inconsistency** — internal contradiction in the memo not reconciled
- **Date confusion** — memo dated `2024-10-03`, actual run was `2026-04-26`. Model anchored on training-data dates rather than `date(now)`.
- **`{notes}` literal-dir bug** — `mkdir -p path/{a,b,c}` with quoting that prevented brace expansion. Coder-Next-specific; 27B doesn't make this mistake. Catalogued as a model-distinguishing failure mode.
- **ADR-001 only had 2 alternatives** vs 27B's 14 — much less rigorous candidate selection.

## Comparison vs 27B-AWQ on the same task

| dimension | Coder-Next | 27B-AWQ |
|---|---|---|
| Repo structure | 90 | 95 |
| In-range company | 100 | 100 |
| ADR granularity | **80 (4)** | 75 (3) |
| ADR alternatives depth | 65 (2 alts) | **90 (14 alts)** |
| Real primary data | **80 (real SEC iXBRL)** | 85 (yfinance + transcripts; SEC blocked) |
| Memo content | 75 (1.3K, PT inconsistency) | **90 (2K, coherent)** |
| Financial model | 70 (3 sheets) | **90 (6 sheets)** |
| Numbers traceable | 75 | 85 |
| Dead ends | 80 (4) | **100 (5)** |
| Questions log | 90 (5) | **100 (9+)** |
| Mispricing thesis | 75 | **90** |
| **Commit hygiene** | **95 (19)** | 60 (3) |
| Wall time | 10.7 min | 28 min |
| Completion tokens | 46K | 53K |
| **Overall** | **~80/100** | **~85/100** |

These are substantively comparable. Coder-Next is *better* on commit hygiene and ADR granularity. 27B is *better* on memo depth, ADR alternatives breadth, financial model scope, and research-process artifacts (dead-ends/questions). Coder-Next finishes 2.6× faster.

## Artifacts

- `agent-pilot/logs/coder_invest_memo_v5/receipt.json` — full reproducibility receipt
- `agent-pilot/logs/coder_invest_memo_v5/transcript.jsonl` — every model turn + tool call
- `agent-pilot/logs/coder_invest_memo_v5/summary.json` — final state
- `agent-pilot/logs/coder_invest_memo_v5/workspace_final.tar.gz` — the agent's repo state at done()
