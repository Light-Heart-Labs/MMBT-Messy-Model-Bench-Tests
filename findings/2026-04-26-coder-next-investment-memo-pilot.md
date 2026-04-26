# 2026-04-26 — Coder-Next on the investment-memo task (pilot)

## Setup

- **Model**: `cyankiwi/Qwen3-Coder-Next-AWQ-4bit` (MoE 80B / 3B activated, 4-bit AWQ via compressed-tensors)
- **Server**: vLLM 0.19.1 on GPU0, port 8001, `--enable-auto-tool-choice --tool-call-parser qwen3_coder`, `--max-model-len 262144`, `--gpu-memory-utilization 0.92`, no reasoning parser
- **Harness**: `agent-pilot/harness.py` — vLLM tool-calling loop, Docker sandbox, full transcript logging, workspace state-hash stuck detector
- **Task**: `agent-pilot/task_investment_memo.md` — pick a $1B–$10B US public company, build a complete repo with /memo, /model, /raw, /extracted, /analysis, /research, /decisions; every claim traceable; commit early/often
- **Brain swap variable**: model is the variable; harness, task, sandbox image are constant
- **Temperature**: 0.0 (so results are largely deterministic given the same context)

## Two runs

### v2 (capped per-turn output bug)

- Caps: `max_tokens=200K` per turn, no per-iteration safety margin → vLLM HTTP 400 once context grew to ~60K and 200K of asked output didn't fit in the 262K window
- Outcome: 196 iters, 19,870 completion tokens, 8 min wall, **never picked a real company** — every ADR has `[Company Name]` placeholders
- Built complete directory scaffolding, wrote 6 ADRs, made 21 git commits with reasonable messages, but the content was all placeholder
- Last ~150 iters were near-no-op (47 ctok / 4.3s each, content_len=0): stuck issuing bash commands without producing files
- Tool distribution: 191 bash, 4 write_file (lopsided)

### v3 (harness fixed: dynamic max_tokens + stuck detector)

- `max_tokens` per request now `min(64K, max_model_len - last_prompt_tokens - 12K - 2K)` — prevents the 200K-vs-prompt-context overflow
- Stuck detector: SHA-1 of workspace file tree (excluding `.git/objects`) recomputed each iter; 30 consecutive iters without a state change triggers termination
- **Picked a real company**: Fortinet (FTNT). Considered Palantir and L3Harris in the ADR with reasoning
- **Caught its own constraint violation** in research/questions.md: noted FTNT mkt cap is ~$35B, outside the $1B–$10B target, but proceeded anyway instead of pivoting
- Got stuck on SEC EDGAR filing downloads. Last 10 iterations were all `curl -s -H "User-Agent: ..." https://sec.gov/Archives/...` with no inspection of what came back, no error handling, no pivot
- Stuck detector fired cleanly at iter 40 / 38 s wall, 3,295 completion tokens, 267k cumulative prompt tokens
- Made 2 real commits (vs v2's 21), both substantive
- Tool distribution: 38 bash, 2 write_file
- finish_reason: `stuck_no_workspace_change_for_30_iters`

## Diagnosis of Coder-Next at this task

**Can do**:
- Plan a structure, scaffold directories
- Pick a real target with reasoning over alternatives
- Write coherent ADRs
- Make sequential commits with decent messages
- Notice its own errors (logged the cap-range violation)

**Can't do**:
- Verify task constraints before committing to a path (picked $35B when asked for $1B–$10B)
- Recover from tool failures — kept hammering curl without inspecting output or trying alternatives
- Use the right tool for the job — sandbox had `python + requests + BeautifulSoup + sec-edgar-downloader` installed, agent used `curl + grep`
- Sustained long-horizon execution — stalled within ~40 iters even with no caps

**Failure mode**: single-track. When plan A doesn't yield results, the model doesn't pivot; it keeps trying minor variations of the same approach.

## Rough rubric score

| dimension | v2 | v3 |
|---|---|---|
| Repo structure | 70 | 60 |
| Picked a real company | 0 | 100 (with caveat: out of target range) |
| ADRs substantive | 20 | 60 |
| Commits | 21 (placeholder content) | 2 (real content) |
| Source discipline | 0 | 0 |
| Real data downloaded | 0 | 0 |
| Memo content | 0 | 0 |
| Financial model | 0 (stub) | 0 (none) |
| Recovery from failure | 0 | 0 |
| **Overall** | ~15/100 | ~20/100 |

## Harness changes from this run

1. **Dynamic max_tokens** — `min(64K, max_model_len - last_prompt_tokens - 14K)`. Prevents context-overflow 400s as history grows.
2. **Workspace state-hash stuck detector** — kills the run after 30 consecutive iters with no file/commit change. Configurable threshold.
3. Removed iteration cap as the primary terminator (was 200, now 10K — basically off; the stuck detector is the real terminator).

## Open questions

- Does a thinking-mode model (27B-AWQ) handle the recovery-from-failure case differently? Same task on 27B is the natural next run.
- If we add a system prompt that nudges toward Python/requests over curl, does Coder-Next make it past the SEC download wall? (tells us whether the failure is "tool selection bias" or "fundamental incapacity")
- What does the same task look like on a frontier model (Claude, GPT-4) for a quality ceiling reference? (would require external API)

## Artifacts

- v2: `agent-pilot/logs/coder_invest_memo_v2/` — transcript.jsonl, summary.json, workspace_final.tar.gz
- v3: `agent-pilot/logs/coder_invest_memo_v3/` — same structure
- Harness at this commit: see `agent-pilot/harness.py`
- Task prompt: `agent-pilot/task_investment_memo.md`
