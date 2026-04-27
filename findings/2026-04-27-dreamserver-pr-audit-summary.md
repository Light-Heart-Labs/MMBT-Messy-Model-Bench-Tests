# 2026-04-27 — DreamServer PR-audit task: three local models, three different failures

> Audit of three local 30B-class agentic models on a real-world PR-review task against a real public repo (`Light-Heart-Labs/DreamServer`, 75 open PRs at time of writing). Headline: **none of the three local models is trustworthy single-shot for code review at this scale**; the *kinds* of failure each one exhibits are themselves diagnostic for the daily-driver question.

## The task family

`agent-pilot/task_dreamserver_pr_audit.md` — full 75-PR audit, multi-hour scope, requires per-PR verdicts + cross-PR dependency analysis + executive synthesis + risk matrix + AMD-impact callout + actually-running tests + reproducing claimed bugs. Quality bar matters; speed of merge doesn't.

`agent-pilot/task_pr_audit_n1.md` — single-PR variant (PR #1057). Same rules-of-the-road, scaled-down deliverable structure. Built after the 75-PR runs revealed all three models failed in different ways and we needed to find each one's ceiling instead of just confirming all three fail at the top.

The escalation ladder (1 → 2 → 4 → 8 → 16 → 32 PRs, nested) was sketched but only N=1 has been run at the time of this writeup. N=1 alone produced enough signal to update the daily-driver decision; whether to scale further is an open question.

## The three models

| short | full | shape | role |
|---|---|---|---|
| **27B-AWQ** | Qwen3.6-27B AWQ-INT4, dense, thinking-mode | ~6-30 s per turn, deep reasoning between tool calls | "deliberate analyst" |
| **Coder-Next-AWQ** | Qwen3-Coder-Next AWQ-4bit, MoE 80B / 3B active, no thinking | ~1-3 s per turn, fast tool calls | "production engineer" |
| **35B-A3B-AWQ** | Qwen3.6-35B-A3B AWQ-4bit, MoE 35B / 3B active, thinking-mode | ~2-25 s per turn, thinking but smaller active param count | dominated on prior tasks (1/6 across memo+board) |

All three served via vLLM 0.19.x at `--max-model-len 262144` and `--gpu-memory-utilization 0.92` on RTX PRO 6000 Blackwell GPUs. Exact launch flags per model are in `agent-pilot/launch-commands.md` and captured in every run's `receipt.json`.

## Phase 1: 75-PR canonical runs

### 27B-AWQ (3 runs: `27b_pr_audit_canonical_v{1,2,3}`)

Three canonical runs, three different shapes:

| run | wall | iters | hand-written reviews | commits | tag | verdict distribution (M/R/Rej) |
|---|---:|---:|---:|---:|---|---:|
| v1 | 24 min | 57 | 3 (PR-1057, PR-988, PR-750) | 2 | `v1.0` ✓ | 59 / 10 / 6 |
| v2 | 39 min | 94 | **0** | 2 | — | 64 / 9 / 2 |
| v3 | 23 min | 54 | 0 | **0** | — | 70 / 4 / 1 |

All three structurally complete (75/75 verdict.md files, all required reports). All three's strategic synthesis is *genuinely good* — `dependency-graph.md` correctly clusters PRs by file overlap, executive summary identifies the right priority merges, contributor patterns are sound.

But — the per-PR depth is concentrated in 0-3 PRs out of 75. The remaining PRs get template-stub verdicts of ~15 lines: title + MERGE/REVISE/REJECT label + one-sentence reason mostly pulled from PR title + bounty tier metadata. *No actual diff inspection, no architectural reasoning, no traceability to specific lines.* And **no tests were run** in any of the three canonical runs. **No bug reproductions** either — the spec required running the installer in a clean container for installer PRs, running pytest on baseline-vs-PR for tested code paths, reproducing claimed bugs on main before validating fixes. None of that happened.

The model literally named v2's second commit *"Batch review scaffolding: initial verdicts, summaries, traces for all 75 PRs"* — admitting these are scaffolds, not reviews.

Pattern: **27B Goodharts the task spec** — produces the *shape* of the deliverable (every required path filled) and skips the *substance* (verdicts unearned by actual analysis). The structural compliance is misleading; a maintainer reading just the executive summary + dependency graph would see good work, then drill into a PR's verdict.md and find a stub.

Variance is also large: v1 was the best run (3 deep reviews, tagged release), v3 was the worst (0 commits, most lenient verdicts). Same task, same flags, same hardware. The harness's "approximate determinism" caveat (vLLM bf16 paths aren't bitwise deterministic) is the full explanation.

