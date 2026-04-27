# DreamServer Open-PR Audit — Qwen3-Coder-Next-AWQ (NO DELIVERABLE)

**Subject:** [Light-Heart-Labs/DreamServer](https://github.com/Light-Heart-Labs/DreamServer)
**Baseline commit:** `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main)
**PR set:** 75 open PRs, numbers `351`–`1057`
**Audit date:** 2026-04-27
**Auditor:** Qwen3-Coder-Next AWQ-4bit (Cyankiwi quantization), MoE 80B / 3B active, no thinking-mode. vLLM 0.19.x at `--max-model-len 262144`, `--temperature 0.3`, sandbox `--docker-socket --gpus all --stuck-threshold 500`.

## This entry intentionally has no audit deliverable

The model attempted the 75-PR audit task **five times** (3 wall-time-capped smokes during harness validation, 2 uncapped canonical runs). All five entered a degenerate failure mode before producing a usable audit. The folder is kept as part of the benchmark record because **the kinds of failure are themselves diagnostic** — readers comparing this benchmark across models should know that this model class can't complete this task at this scale, and what specifically broke.

## Three distinct degenerate failure modes across five attempts

### 1. Identical-call loops (smokes v1, v2, v3)

Three early runs, all wall-time-capped at 5 minutes. Each got 5-15 minutes of real work done (clone repo, fetch all 75 PRs as `refs/remotes/origin/pr/*`, scaffold the audit-repo directory tree, sometimes a first commit) — then locked into 30+ consecutive iterations of an *identical* bash command.

Examples:

- **smoke v1**: 30 consecutive `curl .../pull/1057/files` calls, byte-identical
- **smoke v2**: 30 consecutive `ls -la` calls (different paths each time, but no writes — recon without production)
- **smoke v3**: 50+ consecutive `git log --oneline -1000 --all | grep "Merge pull request" | sed | awk | grep | uniq` calls

These runs surfaced harness gaps that we patched mid-experiment (the `--temperature` and `--stuck-threshold` flags in `agent-pilot/HARNESS-CHANGELOG.md` of the source bench repo). After the harness fixes, the failure mode shifted from "obviously stuck" to subtler forms (below) — but didn't go away.

### 2. Cyclic-name template slop (canonical v1)

Run with the harness fixes applied. Started clean: cloned, fetched PRs, did real distinct ADR work for the first ~25 entries (`decisions/001-test-environment.md`, `002-pr-size-limits.md`, `003-merge-order.md`, `004-amd-verification.md`, `005-contributor-mentorship.md`).

Then around iter 30, locked into a 5-template cycle. From that point on, every 6-iter group produced byte-for-byte identical content with the filename incremented by 5. Killed at ~iter 183 after content-hash dedupe confirmed the pattern:

```
$ md5sum decisions/*.md | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
   6 dc585cd78249be668583a1e460af3c28   ← "final-report" template, 6 copies
   6 92fd6379398e4a8b5b33c40c0a9232d2   ← "final-merge" template, 6 copies
   6 1dada77fde106cd27177451ef6385e03   ← "final-verification" template, 6 copies
   5 59e15fb2662cdafbd6ad31856f8414a0   ← "final-approval" template, 5 copies
   5 0716496128e8d847ff8bdc2340cd2800   ← "final-strategy" template, 5 copies

$ diff decisions/051-final-report.md decisions/056-final-report.md
$ diff decisions/051-final-report.md decisions/061-final-report.md
$ diff decisions/052-final-merge.md decisions/057-final-merge.md
(all three diffs return empty — files are byte-identical)
```

The agent never produced a single per-PR `verdict.md`. 60 ADRs were written; 28 of them are pure duplicates of just 5 templates. The workspace state hash was changing (each new filename incremented file count by 1) so the stuck-detector didn't fire — a real gap in the detector's coverage that this run surfaced.

### 3. Stuck in research (canonical v2)

Final attempt. 157 iterations, all read-only — `git diff origin/main..pr-XXXX --stat` across dozens of distinct PRs, `git log --oneline pr-XXXX`, etc. All commands distinct from each other. Looked encouraging in the live transcript (no obvious slop signature) — until counting writes:

- **0 `write_file` calls**
- **0 git commits**
- **0 file writes via bash redirect** (no `>`, no `tee`, no heredoc)
- 10,576 total completion tokens (67/iter avg — short recon-shaped responses)

The agent did legitimate per-PR investigation for 157 iterations and never once transitioned from "look at diff" to "write verdict." Killed manually because the trajectory had been read-only-forever for the entire run.

The workspace state hash was updating — `git diff` against fetched refs touches git's internal state, which changes `.git/refs/...` files. Same blind spot as v1's cycling-filename slop: the hash predicate sees motion that isn't progress.

## Why the model can't complete this task

All three failure modes share the same underlying mechanism: **peaked logits on long-horizon tasks**. The model finds a stable surface form (identical command / cycling filenames / pure investigation) that satisfies whatever local objective it's tracking — workspace state changes, distinct commands emitted, work being done — but never produces real audit output.

At `--temperature 0.3`, sampling diversity isn't enough to escape the peaks. Higher temperature (0.5, 0.7) wasn't tested on this task; it might break the trap, but it would also reduce verdict accuracy on the per-PR level (see the model's results in `../dreamserver-1-pr-audit/Qwen3-Coder-Next-AWQ/` where it does single-PR work with mixed accuracy).

The model has the *capability* for the task in microcosm — it can do an N=1 PR audit (see the sibling benchmark folder). It can't sustain that capability across N=75 in a single run.

## What this means for using Coder-Next on review work

For real PR-review use, this model class would need either:

- **Per-PR invocation pattern**: invoke the model fresh for each PR rather than expecting one long-running agent to handle all 75. The N=1 results show this is feasible.
- **External orchestration**: a wrapper that detects the loop modes (output-hash repetition, write-rate decay, content-hash duplication) and either restarts the agent or escalates to a different model.
- **Post-hoc verification**: pair every Coder-Next verdict with a second model's check, since the failure modes are silent.

This benchmark, run as the maintainer-facing "audit 75 PRs" task without orchestration, is the wrong shape for this model.

## What is preserved from the failed runs

Every run's `receipt.json` and `transcript.jsonl` are kept in the source bench repo (`agent-pilot/logs/coder_pr_audit_*/`). The canonical-v1 `workspace_final.tar.gz` is also kept (~22 MB) — it contains the 60 cyclic-name ADRs as evidence. canonical v2 has no workspace tarball (the harness was killed mid-loop before its end-of-run cleanup ran).

The bench repo's `findings/2026-04-27-dreamserver-pr-audit-summary.md` has the full cross-model write-up.
