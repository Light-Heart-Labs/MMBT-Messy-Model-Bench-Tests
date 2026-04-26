# Canonical agent deliverables

The actual repos the agents built during their successful runs. Preserved here for later analysis (rubric scoring, traceability spot-checks, content audits, comparison against other models).

## Contents

| dir | model | run | rubric score | mkt cap | finish_reason |
|---|---|---|---|---|---|
| `27b-awq-gtlb/` | Qwen3.6-27B-AWQ-INT4 | `27b_invest_memo_v2` | ~85/100 | GitLab (GTLB) $3.66B | done_signal |
| `coder-next-docu/` | Qwen3-Coder-Next-AWQ-4bit | `coder_invest_memo_v5` | ~80/100 | DocuSign (DOCU) $8.98B | done_signal |

Findings docs:
- `findings/2026-04-26-27b-awq-canonical-run.md`
- `findings/2026-04-26-coder-next-canonical-run.md`

Receipts (full reproducibility — vLLM args, image digest, harness SHA, hardware state, task SHA):
- `agent-pilot/logs/27b_invest_memo_v2/receipt.json`
- `agent-pilot/logs/coder_invest_memo_v5/receipt.json`

## How to inspect the agent's commit history

The agent's `.git` inside each deliverable has been renamed to `_agent_git_history` so the outer repo (this one) can track all the files plainly without treating it as a submodule. The history is fully intact — same SHAs, same refs, same objects.

To run git commands against the agent's history:

```bash
# View commit log
git --git-dir=27b-awq-gtlb/_agent_git_history log --oneline
git --git-dir=coder-next-docu/_agent_git_history log --oneline

# View a specific commit's diff
git --git-dir=27b-awq-gtlb/_agent_git_history show <sha>

# Or temporarily restore the .git name (don't forget to rename back, or git status will show the move)
cd 27b-awq-gtlb && mv _agent_git_history .git && git log --stat && mv .git _agent_git_history
```

For a one-shot analysis script that doesn't risk leaving things renamed:

```bash
GIT_DIR=27b-awq-gtlb/_agent_git_history git log --stat
```

## What you can analyze

For each deliverable:

- **The memo** — `memo/*.md` (and `*.html` for Coder-Next). Read for thesis quality, narrative coherence, internal consistency.
- **The financial model** — `model/*.xlsx`. Spot-check cells for traceability against `extracted/` and `raw/`.
- **The decision records** — `decisions/00*-*.md`. Audit alternatives considered, decision rationale, links to data.
- **The research process** — `research/notes/*.md`, `research/questions.md`, `research/dead-ends.md`. Read for transparency, honesty about what didn't work.
- **The primary sources** — `raw/` (filings, transcripts). Verify they're real content, not error pages.
- **The extracted data** — `extracted/*.csv|json`. Spot-check against the memo's claims.
- **The commit history** — via the GIT_DIR trick above. Read commit messages for "why" vs "what" quality.
- **Sources discipline** — `sources.md`. Check URLs are real, SHAs are present where applicable.
- **Self-audit artifacts** — `tool-log.md` (every tool call) and the receipt under `agent-pilot/logs/<run>/`.

## Side-by-side at a glance

|  | 27B-AWQ (GTLB) | Coder-Next (DOCU) |
|---|---|---|
| Iterations | 56 | 95 |
| Wall time | 28 min | 10.7 min |
| Completion tokens | 52,594 | 46,102 |
| Commits | 3 | 19 |
| ADRs | 3 | 4 |
| Memo word count | 2,006 | 1,296 |
| Excel sheets | 6 | 3 |
| Real SEC filings | ✗ (blocked, documented) | ✓ 4 iXBRL files |
| Earnings transcripts | ✓ 6 from SeekingAlpha | ✗ |
| Dead-ends documented | 5 | 4 |
| Questions log entries | 9+ | 5 |
| Bear/Base/Bull scenarios | ✓ | ✓ |
| Confidence/limitations | ✓ | ✓ |
| ADR-001 alternatives count | 14 | 2 |
| `{notes}` literal-dir bug | no | yes |
| PT-vs-DCF internal consistency | ✓ ($42 PT, $38.52 DCF base, $45.98 prob-weighted — all aligned) | ✗ ($72 PT vs $104.82 DCF base — unreconciled) |
