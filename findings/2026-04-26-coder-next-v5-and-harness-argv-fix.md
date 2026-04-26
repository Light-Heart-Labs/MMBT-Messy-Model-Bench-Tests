# 2026-04-26 — Coder-Next v5 (post argv-length fix) — completed deliverable

> Coder-Next went from ~20/100 (v3, stuck) → ~80/100 (v5, completed) on the *same task with the same model* after fixing a harness bug. This is a story about how harness bugs can silently mask agent capability, plus a comparison vs 27B-AWQ v2.

## What changed in the harness

`docker_exec` was passing the agent's bash command as an argv element to `bash -c`:

```python
full = ["docker", "exec", "-w", workdir, SANDBOX, "bash", "-c", cmd]  # OLD
```

When a model emitted a long heredoc (e.g. a python script for downloading SEC filings), the `cmd` string blew Linux's ~128 KB argv+envp limit and the whole `subprocess.run` call failed with `OSError: [Errno 7] Argument list too long`. Hit this on Coder-Next v4 at iter 38.

Fixed by piping the command via stdin:

```python
full = ["docker", "exec", "-i", "-w", workdir, SANDBOX, "bash", "-s"]  # NEW
p = subprocess.run(full, input=cmd, capture_output=True, text=True, timeout=timeout)
```

Sanity-checked with a 200 KB synthetic command (rc=0). No argv constraint.

This bug was probably affecting Coder-Next runs all along, since Coder-Next is biased toward emitting big bash heredoc tool calls vs. the more modular tool calls a thinking-mode model tends to make. Dies silently or stalls when a "real" tool call fails to dispatch.

## Setup (v5)

- Model: `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` (MoE 80B / 3B activated, 4-bit AWQ)
- vLLM: `--enable-auto-tool-choice --tool-call-parser qwen3_coder --max-model-len 262144 --gpu-memory-utilization 0.92`, no reasoning parser
- Harness git SHA at run: post argv-length-fix commit
- Receipt: `agent-pilot/logs/coder_invest_memo_v5/receipt.json`

## Outcome

| metric | v3 (stuck-detected) | v4 (argv-fail) | **v5 (completed)** |
|---|---|---|---|
| Iterations | 40 | 38 | **95** |
| Wall time | 38 s | ~200 s (crashed) | **645 s (10.7 min)** |
| Total completion tokens | 3,295 | 10,803 | **46,102** |
| Tool calls (bash / write_file / done) | 38 / 2 / 0 | – | **80 / 14 / 1** |
| Commits made (inner repo) | 0 | – | **19** |
| **finish_reason** | stuck-detector | OSError argv | **`done_signal`** ⭐ |

## What v5 produced

**Picked DocuSign (DOCU)** at $8.98B mkt cap → in target range ($1B–$10B). ✓

**19 commits in the inner repo**, all "why" not "what". A few examples:
- `b3c38cb Document WACC selection: 9.0% chosen over 8.93% calculated for margin of safety`
- `5c6808f Document terminal growth selection: 3% chosen for sustainable growth in agreement automation market`
- `7e53f3b Document valuation multiple selection: EV/Revenue 6.4x chosen over P/E for growth company`

**Real SEC filings downloaded** (this is the breakthrough — earlier 27B v1 was 403-blocked from SEC):
- `10-K_20260318_full.html` — 2.0 MB **real iXBRL/Workiva-tagged 10-K**
- `10-Q_20250606_full.html` — 1.2 MB
- `10-Q_20250905_full.html` — 1.5 MB
- `10-Q_20251205_full.html` — 1.5 MB
- (each filing also pulled an EDGAR landing-page wrapper at 70 KB; the agent bundled both)

Verified the 10-K _full.html is genuine XBRL: starts with proper Workiva platform header and `xmlns` declarations for `dei`, `us-gaap`, `srt`, etc.

**Real Excel model** (`docusign_three_statement_model.xlsx`): 3 sheets — Income Statement (30×5), Balance Sheet (49×5), Cash Flow (35×5). No separate Assumptions / Valuation / Scenarios sheets, but the Scenarios analysis is in the memo as a markdown table referencing the model.

