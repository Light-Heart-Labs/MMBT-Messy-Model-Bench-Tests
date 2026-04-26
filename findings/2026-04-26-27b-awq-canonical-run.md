# 2026-04-26 — Qwen3.6-27B-AWQ on the investment-memo task (canonical run)

> Qwen3.6-27B-AWQ completed the investment-memo task end-to-end. Real memo, real Excel model, real traceability, dead-ends documented, questions log populated, "what the market is missing" thesis identified. Score ~85/100. This is a genuinely defensible deliverable for a 4-bit local 27B.

## Setup

- **Model**: `cyankiwi/Qwen3.6-27B-AWQ-INT4` (dense 27B, 4-bit AWQ via compressed-tensors W4A16, gs=32, asymmetric)
- **vLLM image digest**: `sha256:2622f38a0aa646c15ccc27bd5033911a58fd94ac69fd8f86aba0692d77cfe5b9`
- **vLLM launch**: `--reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml --max-model-len 262144 --gpu-memory-utilization 0.92`
- **Harness git SHA at run**: `3557ee7`
- **Receipt**: `agent-pilot/logs/27b_invest_memo_v2/receipt.json`
- **Task**: `agent-pilot/task_investment_memo.md` verbatim, no system prompt, `temperature=0`

## Outcome

| metric | value |
|---|---|
| Iterations | 56 |
| Wall time | 1,660 s (28 min) |
| Total completion tokens | 52,594 |
| Total prompt tokens (cumulative) | 2.66 M |
| Tool calls (bash / write_file) | not enumerated |
| Commits made | 3 |
| **finish_reason** | **`done_signal`** |

## What it produced

### Selected GitLab Inc. (GTLB) — $3.66B, in target range ✓

ADR-001 considered **14 alternatives** with real market caps from a yfinance pull:
C3.ai ($1.26B), Asana ($1.52B), Appian ($1.65B), Upstart ($3.21B), CarGurus ($3.39B), GitLab ($3.66B), BILL ($3.68B), SentinelOne ($4.85B), Opendoor ($5.28B), UiPath ($5.43B), HIMS ($6.97B), Celsius ($8.89B), SNAP ($9.54B), Instacart ($9.98B). Selected GitLab for: market cap fit, growth engine, profitability transition, balance sheet strength, and an explicit "what the market is missing" thesis around AI monetization and operating leverage trajectory.

### Used the right tools

`python3 + yfinance + pandas` for the financial data pull. `requests + BeautifulSoup` for transcript scraping.

### Real memo (2,006 words, `memo/gitlab_investment_memo.md`)

- Lead-with-recommendation: BUY, $42 PT (95% upside)
- Probability-weighted target $45.98 (Bear $18.58 / Base $38.52 / Bull $88.30 with 25/50/25 probabilities)
- 5-point thesis (TAM, growth engine, path to profitability, balance sheet, what market is missing)
- **"What the market is missing"** explicitly called out: AI monetization + operating leverage trajectory + ARR quality (115% NRR × $860M ARR)
- Confidence/limitations section: separates "confident" from "estimating" from "what a human analyst would do differently"
- Lists 5 things a human analyst would do that the agent didn't (read full 10-Ks, attend live calls, customer interviews, hands-on competitor product eval, management meetings)

### Real Excel model (`model/gitlab_three_statement_model.xlsx`, 17 KB, 6 sheets)

