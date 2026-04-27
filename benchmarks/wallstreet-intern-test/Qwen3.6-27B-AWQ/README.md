# Wallstreet Intern Test — Qwen3.6-27B-AWQ

**Subject:** GitLab Inc. (`GTLB`)
**Recommendation:** **BUY** (12-month price target in the memo)
**Audit date:** 2026-04-26
**Auditor:** Qwen3.6-27B AWQ-INT4 (Cyankiwi quantization), dense, thinking-mode
**vLLM config:** `--max-model-len 262144`, `--temperature 0.0`, `--reasoning-parser qwen3 --tool-call-parser qwen3_xml`
**Wall-clock:** 27 min, 56 iterations, 32K completion tokens
**Run name:** `27b_invest_memo_v2` (the *cherry-picked successful run* of three; see "Variance" below)

## Read this first — what this entry is and isn't

This entry is a **successfully completed memo** from a model that succeeded on this task only 1 of 3 attempts. The deliverable is real: a memo with explicit BUY recommendation, a 17 KB three-statement XLSX model, raw filings, extracted data, ADRs, sources with SHAs, and dated research notes. Tagged a release at end-of-run. But the next two attempts at the same task with the same flags produced very different outcomes — see Variance.

## Read in this order

If you have **5 minutes**: read `memo/`'s primary memo file. It's the PM-facing document.

If you have **20 minutes**: read the memo, then `decisions/` for the ADR-style records of non-obvious choices (which company, what discount rate, which competitors), then `analysis/` for the sell-side-miss test.

If you want the full audit chain: every claim in the memo should trace through `extracted/` → `model/gitlab_three_statement_model.xlsx` → memo. Quotes from management trace to line-numbered transcript text in `extracted/transcripts/`. External citations resolve via `sources.md` (URL + SHA-256 + timestamp).

## Variance — read this before treating this entry as "27B's answer"

The model was run **three times** on the same task with the same flags:

| run | wall | iters | finish | shipped? | notes |
|---|---|---|---|---|---|
| `27b_invest_memo_v2` | 27 min | 56 | done_signal ⭐ | yes ← this entry | 2K-word memo, 6-sheet XLSX, 14-alternative ADR, full audit trail |
| `27b_invest_memo_v3` | 11 min | 40 | model_stopped (parser fault) | partial | substantive work but cut off mid-emission |
| `27b_invest_memo_v4` | 68 min | 45 | api_error: timed out | no | got stuck on a single ~1-hour inference call |

So 1 of 3 runs shipped a complete memo. v2 (this entry) is the published result. The other two are kept in the source bench repo as failure-mode evidence.

The relevant comparison: cloud LLMs (`Opus-4.7`, `GPT-5.5`) shipped on every attempt. Local 30B-class quantized models on this task do not.

## Repository layout

```
memo/                  PM-facing memo (markdown source + the thesis prose)
model/                 Three-statement model (XLSX)
raw/                   Original primary sources (filings, transcripts, press)
extracted/             Parsed/cleaned data from raw/, with extraction scripts
analysis/              Sell-side-miss test, competitive analysis, scenarios
research/              Working notes, dated, plus questions.md and dead-ends.md
decisions/             ADRs for non-obvious choices (company pick, discount rate, etc.)
sources.md             Every URL fetched with timestamp + SHA-256
tool-log.md            Tool calls in order, with one-line justifications
```

## Caveats specific to a thinking-mode local model

Compared to the cloud entries on this benchmark:

- **No board-of-advisors presentation follow-on.** The `wallstreet-intern-test` benchmark prompt itself is just the memo task; the `board-of-advisors-presentation/` folder under `GPT-5.5/` was a *separate follow-up task* (see `agent-pilot/task_board_presentation.md` in the source bench repo). 27B-AWQ has separately produced board-deck artifacts in the source bench (run `27b_board_pres_v1` etc.) but those are not packaged as part of this entry.
- **PDF rendering is the markdown source, not a typeset PDF.** The cloud entries include a styled PDF; 27B's run produced markdown only. The PDF generation step in the spec was not exercised.
- **Numbers are checkable but not all are checked.** The XLSX model has 6 sheets with formulas, but I have not run a comprehensive consistency-check script across them. The cloud entries include `model/key-outputs.ndjson`, `model/checks-inspect.ndjson`, and `model/formula-error-scan.ndjson` machine-readable verification artifacts; this entry does not have those files because the agent didn't generate them. The XLSX itself opens cleanly and the formulas are sane on inspection.

## Reproducibility

The exact harness invocation, vLLM container args, GPU snapshot, and task SHA are recorded in the run's `receipt.json` in the source bench repo (private to the maintainer).

To replay (rough):
```bash
python3 agent-pilot/harness.py replay_27b_invest_memo_v2 \
  agent-pilot/task_investment_memo.md \
  --model qwen3.6-27b-awq --port 8000 \
  --temperature 0.0
```

Note that v2 ran at temperature 0.0, before the deterministic-loop-trap discovery that informed our shift to temperature 0.3 for the later PR-audit task family. vLLM bf16 paths aren't bitwise-deterministic regardless; expect divergence.
