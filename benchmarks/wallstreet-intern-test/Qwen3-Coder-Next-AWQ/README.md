# Wallstreet Intern Test — Qwen3-Coder-Next-AWQ

**Subject:** DocuSign, Inc. (`DOCU`)
**Recommendation:** **BUY**
**Audit date:** 2026-04-26
**Auditor:** Qwen3-Coder-Next AWQ-4bit (Cyankiwi quantization), MoE 80B / 3B active, no thinking-mode
**vLLM config:** `--max-model-len 262144`, `--temperature 0.0`, `--enable-auto-tool-choice --tool-call-parser qwen3_coder`
**Wall-clock:** 11 min, 95 iterations, 46K completion tokens
**Run name:** `coder_invest_memo_v5` (the *cherry-picked successful run* of three; see "Variance" below)

## Read this first

This is a **successfully completed memo** from a model that succeeded only 1 of 3 attempts. The deliverable: a 10.6 KB three-statement model, full memo, raw filings, extracted data, sources with SHAs. Tagged a release at end-of-run.

For Coder-Next, "successfully completed" comes with a separate caveat that didn't apply to the 27B entry: **the verdict (the BUY recommendation here) is at the same kind of risk as the verdicts on Coder-Next's PR-audit entries.** The PR-audit benchmark showed that single-shot Coder-Next output can be confidently wrong with fabricated supporting evidence (see [`../../dreamserver-1-pr-audit/Qwen3-Coder-Next-AWQ/README.md`](../../dreamserver-1-pr-audit/Qwen3-Coder-Next-AWQ/README.md)). That risk extends to "BUY" calls in investment memos. Treating this BUY as Coder-Next's actual investment recommendation without verification is the same trap that made the PR-audit verdict wrong 2 of 3 times.

## Read in this order

If you have **5 minutes**: read `memo/`'s primary file for the recommendation and core thesis.

If you have **20 minutes**: read the memo, then `analysis/` (especially anything labeled "sell-side miss" or "scenarios"), then `decisions/` for the ADR records.

For the audit chain: claims in the memo should trace through `extracted/` → `model/docusign_three_statement_model.xlsx` → memo. Quotes trace to line-numbered transcript text in `extracted/transcripts/`. External claims resolve via `sources.md`.

## Variance

| run | wall | iters | finish | shipped? | notes |
|---|---|---|---|---|---|
| `coder_invest_memo_v5` | 11 min | 95 | done_signal ⭐ | yes ← this entry | DocuSign BUY, full audit trail |
| `coder_invest_memo_v6` | 2 min | 37 | stuck (no workspace change) | no | scaffold-and-stop early |
| `coder_invest_memo_v7` | 1 min | 63 | stuck | no | scaffold-and-stop earlier |

1 of 3 runs shipped. The other two stalled in the documented "Coder-Next scaffold-and-stop" pattern that the consolidated 2026-04-26 grid first surfaced (commit `be9997b` in the source bench repo).

## Repository layout

```
memo/                  PM-facing memo (markdown source)
model/                 Three-statement model (XLSX, 10.6 KB)
raw/                   Original primary sources
extracted/             Parsed data + extraction scripts
analysis/              Sell-side-miss test, scenarios
research/              Working notes, questions, dead-ends
decisions/             ADRs for non-obvious choices
sources.md             URLs + timestamps + SHAs
tool-log.md            Tool calls in order
```

## Specific gaps vs the cloud entries

Compared to `Opus-4.7/` and `GPT-5.5/` on this same benchmark:

- **No `key-outputs.ndjson`, `checks-inspect.ndjson`, or `formula-error-scan.ndjson`** — Coder-Next didn't produce the machine-readable workbook-verification artifacts the cloud entries did.
- **No board-of-advisors-presentation follow-on**. Coder-Next has separately run board-deck tasks in the source bench (`coder_board_pres_v1` etc., 3/3 successful per the consolidated 2x3x3 grid) but those aren't packaged here.
- **No PDF rendering** — markdown source only.
- **Verdict reliability caveat** (above): the memo's BUY rests on Coder-Next's interpretation of DocuSign's filings, and Coder-Next's interpretive accuracy at single-shot is the variance-dominated thing the PR-audit benchmark documented.

## Reproducibility

Source-of-truth is `agent-pilot/logs/coder_invest_memo_v5/` in the bench repo. Receipt + transcript + workspace tarball live there.

```bash
python3 agent-pilot/harness.py replay_coder_invest_memo_v5 \
  agent-pilot/task_investment_memo.md \
  --model qwen3-coder-next-awq --port 8001 \
  --temperature 0.0
```

v5 ran at temperature 0.0. Later experiments (PR-audit family) shifted to temperature 0.3 because of the deterministic-loop-trap finding; for this memo task at the time, 0.0 was the convention. vLLM bf16 paths aren't bitwise-deterministic; expect divergence.