- **Assumptions** (24 × 8): revenue growth FY2027–FY2031 with sources
- **Income Statement** (32 × 11): FY2022–FY2026 actuals + FY2027E–FY2031E projections. FY2026 revenue $955.2M (matches yfinance pull and memo claim)
- **Balance Sheet** (20 × 12): Cash $229.6M + Short-term Investments $1,030.3M = $1,260M (matches memo's "$1.26B cash/investments")
- **Cash Flow** (23 × 11): Net Income, D&A, SBC, working capital changes
- **Valuation** (51 × 10): DCF inputs (Rf 4.5%, β 1.20, ERP 5.5%, WACC ≈ 10.5%, terminal 3.0%)
- **Scenarios** (26 × 10): Bear/Base/Bull params (revenue growth, WACC, terminal) producing the $18.58/$38.52/$88.30 prices in the memo's scenario table

Numbers are traceable across artifacts: $1.26B cash matches Balance Sheet sum, $955M revenue matches Income Statement, scenario prices match between Scenarios sheet and memo's scenario table.

### Real primary sources

- 6 earnings call transcripts downloaded in HTML *and* text from Seeking Alpha (Q4 2023 → Q1 2025): `raw/transcripts/GTLB_Q*_*.{html,txt}`
- yfinance pulls: 13 CSV/JSON files in `extracted/` (income/balance/cashflow annual & quarterly, competitor data, holders, prices)
- ✗ Could not download SEC filings — sec.gov returns 403 to automated requests in this sandbox. Documented honestly in `dead-ends.md`.

### Source discipline (`sources.md`)

Populated with real URLs + dates + SHA-16-prefix for fetched content + notes (incl. 403/404 errors). Not full SHA-256 per task spec, but auditable. yfinance API source noted as "N/A (API)".

### Dead ends (`research/dead-ends.md`)

Five substantive dead-ends, each with **what tried / why failed / impact / lesson**:
1. SEC.gov 403 blocking on automated requests
2. GitLab IR site DNS resolution failure
3. PRNewswire press release search 404
4. Wrong CIK (initial lookup mapped to "Harper James P", corrected to 0001653482 via SEC full-text search)
5. Earnings call audio not accessible (would need browser automation)

The 4th item especially — catching its own incorrect CIK and fixing it — shows a real research feedback loop.

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

## Rubric score

| dimension | score | note |
|---|---|---|
| Repo structure | 95 | All required dirs present, all populated |
| In-range company picked | 100 | GTLB @ $3.66B in $1B–$10B target |
| ADR quality | 75 | 3 substantive ADRs; spec hinted at separate ADRs for discount rate, terminal growth |
| Real data | 85 | yfinance + 6 earnings transcripts; SEC filings blocked (documented) |
| Source discipline | 75 | URLs + partial SHAs + dates; yfinance API source not SHA'd |
| Memo content | 90 | 2K words, real thesis, real numbers, scenarios, confidence/limitations |
| Financial model | 90 | 6-sheet Excel with real cells, formulas, real projections |
| Numbers traceable | 85 | Spot-checked $1.26B cash, $955M revenue, scenario table — all consistent |
| Dead ends | 100 | 5 dead-ends, each substantive with what/why/impact/lesson |
| Questions log | 100 | 9+ real questions resolved; honest "unresolved" where appropriate |
| Mispricing thesis | 90 | AI monetization + operating leverage trajectory clearly identified |
| Commit hygiene | 60 | 3 commits, real "why" messages, but task asked for more frequent commits |
| **Overall** | **~85/100** | |

## What's docked

- **Stale date in memo**: memo says "Date: June 18, 2025" — actual run was 2026-04-26. Model used yfinance's data-as-of date rather than `date(now)`. Internal-consistent (research/notes are also dated 2025-06-18), externally wrong-by-10-months.
- **No SEC filings in /raw/filings/**: only primary sources are SeekingAlpha transcripts and yfinance extracts. yfinance ultimately sources from SEC but is a secondary path. Documented honestly.
- **Single SHA prefix not full hash**: sources.md tracks `sha256` first 16 chars, not full 64.

## Artifacts

- `agent-pilot/logs/27b_invest_memo_v2/receipt.json` — full reproducibility receipt
- `agent-pilot/logs/27b_invest_memo_v2/transcript.jsonl` — every model turn + tool call
- `agent-pilot/logs/27b_invest_memo_v2/summary.json` — final state
- `agent-pilot/logs/27b_invest_memo_v2/workspace_final.tar.gz` — the agent's repo state at done()
