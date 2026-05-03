# Known limitations

This is a working benchmark corpus, not a leaderboard. The data is real and the methodology is documented, but several caveats affect how strong any claim from this repository can be. They're spread across many entry READMEs and findings docs; this file consolidates them for a reader who wants to assess what the evidence here can and cannot support.

If you're considering quoting a number from this repo or building a deployment decision on it, **read this file first.**

## Reproducibility caveats

### All published receipts have `git_dirty: true`

Every `receipt.json` in this repo records `harness.git_dirty: true`, meaning the source bench repo had uncommitted changes when the run executed. The harness was being iterated on during the experiment (we made several substantive changes mid-batch — see `tooling/HARNESS-CHANGELOG.md`), and the runs that produced these entries happened against working trees, not clean tagged states. The harness git SHA in each receipt is therefore a near-but-not-exact reference; replays from those SHAs may differ slightly from the published runs.

For future canonical runs intended for publication, runs should be made from clean trees. This is a process fix going forward, not a fix to the published entries.

### Cherry-picked successful runs are published

The local-model entries that have a deliverable are the *single best of multiple attempts*. The Coder-Next single-PR audit, for example, is `n1_coder_v2` — the one of three runs that produced a correct verdict; the other two (`v1` and `v3`) gave wrong verdicts with fabricated supporting evidence. Each entry's README documents its variance honestly and quotes the per-run shipped-rate fraction. But: a reader comparing entries cell-by-cell sees the best of N, not the expected outcome.

For some entries (`benchmarks/dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/`, `benchmarks/wallstreet-intern-test/Qwen3.6-35B-A3B-AWQ/`) we publish failure-mode-only entries with no deliverable. Those are honest about the lack of a single representative run. But for the entries with deliverables, **don't quote a verdict or recommendation as "what the model says" without first checking the entry's variance section**.

### Microbench-2026-04-28: only 3 of 12 task families are published as full entries

The microbench has 12 task families × 2 models × N=3 = ~80 runs. Publishing every run as a full per-model folder would create 60+ tiny entries. Three task families (`adversarial-hallucination/`, `market-research/`, `doc-synthesis/`) are published as full per-model entries because they carry the highest-signal results. The other nine (Phase 1 coding × 3, Phase 2 extraction/CI/triage, Phase 3 business-memo/writing/PM) are published as **lean entries** (per-model README + cost.json + grade.json + label.json + summary.json + receipt.json — no transcripts or deliverables to keep repo size manageable).

This means: for the 9 lean entries, you can read the per-model verdict, cost, and label, but you can't drill into the specific transcript or deliverable artifact from MMBT alone. **However, the task prompts, input starters, ground truth, and grader scripts for all 12 task families are now shipped in `tooling/`** — so a reader with the right hardware can rerun any of these task families and produce their own transcripts + deliverables. See `tooling/REPRODUCING.md` § "Reproducing the microbench".

### Microbench: two manually-advanced 27B runs in `doc-synthesis`

