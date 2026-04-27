# DreamServer 1-PR Audit — Qwen3-Coder-Next-AWQ

**Subject:** [PR #1057](https://github.com/Light-Heart-Labs/DreamServer/pull/1057) — `fix(host-agent): runtime hygiene`
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main)
**Audit date:** 2026-04-27
**Auditor:** Qwen3-Coder-Next AWQ-4bit (Cyankiwi quantization), MoE 80B / 3B active, no thinking-mode
**vLLM config:** `--max-model-len 262144`, `--temperature 0.3`, `--enable-auto-tool-choice --tool-call-parser qwen3_coder`
**Sandbox config:** `--docker-socket --gpus all --stuck-threshold 500`
**Wall-clock:** 3 minutes 15 seconds, 63 iterations, 20K completion tokens
**Run name:** `n1_coder_v2` (the *cherry-picked correct run* of three; see "Variance" below)

## Verdict

**MERGE** after minor documentation improvements.

Specifically: the model correctly identified the `_handle_model_list` vs `_handle_model_download` asymmetric catalog handling as intentional and well-architected, marked all 7 changes ✅ correct, called out that no AMD-specific code paths are touched, and recommended adding a comment explaining the Windows path-skip logic. This matches the ground-truth assessment (see [`Opus-4.7/prs/pr-1057/verdict.md`](../../dreamserver-75-pr-audit/Opus-4.7/prs/pr-1057/verdict.md) in the sibling 75-PR benchmark).

## Variance — read this before treating the verdict as the model's "answer"

The model was run **three times** on the same task with the same flags. The verdicts:

| run | wall | iters | verdict | wrong-on |
|---|---|---|---|---|
| `n1_coder_v1` | 3 min | 54 | **REJECT** | catalog-handling (conflated the two handlers) |
| `n1_coder_v2` | 3 min | 63 | **MERGE** ← this entry | (correct) |
| `n1_coder_v3` | 4 min | 60 | **REJECT** | stderr direction + catalog + llama-server + pull edge case (fabricated 4 issues, including a fake `tests/test_stderr_truncation.py` that "demonstrates" a non-existent issue) |

**Two of three runs were wrong.** The wrong runs hallucinated *different* specific technical issues each time. Majority vote across N=3 doesn't save the model — REJECT wins 2-1, but it's the wrong call.

This entry contains v2's deliverable (the correct one) because it's the actual successful audit. But anyone treating this entry as "Coder-Next's verdict on PR-1057" without reading this section would be misled — the model's *expected* output on this PR with the same flags is "wrong with 67% probability." For a daily-driver review use case, that means single-shot output cannot be trusted; you'd need a second model's verification on every verdict.

The full variance characterization is in the bench repo's `findings/2026-04-27-dreamserver-pr-audit-summary.md` and the sibling-folder findings doc at [`../../dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`](../../dreamserver-75-pr-audit/findings-2026-04-27-local-models.md).

## What's in this entry

```
verdict.md         MERGE recommendation with line-by-line justification
summary.md         What the PR claims, in auditor's words
review.md          Line-by-line review of all 7 changes
diff-analysis.md   Claimed vs actual changes
tests/             Reproduction scripts the model wrote
trace.md           Pointers to commits, files, lines reviewed
research/          notes.md, questions.md, dead-ends.md, upstream-context.md
sources.md         External content fetched
tool-log.md        Tool calls in order
```

The model also tagged `v1.0.0` at the end of its run, satisfying the task's "tag a release when done" requirement. (That tag is not preserved in this published entry — only the file content.)

## Reproducibility

Source-of-truth is `agent-pilot/logs/n1_coder_v2/` in the bench repo. Receipt has the exact vLLM args, harness git SHA, task file SHA, GPU snapshot, and sandbox runtime config.

To replay:
```bash
python3 agent-pilot/harness.py replay_n1_coder_v2 agent-pilot/task_pr_audit_n1.md \
  --model qwen3-coder-next-awq --port 8001 \
  --temperature 0.3 --stuck-threshold 500 \
  --docker-socket --gpus all
```

Expect divergence — vLLM bf16 paths aren't bitwise-deterministic, and at temp=0.3 the sampling diversity is real.
