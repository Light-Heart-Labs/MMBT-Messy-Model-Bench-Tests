# 2026-04-26 — Qwen3.6-27B-AWQ on the investment-memo task (v1, harness timeout)

## Setup

- **Model**: `cyankiwi/Qwen3.6-27B-AWQ-INT4` (dense 27B, 4-bit AWQ via compressed-tensors W4A16, gs=32, asymmetric)
- **Server**: vLLM 0.19.1 on GPU1, port 8000, `--reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_xml`, `--max-model-len 262144`, `--gpu-memory-utilization 0.92`
- **Harness git SHA at run**: `a1d59fb` (dirty: True — I had unstaged harness edits when I launched, fixed in next commit)
- **vLLM image digest at run**: `sha256:2622f38a0aa646c15ccc27bd5033911a58fd94ac69fd8f86aba0692d77cfe5b9`
- **Task**: `agent-pilot/task_investment_memo.md`, sha256 `02f48c90...`
- **Receipt**: `agent-pilot/logs/27b_invest_memo_v1/receipt.json`

## Outcome

| metric | value |
|---|---|
| Iterations | 30 |
| Wall time | 1,452 s (24 min) |
| Total completion tokens | 16,253 |
| Total prompt tokens | 535,923 (cumulative) |
| Tool calls (bash / write_file) | 27 / 2 |
| Commits made | 2 |
| **finish_reason** | `api_error: timed out` (single-turn vLLM call exceeded the 900s urlopen budget; not a model stall) |

## What the 27B actually did

### Picked HIMS (Hims & Hers Health) — *in target range*, $6.97B mkt cap

ADR-001 considered **14 alternatives** with real market caps from a yfinance pull:
C3.ai ($1.26B), Asana ($1.52B), Appian ($1.65B), Upstart ($3.21B), CarGurus ($3.39B), GitLab ($3.66B), BILL ($3.68B), SentinelOne ($4.85B), Opendoor ($5.28B), UiPath ($5.43B), HIMS ($6.97B), Celsius ($8.89B), SNAP ($9.54B), Instacart ($9.98B). Selected HIMS for: market cap fit, profitability transition (recently GAAP-positive), regulatory dynamics (FDA, telehealth), data availability, mispricing-around-margin-trajectory thesis.

### Used the right tools

`python3 + yfinance + pandas` for the financial data pull. (Coder-Next on the same task used `curl + grep` and never got out of an empty-response loop.)

### Produced real artifacts

```
raw/hims_income_annual.csv
raw/hims_income_quarterly.csv
raw/hims_balance_annual.csv
raw/hims_balance_quarterly.csv
raw/hims_cashflow_annual.csv
raw/hims_cashflow_quarterly.csv
raw/hims_info.json
```

Sample (Normalized EBITDA from `hims_income_annual.csv`, in millions):

| 2021 | 2022 | 2023 | 2024 | 2025 |
|---:|---:|---:|---:|---:|
| n/a | (61.2) | (19.9) | 79.0 | 155.7 |

Real numbers, real time-series. The data made it from yfinance into the repo as actual primary material.

### Commit hygiene

Only 2 commits, but the messages are real "why" reasons:
- `90498e6 Initialize repo structure with README and directory layout`
- `b7ce3ba Select HIMS as target company - telehealth platform with B mcap, profitability transition, and interesting regulatory dynamics`

## Where it stopped (and why this is a harness bug, not a capability ceiling)

The harness uses `urllib.request.urlopen(req, timeout=900)`. A single vLLM call exceeded 900 s — almost certainly because the 27B is a thinking-mode model and was reasoning through a complex step (likely the next phase: parsing the data into a model). Last 5 bash commands were fresh python scripts attempting different data sources — *not* a stuck loop. The stuck detector (workspace state hash) showed 0–3 no-progress iters at the time of crash.

**This is a harness bug:** 900 s is too short for a thinking model on hard tasks. Bumping to 3600 s in the next harness commit.

## Comparison vs Coder-Next on the same task

| | Coder-Next (v3) | 27B-AWQ (v1) |
|---|---|---|
| Iterations | 40 (stuck-detected) | 30 (timeout) |
| Wall time | 38 s | 1,452 s |
| Completion tokens | 3,295 | 16,253 |
| In-range company | ✗ FTNT @ $35B | ✓ HIMS @ $6.97B |
| ADR alternatives | 3 | 14 |
| Real data files | 0 | 7 CSV + 1 JSON |
| Tool choice | curl+grep | python+yfinance+pandas |
| `{notes}` literal-dir bash bug | yes | no |
| Failure mode | stuck in curl loop | progress-while-thinking, hit harness timeout |

The 27B is **substantively more capable** at this task than Coder-Next at the same precision, despite being a smaller dense model vs an 80B-active-3B MoE. Likely drivers: (1) thinking mode lets it plan before each tool call rather than chaining shallow attempts, (2) better tool selection — it actually used the python libs in the sandbox, (3) thinks before declaring failure, so doesn't fall into single-track loops.

## Provisional rubric score

| dimension | 27B v1 |
|---|---|
| Repo structure | 80 |
| ADR quality | 85 |
| Real company in range | 100 |
| Real data downloaded | 80 |
| Tool selection | 100 |
| Commits with *why* | 60 (only 2 of them) |
| Memo content | 0 (didn't get there) |
| Financial model | 0 (didn't get there) |
| Source discipline | 0 (sources.md empty) |
| **Overall (provisional, run was cut short)** | **~50/100** |

The ceiling is clearly higher — it was on track to do real work when the timeout hit. Re-run with longer timeout will tell us where it actually plateaus.

## Harness change made for v2

```diff
-        with urllib.request.urlopen(req, timeout=900) as r:
+        with urllib.request.urlopen(req, timeout=3600) as r:
```

60-minute per-call timeout. The stuck detector (30 iters of no workspace change) is still the primary terminator for "model is stalled" — the urlopen timeout was only meant to be a backstop for hung connections, not a per-turn budget. 3600 s is generous enough that even very long thinking sessions complete.

## Artifacts

- Receipt: `agent-pilot/logs/27b_invest_memo_v1/receipt.json`
- Transcript: `agent-pilot/logs/27b_invest_memo_v1/transcript.jsonl`
- Summary: `agent-pilot/logs/27b_invest_memo_v1/summary.json`
- Final workspace: `agent-pilot/logs/27b_invest_memo_v1/workspace_final.tar.gz`
