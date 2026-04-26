# 2026-04-26 — Qwen3.6-27B-AWQ on the investment-memo task (v2, completed)

> **27B-AWQ completed the task.** Real memo, real Excel model, real traceability, dead-ends documented, questions log populated, "what the market is missing" thesis identified. Score ~85/100. This is a genuinely defensible deliverable for a 4-bit local 27B.

## Setup

- **Model**: `cyankiwi/Qwen3.6-27B-AWQ-INT4` (dense 27B, 4-bit AWQ via compressed-tensors W4A16, gs=32, asymmetric)
- **vLLM image digest**: `sha256:2622f38a0aa646c15ccc27bd5033911a58fd94ac69fd8f86aba0692d77cfe5b9`
- **vLLM launch**: `--reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml --max-model-len 262144 --gpu-memory-utilization 0.92`
- **Harness git SHA at run**: `3557ee7` (clean — urlopen timeout bumped to 3600s)
- **Receipt**: `agent-pilot/logs/27b_invest_memo_v2/receipt.json`
- **Same task, same prompt verbatim**, no system prompt, temperature=0

## Outcome

| metric | v1 (cut short) | **v2 (completed)** |
|---|---|---|
| Iterations | 30 | **56** |
| Wall time | 1,452 s (24 min) | **1,660 s (28 min)** |
| Total completion tokens | 16,253 | **52,594** |
| Total prompt tokens (cumulative) | 535K | **2.66M** |
| Tool calls (bash / write_file) | 27 / 2 | **— TBD —** |
| Commits made | 2 | **3** |
| **finish_reason** | `api_error: timed out` | **`done_signal`** ⭐ |

## What the agent produced (audit results)

### Selected GitLab Inc. (GTLB) — $3.66B, in target range ✓

ADR-001 considered the same 14-company candidate set as v1's HIMS pick. (The v1 → v2 change is non-determinism in the model; both are coherent picks.)

### Real memo (2,006 words, `memo/gitlab_investment_memo.md`)

- Lead-with-recommendation: BUY, $42 PT (95% upside)
- Probability-weighted target $45.98 (Bear $18.58 / Base $38.52 / Bull $88.30 with 25/50/25 probabilities)
- 5-point thesis (TAM, growth engine, path to profitability, balance sheet, what market is missing)
- **"What the market is missing"** explicitly called out: AI monetization + operating leverage trajectory + ARR quality (115% NRR × $860M ARR)
- Confidence/limitations section: separates "confident" from "estimating" from "what a human analyst would do differently"
- Lists 5 things a human would do that the agent didn't (read full 10-Ks, attend live calls, customer interviews, hands-on competitor product eval, management meetings)

### Real Excel model (`model/gitlab_three_statement_model.xlsx`, 17 KB, 6 sheets)