### Coder-Next-AWQ (smokes + 2 canonical attempts)

Three N=1 smokes (in the original 75-PR shape, wall-time-capped at 5 min each — these were what surfaced the harness fixes documented in `agent-pilot/HARNESS-CHANGELOG.md`):

- **smoke v1**: deterministic loop trap. 41 iters, 30 of them identical `curl .../pull/1057/files` calls. Surfaced the temp=0+seed=42 fixed-point issue → led to the `--temperature` flag.
- **smoke v2**: `ls -la` recon loop. 54 iters, 30 of them identical-shape `ls` of different DreamServer subdirs without writes. Surfaced the workspace-state-hash gap on read-only operations → led to the `--stuck-threshold` flag.
- **smoke v3**: cleaner harness fixes applied; agent did 54 iters of real work before locking into a `git log | grep "Merge pull request"` loop for the remaining iters. Wall-time killed it before stuck-detector fired.

Two canonical attempts (with the harness fixes applied):

- **canonical v1**: cycling-name template slop. 60 ADRs in `decisions/0XX-final-{report,merge,verification,approval,strategy}.md`, byte-identical content across cycles (5 templates repeating with filename++). Killed at ~iter 183 after content-hash dedupe confirmed the cycling pattern.
- **canonical v2**: stuck in research. 157 iters of legitimate per-PR `git diff` analysis across dozens of PRs. **0 write_file calls. 0 git commits.** Killed manually on the pivot to escalation experiment; trajectory had been read-only-forever for the entire run.

Three canonical-scale attempts, **three distinct degenerate failure modes**, all rooted in the same underlying mechanism: peaked logits on long-horizon tasks, where the model finds a stable surface form (identical command / cycling filenames / pure investigation) that satisfies whatever local objective it's tracking but never produces real audit work.

### 35B-A3B-AWQ

Not run on the 75-PR task. Consolidated-grid prior (1/6 across memo+board) made it the lowest-priority candidate; subsequent N=1 results (next section) confirmed the prior holds.

### Phase 1 conclusion

All three models fail the 75-PR task in different ways. **27B fails by Goodharting** — looks complete, isn't. **Coder-Next fails by spiraling** — produces motion without progress. The binary "all three fail" is a real signal but it doesn't tell us which one to pick for daily-driver use, where the typical task is much smaller than 75 PRs.

## Phase 2: N=1 escalation (six runs + one disqualifier)

`task_pr_audit_n1.md` reduces the task to a single PR (#1057, yasinBursali host-agent surgical fixes — known-clean MERGE per the canonical-v1 hand-written review and verifiable against the actual public diff). Same rules of the road, scaled-down deliverable structure (verdict + summary + review + diff-analysis + tests + research/notes/questions/dead-ends + decisions ADRs + sources + tool-log + README + final tag).

### Results

| run | wall | iters | files (of 13) | commits | tag | done() | verdict | quality |
|---|---:|---:|---:|---:|---|---|---|---|
| n1_coder_v1 | 3 min | 54 | 13 ✓ | 20 | ✓ | ✓ | **REJECT (wrong, 1 fabricated issue)** | low |
| n1_coder_v2 | 3 min | 63 | 13 ✓ | 18 | ✓ | ✓ | **MERGE (correct)** | medium |
| n1_coder_v3 | 4 min | 60 | 13 ✓ | 18 | ✓ | ✓ | **REJECT (wrong, 4 fabricated issues + fake test script)** | very low |
| n1_27b_v1 | 13 min | 62 | 4 ✗ | 1 | ✗ | ✗ | (not shipped; partial notes lean correct) | high |
| n1_27b_v2 | 5 min | 45 | 2 ✗ | 0 | ✗ | ✗ | (not shipped; partial notes correct on catalog) | high |
| n1_27b_v3 | 7 min | 46 | 7 ✗ | 0 | ✗ | ✗ | **implicit MERGE in review.md "Summary of Findings" table** | excellent |
| n1_35ba3b_v1 | 1.5 min | 28 | **0 ✗** | 0 | ✗ | ✗ | none — no artifacts written | n/a |

### What "wrong" means

PR #1057 is `fix(host-agent): runtime hygiene` — seven small surgical edits to `dream-server/bin/dream-host-agent.py`. Ground truth was established three independent ways:

1. The canonical-v1 27B hand-written review documented all 7 changes as MERGE-worthy with line-level reasoning, including the call-out that the catalog 500/403 asymmetry is intentional ("documented and justified")
2. The actual public diff (`patch-diff.githubusercontent.com/raw/.../1057.diff`) was fetched directly. The `_handle_model_list` and `_handle_model_download` handlers have intentionally different policies on missing-catalog: list returns empty (fresh install OK), download returns 500 (download requires a catalog to validate against). Both behaviors match the in-code comments
3. 27B v3's research/questions.md Q2 walked through the three branches (file doesn't exist / file exists but malformed / file exists and valid) and arrived at "the sentinel correctly handles the missing-file case as a broken install" — same conclusion as the hand-written review, derived independently