**Real memo** (1,296 words):
- BUY at $72 PT (30% upside from $55.40)
- Bear/Base/Bull scenarios ($77.48 / $104.82 / $132.36 — note: an inconsistency, the base case DCF is $104 but the published PT is $72 — the agent didn't reconcile)
- Multiples analysis vs Adobe (EV/Revenue 6.4x vs 4.1x, EV/EBITDA 8.5x vs 10.2x, P/E 31.2x vs 14.3x)
- Risk summary table (probability × impact × rating)
- "Confidence and Limitations" section with what's certain, what's estimated, what's uncertain, and explicit model limitations

**4 ADRs** — all granular per task spec:
- 001 Company Selection (UiPath vs DocuSign — only 2 alternatives, vs 27B's 14)
- 002 Multiple Selection (EV/Revenue 6.4x chosen over P/E)
- 003 Discount Rate (WACC 9.0% chosen vs 8.93% calculated, "for margin of safety")
- 004 Terminal Growth (3% for agreement automation market)

**4 dead-ends documented** with what tried / why failed / resolution / lesson:
- DocuSign IR site DNS unreachable
- Earnings call transcripts not freely available
- Customer metrics (NRR, CAC, LTV) not disclosed
- Detailed competitive pricing not public

## Comparison vs 27B-AWQ v2 — same task, same harness

| dimension | Coder-Next v5 | 27B-AWQ v2 |
|---|---|---|
| Repo structure | 90 (`{notes}` literal-dir bug present) | 95 |
| In-range company | 100 (DOCU $8.98B) | 100 (GTLB $3.66B) |
| ADR granularity | **80** (4 ADRs covering each non-obvious choice) | 75 (3 ADRs, some choices folded together) |
| ADR alternatives depth | 65 (2 alts in 001) | 90 (14 alts in 001) |
| Real primary data | **80** (real SEC iXBRL 10-K + 3 10-Qs) | 85 (yfinance API + 6 SeekingAlpha transcripts; SEC blocked) |
| Source discipline | 75 | 75 |
| Memo content | 75 (1.3K words; PT-vs-DCF inconsistency) | 90 (2K words; coherent) |
| Financial model | 70 (3 sheets) | 90 (6 sheets incl. Assumptions/Valuation/Scenarios) |
| Numbers traceable | 75 | 85 |
| Dead ends | 80 (4 substantive) | 100 (5 substantive with deeper analysis) |
| Questions log | 90 (5 substantive Qs) | 100 (9+ with status flags) |
| Mispricing thesis | 75 (less explicit) | 90 |
| **Commit hygiene** | **95 (19 commits, all "why")** | 60 (3 commits) |
| Wall time | 10.7 min | 28 min |
| Completion tokens | 46K | 53K |
| **Overall** | **~80/100** | **~85/100** |

These are now substantively comparable. Coder-Next is *better* on commit hygiene (19 vs 3) and ADR granularity (4 vs 3). 27B is *better* on memo depth, ADR alternatives breadth, financial model scope, and dead-ends/questions thoroughness.

The v3 → v5 swing is **3.5×** in score on the same task with the same model — almost entirely attributable to the harness argv-length bug. Worth taking seriously as a methodological lesson.

## Determinism caveat

Both runs used `temperature=0`. Coder-Next v3 picked Fortinet ($35B, out of range) and got stuck on curl. Coder-Next v5 picked DocuSign ($8.98B, in range) and completed cleanly. Same model, same prompt, same vLLM container.

Possible drivers of the divergence:
1. The harness argv-length bug was silently truncating tool calls in v3 too, before the explicit OSError surfaced in v4
2. vLLM bf16 arithmetic isn't bitwise-deterministic across runs even at T=0 (kernel batch reordering, cuBLAS workspaces, etc.)
3. KV cache state from prior unrelated requests on the same vLLM instance might subtly perturb early-context routing in MoE models

Implication: **N=1 is not enough** for confident model comparisons. Future runs should be N≥3 per (model × task) and report mean + range, not single scores.

## Three-way table — same task, same harness (post-fix), same vLLM image, same workspace structure

| | **Coder-Next v3** | **Coder-Next v5** | **27B-AWQ v2** |
|---|---|---|---|
| Iterations | 40 | 95 | 56 |
| Wall time | 38 s | 645 s | 1,660 s |
| Completion tokens | 3,295 | 46,102 | 52,594 |
| In-range company | ✗ FTNT $35B | ✓ DOCU $8.98B | ✓ GTLB $3.66B |
| Real SEC filings | ✗ | ✓ 4 iXBRL files | ✗ (blocked) |
| Real Excel model | ✗ | ✓ 3 sheets | ✓ 6 sheets |
| Memo content | ✗ | ✓ 1.3K words | ✓ 2.0K words |
| Bear/Base/Bull scenarios | ✗ | ✓ | ✓ |
| Confidence/limitations | ✗ | ✓ | ✓ |
| ADRs | 1 (placeholder) | 4 substantive | 3 substantive |
| Dead-ends | template | 4 real | 5 real |
| Questions log | template | 5 real | 9+ real |
| Commits | 2 placeholder | 19 substantive | 3 substantive |
| `{notes}` literal-dir bug | yes | yes | no |
| finish_reason | stuck | done_signal | done_signal |
| Estimated rubric | ~20 | ~80 | ~85 |

## Methodology notes added to repo posture

- **Argv-length is a real harness constraint.** Long tool calls must go via stdin. Documented in the docker_exec docstring.
- **Determinism is approximate.** Plan for N≥3 runs per (model × task) for confident scoring.
- **Coder-Next is more capable than the v3 result suggested.** v3's failure mode now reads as "harness bug + maybe one bad early decision" rather than "model can't do agent work".
- **The `{notes}` literal-dir bug is a Coder-Next pattern** — it shells out `mkdir -p path/{a,b,c}` without realizing brace expansion needs unquoted shell. 27B doesn't make this mistake.

## Artifacts

- v3 (stuck): `agent-pilot/logs/coder_invest_memo_v3/`
- v4 (argv-fail partial): `agent-pilot/logs/coder_invest_memo_v4_partial/`
- **v5 (completed)**: `agent-pilot/logs/coder_invest_memo_v5/`
