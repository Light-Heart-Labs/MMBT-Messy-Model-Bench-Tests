# DreamServer 1-PR Audit — Qwen3.6-27B-AWQ

**Subject:** [PR #1057](https://github.com/Light-Heart-Labs/DreamServer/pull/1057) — `fix(host-agent): runtime hygiene`
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main)
**Audit date:** 2026-04-27
**Auditor:** Qwen3.6-27B AWQ-INT4 (Cyankiwi quantization), dense, thinking-mode
**vLLM config:** `--max-model-len 262144`, `--temperature 0.3`, `--reasoning-parser qwen3 --tool-call-parser qwen3_xml`
**Sandbox config:** `--docker-socket --gpus all --stuck-threshold 500`
**Wall-clock:** 6 minutes 48 seconds, 46 iterations, 15K completion tokens
**Run name:** `n1_27b_v3` (the highest-quality run of three; see "Variance" below)

## Verdict

**Implicit MERGE** in [`review.md`](review.md)'s "Summary of Findings" table — every change marked ✅ Correct, AMD impact: None across the board.

But there's no `verdict.md` file. The model produced excellent analytical content but failed to ship the spec-shaped deliverable. The task explicitly required `verdict.md` with a top-level recommendation header; instead the verdict has to be inferred from the table at the end of `review.md`. This is a real defect for any pipeline that scrapes `verdict.md`.

## Read this first — what this entry is and isn't

This entry is **substantively excellent, structurally incomplete**.

What's real and worth reading:
- [`research/questions.md`](research/questions.md) — five questions with explicit walked-through resolutions. Q2 is the cleanest articulation of the catalog-handling architecture across all 7 model runs on this PR (3× Coder-Next + 3× 27B + 1× 35B-A3B): walks through the three branches (file doesn't exist / file exists but malformed / file exists and valid) and arrives at the correct conclusion that the asymmetric handling is intentional. Better framing than the canonical hand-written ground-truth review.
- [`review.md`](review.md) — line-by-line analysis of all 7 changes, with risk and AMD-impact columns. Ends with a Summary of Findings table that is functionally a MERGE recommendation.
- [`research/dead-ends.md`](research/dead-ends.md) — honest about what couldn't be tested in the sandbox environment ("attempted to reproduce X but the sandbox doesn't have full DreamServer extension structure; accepted based on code analysis"). The right kind of "dead end" — admits limits and explains the workaround.
- [`tests/test_host_agent_suite.py`](tests/test_host_agent_suite.py) — the model invoked pytest on the actual upstream test suite during the run (38 tests, all passed on both `main` and the PR branch — confirmed in the run's transcript).

What's missing:
- **No `verdict.md`.** Verdict has to be inferred from review.md's table.
- **No `tag` (`v1.0`).** Spec required tagging a release at end-of-run.
- **No `done()` call.** The model emitted an empty assistant message at iter 46 and stopped without explicitly signaling completion.
- **No `decisions/<ADR>.md`.** The `decisions/` directory exists but is empty.
- **No `sources.md`, no `tool-log.md`** — the model didn't write these spec-required artifacts.
- **0 git commits** — the model never ran `git add` + `git commit` in its workspace.

## Variance — read this before treating the analysis as the model's "answer"

The model was run **three times** on the same task. None shipped a spec-compliant deliverable. The analytical content varied:

| run | wall | iters | files written | git commits | quality of partial work |
|---|---|---|---|---|---|
| `n1_27b_v1` | 13 min | 62 | 4 | 1 | high — caught a bug Coder-Next missed (rollback-path silent failure), self-corrected on a false `logger.info` indentation claim |
| `n1_27b_v2` | 5 min | 45 | 2 | 0 | medium — analysis correct on catalog, but the rollback-bug claim from v1 *flipped* to "this is fine" |
| `n1_27b_v3` | 7 min | 46 | 7 ← this entry | 0 | excellent — cleanest catalog walk-through, all 7 changes correctly assessed |

So 27B's three runs span "best analytical content of any local model" (v3) to "minimal partial output" (v2). Within research notes, specific claims (like the rollback-path concern) flipped between runs — meaning any individual claim warrants cross-checking against either the actual diff or another run.

What's *consistent* across all three: **none ship the spec-shaped deliverable.** No verdict.md, no tag, no done() in any run.

Daily-driver implication: 27B is meaningfully more *trustworthy* than Coder-Next on this PR (no incorrect verdicts shipped, since no verdicts shipped period), but if you're using output that depends on the spec-required file structure, you can't rely on 27B to produce it. Cost: you read review.md + research/ to extract the answer.

## What's in this entry

```
review.md            line-by-line review with verdict-shaped Summary of Findings table
summary.md           what the PR claims
diff-analysis.md     claimed vs actual changes
research/
  notes.md           working notes
  questions.md       five questions with resolutions (Q2 is the catalog walk-through)
  dead-ends.md       what the sandbox couldn't reproduce, and why
tests/
  test_host_agent_suite.py   pytest invocation against upstream tests (38/38 passed both branches)
decisions/           empty (the model didn't write any ADRs in this run)
```

Compared to the [`Qwen3-Coder-Next-AWQ/`](../Qwen3-Coder-Next-AWQ/) sibling: Coder-Next has the spec-compliant 13-file structure (verdict.md, tag, done()) but its verdict was wrong 2 of 3 times. 27B has correct analysis but skips the spec scaffolding.

## Reproducibility

Source-of-truth is `agent-pilot/logs/n1_27b_v3/` in the bench repo. Receipt has the exact vLLM args, harness git SHA, task file SHA, GPU snapshot.

To replay:
```bash
python3 agent-pilot/harness.py replay_n1_27b_v3 agent-pilot/task_pr_audit_n1.md \
  --model qwen3.6-27b-awq --port 8000 \
  --temperature 0.3 --stuck-threshold 500 \
  --docker-socket --gpus all
```

vLLM bf16 paths aren't bitwise-deterministic. Expect divergence between runs.