When Coder-Next v1 said "the PR returns 500 for missing files which contradicts its own comment" → it conflated the LIST handler's comment with the DOWNLOAD handler's behavior. **One handler. Different comment.** The model pattern-matched "comment about missing files" + "code returning 500 nearby" without checking the function boundaries.

Coder-Next v3 went further: claimed `stderr[-500:]` is wrong because errors are at the *beginning* of stderr (the PR's whole point is that Docker Compose puts errors at the END), claimed `_recreate_llama_server` raising RuntimeError is "inconsistent with the codebase" (it's the explicit fix for a 5-minute hang), and authored a fake `tests/test_stderr_truncation.py` that purportedly demonstrates the (non-existent) issue.

### What this looks like for daily-driver use

**Coder-Next at N=1**: 100% spec-compliant deliverables (every run hits done() and tags a release). 67% wrong verdicts. The wrong runs cite line numbers and sometimes write fake test scripts to support fabricated technical issues. **Majority vote across N=3 doesn't save it** — REJECT wins 2-1, but it's the wrong call, and the two REJECT runs hallucinate *different specific issues*. A reviewer reading just verdict.md would be confidently misled.

**27B at N=1**: 0% spec-compliant deliverables (no verdict.md, no tag, no done() in any run). 0% wrong verdicts (no shipped verdicts to be wrong about). Quality of partial work ranges from high (v1, v2) to excellent (v3 — best analysis content of any of the 6 runs, including a clean walk-through of the catalog architecture in questions.md). **Failure mode is spec compliance, not quality.** A reviewer reading review.md + research/questions.md would get correct, well-reasoned analysis.

**35B-A3B at N=1**: 0% ship anything. 28 iters of legitimate investigation (read code, ran pytest), then a 25-second thinking turn with 4,368 reasoning tokens that emitted no tool calls. Floor failure. Disqualified from the escalation grid.

### Variance characterization

| | spec compliance | accuracy | content variance |
|---|---|---|---|
| Coder-Next | very low (100% complete) | **high** (verdict flips REJECT→MERGE→REJECT across runs; wrong runs hallucinate different issues each time) | also flips per-claim |
| 27B-AWQ | high (0% complete) | low for spec-shaped output | medium (the rollback-bug claim flipped between v1 "is a bug" and v2 "is fine" within research notes) |
| 35B-A3B | n/a (no output) | n/a | n/a |

**Coder-Next's variance is more dangerous than 27B's** because it lands in the visible-shape layer. Two runs of the same model on the same input produce confidently opposite verdicts, both with line-cited evidence, both calling done() and tagging a release. From the artifact alone you can't tell which run got it right.

27B's variance lives in research notes — between v1 and v2 the rollback-path concern flipped from "this silently fails" to "this is correctly caught." Less catastrophic than Coder-Next's verdict flip because no incorrect verdict ships, but it does mean any specific claim in 27B's notes warrants cross-checking.

## What this means for the daily-driver question

The original goal was picking a single local model to use day-to-day. The data here updates that question more than it answers it.

**For automated review pipelines that scrape verdict.md**: only Coder-Next ships in that shape, and it would mis-route 2/3 of PRs at N=1. Don't.

**For human-in-the-loop review where someone reads review.md / research notes**: 27B's partial output is meaningfully more trustworthy than Coder-Next's complete output. The "doesn't ship verdict.md" failure is a UI defect, not a quality defect — review.md alone is a real review. Cost: you have to know to look there.

**For long-horizon agentic work (hours unattended)**: none of the three. All three find a degenerate mode within 30-60 minutes of running.

**For chat / single-shot reasoning / one-off coding help**: this benchmark doesn't directly measure that. The consolidated-grid finding from 2026-04-26 (Coder-Next on the bounded board task: 3/3, mean 90, range 7) suggests Coder-Next is fine for *bounded structured-input* tasks where the variance source is small. But that's a different shape from "review this PR for me."

**For 35B-A3B**: don't.

## Caveats — please read before quoting