`p3_doc_27b_v2` and `p3_doc_27b_v3` were manually SIGTERM'd mid-run after entering identical-call-loops on `brief.md` (writing the same content for 50-130+ iters). The stuck-detector at `--stuck-threshold 500` would have eventually fired but several hours later. The runs' summary.json files explicitly mark `finish_reason: wall_killed_identical_call_loop`. The behavior is documented as a 27B failure shape on this task, not a transient bug. But: a strict reading might note that the 0/3 PASS rate on doc-synthesis includes 2 manually-advanced runs, not 3 stuck-detector-fired runs. The diagnostic interpretation (model can't trim to word limit) is supported by all 3 runs producing identical-content writes around the same word count (765/775/768).

### Failed-run artifacts not currently included for most entries

Source bench repo has full receipts + transcripts + workspaces for every attempted run (success and failure). MMBT publishes receipts + transcripts only for the single representative run per entry. The 5 failed runs across the local models (`27b_invest_memo_v3`, `27b_invest_memo_v4`, `coder_invest_memo_v6`, `coder_invest_memo_v7`, `n1_coder_v1`, `n1_coder_v3`, all three 27B PR-audit canonicals' "secondary" runs, and the 35B-A3B failure runs) have receipts and transcripts in the private bench repo but not here. A more rigorous audit of variance would need those.

## Methodology caveats

### No formal scoring rubric

Verdicts are graded right/wrong by hand against the actual diff and a known-correct reference review. This works at small N with a single PR; it does not scale. Any larger comparison should establish a per-claim rubric (verdict matches ground truth: y/n; line citations valid: y/n; fabricated evidence count) and apply it consistently. The forthcoming `SCORECARD.md` synthesizes existing evidence into a normalized table but uses hand-graded inputs, not a formal rubric.

### Microbench Phase 3 hand-grading is *claude-grading-claude*

The 30 hand-graded subjective dimensions on the microbench Phase 3 entries (prose quality, stance clarity, source skepticism, balanced tone, audience tone fit, faithfulness, fabrication count, citation validity) were graded by Claude Opus 4.7, not by the human maintainer. The grader is a different model from the grade-ees (Qwen3.6-27B-AWQ, Qwen3-Coder-Next-AWQ), and the grader's outputs went into `hand_rating_placeholders` with explicit `_GRADER_: claude-opus-4.7-1m-context` provenance fields — but the meta-issue stands: a model graded other models' outputs, and the grader's biases are not separately characterized. For research-grade claims about prose quality differences between models, a human grading pass would be needed.

The citation-validity sample on the 27B market-research entry (18 of 33 URLs, measured 75% valid) was done with WebFetch + content-comparison, which is a more grounded methodology than aesthetic judgment. The remaining hand-graded dimensions are prose-aesthetic and meta-issue-affected.

### Small N (typically N=3 per model × task)

3 runs per cell is enough to see that variance exists; not enough to bound it. Confidence intervals on a 1/3 success rate are wide ([1%, 71%] at 95%). Aggregate claims like "Coder-Next is wrong 67% of the time at N=1" are best read as "in the runs we ran, it was wrong 2/3 of the time." Generalization needs more data.

### Approximate determinism only

vLLM's bf16 paths aren't bitwise-deterministic, so `temperature=0.0 + seed=42` doesn't produce identical runs. Most runs in this repo use `temperature=0.3` deliberately, to break deterministic loop traps surfaced during the smokes. That makes per-run variance an inherent property of the data, not a bug — but it also means rerunning the same prompt with the same flags will produce a different output, and comparing single runs cell-by-cell is misleading.

### Live data drift

Tasks that reference real public state (DreamServer PRs, SEC filings, market prices) will see that state drift over time. The DreamServer PR audit task pins to a specific baseline commit (`d5154c37...`) but PR comments accumulate, contributors close PRs, the issue tracker moves. The wallstreet task has no such anchor — the company-pick is the agent's decision and the analyzed material may have been updated since extraction. Take time-of-run into account when comparing across replicates.

## Hardware and platform caveats

### Single-workstation hardware specificity

All published runs were on a workstation with 2× RTX PRO 6000 Blackwell (96 GB each, 600 W each at full uncapped operation), TR PRO 7965WX, 252 GB RAM. Smaller GPUs work but the published flags assume this configuration. Specifically: `--max-model-len 262144` and `--gpu-memory-utilization 0.92` will OOM on consumer 24-48 GB GPUs. `tooling/REPRODUCING.md` notes this; the cost.json files do not normalize for it.

Cost numbers in `cost.json` are upper-bound estimates (assume the GPU drew at its `power.limit` for the entire wall — real draw is lower). On different hardware, the same workload would have different absolute cost numbers; comparing cost.json across hardware setups requires renormalization.

### Quantization specificity

The local-model entries used 4-bit AWQ quantizations from the cyankiwi HuggingFace organization. Different quants of the same base model (FP8, BF16, different AWQ tools) will behave differently. The entries pin specific HuggingFace model paths in `launch-commands.md`; respect those when comparing.

#### Cyankiwi 4-bit AWQ field reports

As of 2026-05, multiple practitioners (in independent forum / community discussions) have reported that the Cyankiwi 4-bit AWQ quants of Qwen3.6-27B and Qwen3-Coder-Next underperform the official Qwen FP8 quants and Unsloth UD4 GGUFs of the same base models in their workflows. The reports describe degraded output coherence and increased loop pathologies on certain task shapes.

This benchmark uses Cyankiwi 4-bit AWQ throughout for three reasons:
1. Reproducible community release with stable HuggingFace paths
2. Fits the available VRAM-throughput envelope on Tower2 with room for `--max-model-len 262144` and large concurrency batches in the hardware-tests sweep
3. Consistent across all three model arms (apples-to-apples within the quant)

What this means for the data here:
- **Within-quant comparisons (Coder-Next vs 27B at the same Cyankiwi 4-bit AWQ) remain informative.** Differential behaviors — Coder-Next's `p3_market` 0/10 collapse, 27B's word-trim loop, the `--no-think` ship-rate jump — are model-mechanism findings that are unlikely to disappear at higher precision.
- **Absolute model capability at higher precisions (FP8 / Unsloth UD4 / BF16) is not characterized.** Headline numbers like "27B-no-think 95.8% ship rate" are quant-specific.
- **The ranking of cells where models tie at this quant could shift at FP8.** The both-ship cells (p2_ci, p2_extract, p2_triage) are the most likely to be sensitive.

The FP8 re-run of the same 12-cell grid is the highest-priority follow-up — see [`ROADMAP.md`](ROADMAP.md). Contributors with FP8-capable hardware are welcome to PR results via the [`tooling/ADDING-A-MODEL.md`](tooling/ADDING-A-MODEL.md) flow (which now explicitly covers the "same model, different quant" contribution path).

### Cloud-LLM hardware is different

Cloud entries (`Opus-4.7/`, `GPT-5.5/`) ran on the providers' inference infrastructure, not Tower2. Cross-comparison should account for that — "the cloud LLM is better" partly reflects "different hardware + different quantization-strategy + different inference engine," not just model differences.

## Security caveats — for replicators only

The harness exposes flags that give the model-controlled sandbox elevated access to the host. This is documented in `tooling/HARNESS-CHANGELOG.md` and per-flag in `harness.py --help`, but worth restating prominently:

- **`--docker-socket`**: bind-mounts `/var/run/docker.sock`. The sandbox can spawn sibling containers, kill containers, pull images. **Effectively root-equivalent on the host docker daemon.** Used during the PR-audit experiments so the agent could run `docker run ubuntu:22.04` for installer testing. **Do not enable this on a host you don't fully control.**
- **`--gh-token`**: passes a GitHub PAT into the sandbox via env var. The model can use it. If the token has write scopes, the model can in principle push commits, comment on issues, close PRs. We mitigated by either passing a read-only token or no token at all (the DreamServer repo is public, so unauth `git fetch` works for the PR-audit task) — but if you replicate, **mint a fine-scoped read-only token, and treat any token you pass as compromised after the run.**
- **`--gpus all`**: the sandbox shares GPU access with the host. The agent can run CUDA workloads, fingerprint hardware, exfiltrate via timing, etc. Not a privilege escalation per se, but worth knowing.

These flags exist because the benchmark tasks needed them. They are not appropriate for adversarial-input evaluations or for any setup where the model is untrusted.

## Comparison-to-cloud caveats

The cloud entries in this repo were not graded with the same scoring methodology as the local entries, because the local entries' grading was hand-done against ground truth on PR #1057 and the cloud entries' verdicts on the same PR aren't graded at the per-claim level here (Opus-4.7's broader audit covers PR #1057 in passing; GPT-5.5's similarly). So while both classes are present in this repo, **a direct head-to-head with consistent grading isn't currently published.**

That's the gap a future `RUBRIC.md` + per-entry `grade.json` would close. As of this writing, the cloud-vs-local comparison should be read at the *categorical* level ("cloud entries shipped complete deliverables; most local entries shipped failure modes") not at the per-claim accuracy level.

### `microbench-2026-04-28` is local-models-only

The microbench has no cloud-LLM entries at all. The 12 task families were run only on Qwen3.6-27B-AWQ and Qwen3-Coder-Next-AWQ. Headline reads from the microbench (e.g. "27B drives internet-research workflows that Coder-Next doesn't") apply *between local models*, not vs cloud. Cloud LLMs would almost certainly do as well or better on these tasks; the gap-vs-cloud is undocumented.

A future microbench expansion that runs Opus-4.7 / GPT-5.5 on the same task starters (using the same harness via API instead of vLLM) would close this. Until then: the microbench tells you which *local* model to use, not whether a local model is the right fit at all.

## What this repo can and can't support

**Can support**:
- "Here's what agentic 30B-class quantized local-model failures look like in detail."
- "Here are receipts + transcripts + cost numbers for replicating a specific run."
- "Here's a documented vocabulary for agentic failure modes" (`tooling/FAILURE-TAXONOMY.md`).
- "Here's evidence that the same model can ship structurally complete output and confidently wrong content in the same task."
- "Here's the harness that produced these runs, with its iterative-fix history."

**Can't support yet** (until rubric + larger N + cloud-rubric pass land):
- "This model is reliably better than that one for everyday work."
- "This model has X% factual accuracy."
- "Cost of operation is exactly $Y per task at production scale."
- "Cloud is N× better than local on this benchmark."

When in doubt: cite the specific run name and its receipt, not the model name in general.