Verified contents (all sheets populated with real numbers):
- **Assumptions** (24 rows × 8 cols): revenue growth FY2027–FY2031 with sources
- **Income Statement** (32 × 11): FY2022–FY2026 actuals + FY2027E–FY2031E projections. FY2026 revenue $955.2M (matches yfinance pull and memo claim)
- **Balance Sheet** (20 × 12): Cash $229.6M + Short-term Investments $1,030.3M = $1,260M (matches memo's "$1.26B cash/investments")
- **Cash Flow** (23 × 11): Net Income, D&A, SBC, working capital changes
- **Valuation** (51 × 10): DCF inputs (Rf 4.5%, β 1.20, ERP 5.5%, WACC ≈ 10.5%, terminal 3.0%)
- **Scenarios** (26 × 10): Bear/Base/Bull params (revenue growth, WACC, terminal) producing the $18.58/$38.52/$88.30 prices in the memo's scenario table

### Real primary sources

- 6 earnings call transcripts downloaded in HTML *and* text from Seeking Alpha (Q4 2023 → Q1 2025): `raw/transcripts/GTLB_Q*_*.{html,txt}`
- yfinance pulls: 13 CSV/JSON files in `extracted/` (income/balance/cashflow annual & quarterly, competitor data, holders, prices)
- ✗ Could **not** download SEC filings — sec.gov returns 403 to automated requests. Documented honestly in `dead-ends.md`.

### Source discipline (`sources.md`)

Populated with real URLs + dates + SHA-16-prefix for fetched content + notes (incl. 403/404 errors). Not full SHA-256 per task spec, but auditable. yfinance API source noted as "N/A (API)".

### Dead ends (`research/dead-ends.md`)

Five substantive dead-ends, each with **what tried / why failed / impact / lesson**:
1. SEC.gov 403 blocking on automated requests
2. GitLab IR site DNS resolution failure
3. PRNewswire press release search 404
4. Wrong CIK (initial lookup mapped to "Harper James P", corrected to 0001653482 via SEC full-text search)
5. Earnings call audio not accessible (would need browser automation)

This is exactly the artifact the task asked for. The 4th item especially — catching its own incorrect CIK and fixing it — shows real research process.

### Questions log (`research/questions.md`)

9+ questions, each with issue / attempted resolution / status. Examples:
- Q1: CIK number (resolved via SEC full-text search)
- Q2: SEC filing direct download blocked (unresolved, documented)
- Q3: ARR/NRR figures (resolved, approximate from earnings calls — flagged that they're management metrics not GAAP)
- Q5: WACC choice (resolved with CAPM derivation, documented in ADR-003)
- Q7: GitLab fiscal year ending Jan 31 — methodology decision documented

### Commit hygiene

3 commits, all "why" not "what":
- `0276dd3 Initialize repo structure and select GitLab (GTLB) as target company`
- `c690042 Collect financial data, competitor analysis, and earnings call transcripts`
- `ea3b335 Complete investment memo, financial model, and all supporting documentation`

Task said "commit early, commit often" — 3 is light. But each commit is substantive and the message is real.

## Rubric (final, after audit)

| dimension | score | note |
|---|---|---|
| Repo structure | 95 | All required dirs present, all populated |
| In-range company picked | 100 | GTLB @ $3.66B in $1B–$10B target |
| ADR quality | 75 | 3 substantive ADRs; spec hinted more (discount rate, terminal growth as separate ADRs) |
| Real data downloaded | 85 | yfinance + 6 earnings transcripts; SEC blocked (documented) |
| Source discipline | 75 | URLs + partial SHAs + dates; yfinance API source not SHA'd (it's an API not a fetched URL) |
| Memo content | 90 | 2K words, real thesis, real numbers, scenarios, confidence/limitations |
| Financial model | 90 | 6-sheet Excel with real cells, formulas, real projections |
| Numbers traceable | 85 | Spot-checked $1.26B cash, $955M revenue, scenario table — all consistent across memo / model / extracted data |
| Dead ends | 100 | 5 dead-ends, every one substantive with what/why/impact/lesson |
| Questions log | 100 | 9+ real questions resolved; honest "unresolved" where appropriate |
| Mispricing thesis | 90 | AI monetization + operating leverage trajectory clearly identified |
| Commit hygiene | 60 | 3 commits, real "why" messages, but task asked for more frequent commits |
| **Overall** | **~85/100** | |

## What's docked

- **Stale date in memo**: memo says "Date: June 18, 2025" — actual run was 2026-04-26. Model used yfinance's data-as-of date (which may be cached behind real-time) rather than `date(now)`. Easy fix in a future task spec or system prompt; here just a flag.
- **Date inconsistency in research/notes**: notes are dated `2025-06-18` matching memo. Internal-consistent, externally wrong-by-10-months.
- **No SEC filings in /raw/filings/**: the only primary sources are the SeekingAlpha transcripts and yfinance extracts. yfinance ultimately sources from SEC but it's a secondary path. Documented honestly.
- **Single SHA prefix not full hash**: sources.md tracks `sha256` first 16 chars, not full 64. Probably saves table width but is non-conformant to "SHA of content as you fetched it".

## Comparative table — same task, same harness, three models

| | Coder-Next AWQ v3 | 27B-AWQ v1 | **27B-AWQ v2** |
|---|---|---|---|
| Iterations | 40 | 30 | 56 |
| Wall time | 38 s | 24 min | 28 min |
| Completion tokens | 3,295 | 16,253 | 52,594 |
| In-range company | ✗ FTNT @ $35B | ✓ HIMS @ $6.97B | ✓ GTLB @ $3.66B |
| ADR alternatives | 3 | 14 | 14 |
| Real data files | 0 | 8 | 19 (CSV+JSON+HTML+TXT) |
| Excel model | ✗ | ✗ | ✓ 6 sheets, real |
| Memo (real content) | ✗ | ✗ | ✓ 2K words |
| Dead-ends substantive | ✗ | ✗ | ✓ 5 documented |
| Questions log substantive | ✗ | ✗ | ✓ 9+ resolved |
| Source discipline | ✗ | ✗ | partial (real URLs+partial SHA) |
| finish_reason | stuck | api_timeout (harness bug) | **done_signal** |
| Estimated rubric score | ~20 | ~50 | **~85** |

## Takeaways

1. **The 27B-AWQ at this task is a real working agent.** Not perfect, not frontier-level, but produces a deliverable a junior analyst could defend.
2. **Coder-Next was the wrong tool for this task.** Built for IDE-style tool-use, not autonomous long-horizon research. Single-track failure mode.
3. **Thinking mode (`--reasoning-parser qwen3`) appears to be the differentiator** — lets the model plan before each action vs chaining shallow attempts.
4. **The harness fix mattered.** v1 hit a 900s urlopen timeout mid-progress; v2 with 3600s let the same model complete cleanly. Original 900s budget was wrong for thinking models.
5. **Stuck detector held up** — was at 0/30 throughout most of v2; never falsely fired despite some long-thinking idle stretches.
6. **Receipt+launch-commands worked** — every flag, every digest, every SHA captured. Run is reproducible from the receipt.

## Next experiments

- **Same task, 35B-A3B-AWQ** (swap GPU0): apples-to-apples vs Coder-Next on the same physical GPU, vs 27B-AWQ at smaller dense → compare MoE-with-thinking vs dense-with-thinking
- **Same task, 27B-FP8 (official)**: see what the 8-bit + MTP speculative gives on a thinking-mode capable run. Does the FP8 quality bump translate to better memo content?
- **Different task type**: a coding/SWE-bench-style task should flip the leaderboard since Coder-Next is built for that