- **One PR, hand-graded.** The N=1 results are based on three runs each on a single PR with depth that lets us hand-verify against the actual diff. Generalizing to "Coder-Next is wrong 67% of the time on PR review" *would be wrong*. The right framing is: "on this specific PR, with these specific architectural distinctions to spot, with these specific harness flags, on this specific hardware, Coder-Next was wrong 2/3 of the time." Different PRs, different distinctions, different hardware can move the rate either way.
- **Harness was iteratively fixed mid-experiment.** Three substantive harness changes happened between the first smoke and the canonical runs: `--temperature` flag (was hardcoded 0.0), `--stuck-threshold` flag (was hardcoded 30), sandbox capability flags (`--gh-token`, `--docker-socket`, `--gpus`). All documented in `agent-pilot/HARNESS-CHANGELOG.md`. The smokes that used pre-fix flags are kept as data points — they characterize the failure mode before the fix — but not used as fair model-comparison evidence after the fix landed.
- **Approximate determinism.** vLLM bf16 paths aren't bitwise-deterministic, so `temperature=0.0 + seed=42` doesn't produce identical runs. We're operating at `temperature=0.3` for the canonical/N=1 runs (to break the deterministic loop traps surfaced by the smokes), which makes per-run variance an inherent property of the data, not a bug.
- **No formal scoring rubric.** Verdicts were graded right/wrong by checking specific claims against the actual diff and the canonical hand-written review. This is fine at N=1 with one PR; it does not scale. Any formal cloud-vs-local comparison should establish a per-claim rubric (verdict matches ground truth: y/n; line citations valid: y/n; fabricated evidence present: y/n) and apply it consistently.
- **Hardware: Tower2 (WRX90E, TR PRO 7965WX, 2× RTX PRO 6000 Blackwell at 600 W uncapped, 252 GB RAM).** GPU0 hosted Coder-Next or 35B-A3B (swapped); GPU1 hosted 27B. Each run's `receipt.json` records the actual nvidia-smi snapshot at start, vLLM container Args, and harness git SHA — those receipts are the canonical reproducibility artifacts.
- **35B-A3B disqualification was made on N=1.** A defender of 35B-A3B could reasonably ask for N=3. The trajectory at N=1 (28 iters → 25-second thinking turn → empty assistant message → stop) and the prior from the consolidated grid (1/6 across memo+board) made the variance question feel low-value relative to spending compute on the actually-competitive comparison. This is a judgment call worth flagging.

## Open follow-ups

The N=1 results sharpen the daily-driver picture but leave several things unexplored:

1. **N=2, N=4, N=8 runs** would tell us where Coder-Next's accuracy gets even worse vs where 27B's spec compliance gets even worse. The escalation experiment was paused at N=1.
2. **Cloud-LLM head-to-head on the same N=1 task** is the natural next step. Does Claude / GPT / Gemini ship verdict.md + tag release like Coder-Next, *and* get the verdict right like 27B? That gap is the cost of "local vs cloud" stated cleanly.
3. **Different PRs.** PR #1057 has subtle architectural distinctions (two handlers, intentionally asymmetric); a different PR class (pure docs change, large refactor with bugs, security-sensitive change) would test different failure modes.
4. **Different prompting.** The task spec is dense and prescriptive. A loose-prompt variant ("review this PR and tell me what you think") might shift the failure modes — Coder-Next might hallucinate less under a less-prescriptive setup; 27B might ship a verdict if the spec doesn't enforce 13 specific files.
5. **Variance reduction at higher N**. 27B's accuracy looks high at N=3 with the small caveat about analysis-content variance. Would N=5+ show convergence on the right answer, or new failure modes emerging?

## Reproducibility

Every run has:
- `agent-pilot/logs/<run>/receipt.json` — vLLM container Args, harness git SHA + dirty flag, task file SHA, host kernel/OS, full nvidia-smi snapshot at run start, sandbox runtime config (gh_token_set, docker_socket, gpus, input_mount), inference request defaults
- `agent-pilot/logs/<run>/transcript.jsonl` — every model turn + tool call with timing, token counts, finish_reason
- `agent-pilot/logs/<run>/summary.json` — final state (when the harness exits cleanly; absent for runs killed mid-loop)
- `agent-pilot/logs/<run>/workspace_final.tar.gz` — the agent's complete workspace at end-of-run (for runs that exit cleanly)

To rerun a specific run identically: checkout the harness git SHA from its receipt, rebuild the sandbox image (`docker build -t bench-sandbox:latest agent-pilot/`), launch vLLM with the exact args from `receipt.vllm.containers[0].args`, run the harness with the same flags. See `REPRODUCING.md` for a full walkthrough.
