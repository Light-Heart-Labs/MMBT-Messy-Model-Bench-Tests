# DreamServer 1-PR Audit — Qwen3.6-35B-A3B-AWQ (FLOOR FAILURE)

**Subject:** [PR #1057](https://github.com/Light-Heart-Labs/DreamServer/pull/1057) — `fix(host-agent): runtime hygiene`
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main)
**Audit date:** 2026-04-27
**Auditor:** Qwen3.6-35B-A3B AWQ-4bit (Cyankiwi quantization), MoE 35B / 3B active, thinking-mode
**vLLM config:** `--max-model-len 262144`, `--temperature 0.3`, `--reasoning-parser qwen3 --tool-call-parser qwen3_xml`
**Sandbox config:** `--docker-socket --gpus all --stuck-threshold 500`
**Wall-clock:** 1 minute 42 seconds, 28 iterations, 8.9K completion tokens
**Run name:** `n1_35ba3b_v1`

## This entry intentionally has no audit deliverable

The model attempted the task once and produced **zero audit artifacts**. No verdict.md, no review.md, no commits, no tag — nothing. The folder is kept as part of the benchmark record because "this model can't even do N=1 on this task class" is itself a meaningful comparison point against the other entries in this folder.

## What happened

Trajectory across 28 iterations:
- **Iters 1-19**: Genuine investigation. Cloned the repo, fetched the PR branch, ran `git diff`, read large code chunks at lines 190-260, 1130-1370, 1530-1810, 1960-2010, 2070-2230. Hit GitHub API. Looked at `CONTRIBUTING.md` for bounty info. Grep'd for AMD-related code paths. Quality of recon was reasonable.
- **Iters 20-25**: Even attempted the test suite. Hit a `pyyaml` import error, installed it, then ran `pytest` on `main`. Used `git checkout refs/pull/1057/head -- dream-server/bin/dream-host-agent.py` to swap just the changed file in and ran `pytest` again. Real test methodology.
- **Iter 26**: Reset back to `main`.
- **Iter 27**: Created `/workspace/audit-repo/tests/repro/` directory (empty).
- **Iter 28**: Spent 25.91 seconds on a long thinking turn (4,368 reasoning tokens), emitted **no tool calls**, and stopped.

End state: the audit repo has its directory tree mkdir'd but **no files written and no commits made**. Stuck-detector didn't fire (`no-progress=` was 0/500 because git operations changed the workspace state hash). The model just... didn't transition from "think about the audit" to "write the audit."

## Why this is the same disease, deeper

This is the same "stuck in research, can't transition to writing" failure mode as Coder-Next's [`canonical-v2 75-PR run`](../../dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/), but at much smaller scale. Coder-Next did 157 iterations of investigation across 75 PRs before being killed. 35B-A3B did 28 iterations on a *single PR* and stopped on its own without ever writing.

The N=1 case strips away every excuse a model could have on the 75-PR variant — there's no scope to be overwhelmed by, no batch to scaffold, no degenerate-mode to fall into via long context. Just one PR, one verdict to write. 35B-A3B can't do that without external orchestration.

## Prior consolidated-grid result

In the earlier 2026-04-26 grid (memo + board × three replicates each), 35B-A3B-AWQ was 1/6 across both task families — the only success was a single board-task run (#1 of 3). On that batch:

- Memo task: 0/3 (all failed in different ways: stuck, model_stopped, exceeded_max_tokens)
- Board task: 1/3 (one success at score ~85; v2 hit api_error 400 context overflow; v3 model_stopped)

The 1-PR audit floor failure is consistent with that prior. 35B-A3B-AWQ at 4-bit quantization on this hardware is below the threshold needed for agentic work in this task family. **Disqualified from continuation in the escalation experiment** — N=2, N=4, etc. were not run on this model.

## What is preserved

`agent-pilot/logs/n1_35ba3b_v1/` in the bench repo has the receipt, transcript, and (since the harness exited cleanly via model_stopped) summary.json + an essentially-empty workspace tarball. The transcript is the most useful artifact for understanding the failure trajectory.

## Reproducibility

To attempt a replay:
```bash
python3 agent-pilot/harness.py replay_n1_35ba3b_v1 agent-pilot/task_pr_audit_n1.md \
  --model qwen3.6-35ba3b-awq --port 8001 \
  --temperature 0.3 --stuck-threshold 500 \
  --docker-socket --gpus all
```

We expect a similar-shape failure (early model_stopped after long internal thinking) but with non-bitwise-deterministic divergence in the specific iter count and recon trajectory.
