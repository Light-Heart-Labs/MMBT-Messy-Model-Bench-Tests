# 27B No-Think Full Grid — Results

> N=10 reps × 12 task families = 120 runs. Same harness flags as Phase B (`--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`), with `--no-think`. Two GPUs sharing the load via the sharded grid script (port 8002 / GPU0 + port 8003 / GPU1). Chain launched 2026-05-01 22:09 EDT, completed 2026-05-03 00:53 UTC. Wall: ~26h end-to-end including the operator-monitoring window in the final stretch.

## Headline numbers

| Outcome                                          | Count | %      |
|--------------------------------------------------|------:|-------:|
| `done_signal` (clean ship)                       |   113 | 94.2%  |
| `wall_killed_identical_call_loop` (harness-killed) |     4 |  3.3%  |
| `model_exceeded_max_tokens_137855` (runaway gen) |     1 |  0.8%  |
| operator-SIGTERM, primary=`identical-call-loop`  |     2 |  1.7%  |
| **Total accounted**                              | **120** | **100%** |

Effective ship rate: **113/120 = 94.2%** (Wilson 95% CI [88.4%, 97.4%]).
Pathological exit rate: **7/120 = 5.8%** (CI [2.6%, 11.6%]).

## Per-task-family ship rates

| Family            | done | auto-stuck | oversize | op-loop | Ship rate |
|-------------------|-----:|-----------:|---------:|--------:|:---------:|
| p1_bugfix         |   10 |          0 |        0 |       0 | **10/10** |
| p1_refactor       |   10 |          0 |        0 |       0 | **10/10** |
| p1_testwrite      |   10 |          0 |        0 |       0 | **10/10** |
| p2_ci             |   10 |          0 |        0 |       0 | **10/10** |
| p2_extract        |   10 |          0 |        0 |       0 | **10/10** |
| p2_hallucination  |   10 |          0 |        0 |       0 | **10/10** |
| p2_triage         |   10 |          0 |        0 |       0 | **10/10** |
| p3_business       |    8 |          2 |        0 |       0 | 8/10      |
| p3_doc            |    8 |          2 |        0 |       0 | 8/10      |
| p3_market         |    7 |          0 |        1 |       2 | **7/10**  |
| p3_pm             |   10 |          0 |        0 |       0 | **10/10** |
| p3_writing        |   10 |          0 |        0 |       0 | **10/10** |

### What this says

- **P1 (code) and P2 (analysis) are 100% solid for 27B-no-think across 70 runs.** Bugfix, refactor, testwrite, CI failure, extraction, hallucination triage, regression triage — all 10/10 done_signal. No pathology, zero exceptions.
- **All pathology lives in P3 (open-ended research/synthesis).** Business memo, doc synthesis, and market research are the only families that produced any failures.
- **p3_market is uniquely bad** — three *distinct* failure modes in 10 runs (70% ship, 30% pathological), more than any other cell.

## p3_market deep dive — three pathologies in 10 runs

The market-research task asks the agent to evaluate 5 password-manager products against pricing/security/SSO/CLI criteria, hitting live vendor pricing pages over the network. 27B-no-think failed three different ways:

| Run | Outcome | Mechanism |
|---|---|---|
| v1 | operator-SIGTERM @ iter 228 | identical-call-loop (155-iter scroll on PCMag page) |
| v2 | done_signal | clean ship |
| v3 | done_signal | clean ship |
| v4 | done_signal | clean ship |
| v5 | `model_exceeded_max_tokens_137855` | runaway generation past 137K output tokens, single response |
| v6 | done_signal | clean ship |
| v7 | done_signal | clean ship |
| v8 | operator-SIGTERM @ iter 116 | identical-call-loop (31-iter scroll on PCMag page, same template as v1) |
| v9 | done_signal | clean ship |
| v10| done_signal | clean ship |

The two SIGTERM'd runs (v1 and v8) were stuck in the **same exact pattern** — PCMag/LastPass-pricing scrape, walking the same HTML response in 20K-byte slices via `python -c "print(content[N:N+20000])"`. Each iter incremented the slice offset; raw command hashes were unique so the harness's same-content guard did not fire. v1 walked 155 iters before operator intervention; v8 walked 31. Both runs spent 30+ minutes producing nothing.

The third failure (v5) was a different pathology: the model emitted a single very long response that exhausted the harness's output-token budget. No tool-call loop — just a runaway generation. This finish_reason (`model_exceeded_max_tokens_*`) is **not currently in `agent-pilot/FAILURE-TAXONOMY.md`**.

## Methodology improvement caught during the run

The original monitoring loop checked liveness — was the harness writing transcripts, were iter counters climbing, were GPUs busy. v1 was looping for ~2 hours under those signals (transcripts growing, iter counter +1/iter, GPU at 500W) before any flag fired.

What caught it: **substance checking** — sampling the recent tool-call commands and comparing them with digit-stripping (collapsing `content[2615000:2635000]` and `content[2795000:2815000]` to a single template). The first scroll-loop in this chain was running for 155 consecutive iters of the same digit-stripped template before being detected.

The harness's own stuck guard is a workspace-hash check that fires after 500 unchanged iterations. It does not catch scroll-loops because the model-emitted commands have *different* hashes (offsets differ) and stdout outputs are different page slices, even though no real progress is being made. Three of these runs (v1, v8, and likely the wall_killed ones in business/doc) followed this same pattern.

**Recommendation for `FAILURE-TAXONOMY.md`:**
- Add a sub-label `scroll-loop` under `identical-call-loop` for the digit-different but template-identical case.
- Add a primary label or finish_reason note for `model_exceeded_max_tokens_*` so this pathology is taggable separately from `partial-no-spec-output`.

## Operator-monitoring summary (the final stretch)

In the final ~3 hours of the chain, an operator-monitoring loop ran a 5-min cron substance check that:

1. Sampled the last 10 tool calls per live run.
2. Computed digit-stripped template counts (`uniq_tpl_last10` and `tail_streak`).
3. SIGTERM'd by exact PID per the documented `>30 same-content writes` methodology rule.
4. Wrote `label.json` with `primary: identical-call-loop` for each kill.

This caught v1 and v8 before the harness's no-progress threshold fired (v1 was at 205/500, v8 at ~67/500 when killed). The same monitoring loop also surfaced v5's runaway generation (transcript stale 12+ min while harness alive — model still generating) before the harness's 60-min HTTP timeout would have fired.

The substance check's one false-positive: `write_file`-heavy task wrap-up phases collapse to identical templates under digit-stripping (every `write_file` call has the prefix `{"content": "..."}`). Refinement: track tool-name dispersion alongside template count, and inspect content novelty for `write_file` separately. v3 and v10 of p3_market both triggered this false flag during their final-deliverables phase and were quickly cleared.

## Comparison to Phase B (where overlap exists)

Phase B (2026-04-30) ran N=10 on the four differential cells (`p2_hallucination`, `p3_business`, `p3_doc`, `p3_market`) for both 27B-thinking and Coder-Next. The new no-think grid extends to all 12 families. Where the cells overlap:

| Cell | 27B (thinking, Phase B) | 27B-no-think (this run) |
|---|---|---|
| p2_hallucination | 10/10 done_signal | 10/10 done_signal |
| p3_business | 9/10 done_signal | 8/10 done_signal |
| p3_doc | 6/10 done_signal | 8/10 done_signal |
| p3_market | 7/10 done_signal | 7/10 done_signal |

p3_doc improved from 6/10 → 8/10 in no-think mode (the word-limit-trim loop from Phase B is less prevalent without thinking enabled). Other cells are within sampling noise.

## Caveats

- This doc reports **ship rate** (does the agent emit `done_signal` and stop?). It does not report **PASS rate** (does the output meet the per-task grading rubric?). PASS-rate analysis requires running the batch graders against the new tarballs and comparing verdicts to ground truth — a follow-up.
- Two of the SIGTERM'd runs (p3_market v1 and v8) have `label.json` and a transcript but no `summary.json` or `workspace_final.tar.gz`. Grader code that reads only summary.json will treat these as missing; the loop-rate denominator should include them.
- The 4 `wall_killed_identical_call_loop` runs (in p3_business and p3_doc) follow the same pattern type as v1/v8 but reached the harness's own threshold. They have full summary + tarball.

## Files

- Bench logs: `agent-pilot/logs/{cell}_27b-nothink_v{1..10}/` per run (transcript + receipt + summary + tarball + label.json where applicable)
- Operator-monitoring artifacts: `/tmp/chain_progress.log`, `/tmp/chain_watchdog.log`, `/tmp/chain_27b_nothink_shard{0,1}.log`, `/tmp/chain_27b_nothink_gpu1_finisher.log`
- Branch: `submit/phase-b-overnight-2026-05-02`
