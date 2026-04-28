# microbench-2026-04-28

> 12 task families, 2 local models, N=3 each. Smaller-scope tasks than the dreamserver-PR-audit / wallstreet-intern-test benchmarks above — each task is a 5-30 minute deliverable rather than a multi-hour audit. Designed to surface task-class-specific differences between Qwen3.6-27B-AWQ and Qwen3-Coder-Next-AWQ that the larger benchmarks couldn't isolate.

## Read these first

- [`findings.md`](findings.md) — cross-cutting writeup. Headline reads, daily-driver-guide updates, caveats. Read this before drilling into individual task-family folders.
- [`../../SCORECARD.md`](../../SCORECARD.md) § "microbench-2026-04-28" — single-table summary with PASS rates, costs, walls.

## What's published here

This benchmark has 12 task families and would produce 60+ per-model folders if every cell were published in full. To avoid bloating the repo, **all 12 task families have entries — but published at two levels of detail**:

**Three highest-signal task families: full per-model entries** (with transcripts and complete deliverable bundles):

| Task family | Why it's here | 27B | Coder-Next |
|---|---|---|---|
| [`adversarial-hallucination/`](adversarial-hallucination/) | Sharpest local-model superiority signal in the entire suite. 27B 100% accurate / 0 dangerous; Coder-Next 1/3 PASS, 2/3 stuck-detector fired, the one shipping run had 2 fabrications-confirmed-as-real. | [Qwen3.6-27B-AWQ/](adversarial-hallucination/Qwen3.6-27B-AWQ/) | [Qwen3-Coder-Next-AWQ/](adversarial-hallucination/Qwen3-Coder-Next-AWQ/) |
| [`market-research/`](market-research/) | Second-sharpest signal — and an inversion of the "both fail at internet research" expectation. 27B 3/3 STRUCTURAL_PASS (5 products, 12-18 inline cites to 29-33 distinct URLs); Coder-Next 0/3 STRUCTURAL_FAIL (no required output files produced). | [Qwen3.6-27B-AWQ/](market-research/Qwen3.6-27B-AWQ/) | [Qwen3-Coder-Next-AWQ/](market-research/Qwen3-Coder-Next-AWQ/) |
| [`doc-synthesis/`](doc-synthesis/) | Documented 27B failure mode — 8/8 planted facts captured every run, but 0/3 PASS because model couldn't trim to the 700-word limit. Two of three runs entered identical-call-loops on `brief.md`. Coder-Next handled the same task-class better (2/3 PASS). | [Qwen3.6-27B-AWQ/](doc-synthesis/Qwen3.6-27B-AWQ/) | [Qwen3-Coder-Next-AWQ/](doc-synthesis/Qwen3-Coder-Next-AWQ/) |

**Nine other task families: lean entries** (per-model README + cost.json + grade.json + label.json + summary.json + receipt.json — no transcripts or deliverables to keep the repo size manageable):

| Task family | 27B | Coder-Next | Headline |
|---|---|---|---|
| [`bug-fixing/`](bug-fixing/) | 3/3 PASS | 2/3 PASS | Both can fix planted bugs; 27B more reliable, Coder-Next faster |
| [`test-writing/`](test-writing/) | 0/3 † | 0/3 † | Task-design issue (broken starter import) — see findings.md caveat |
| [`refactoring/`](refactoring/) | 0/3 † | 0/3 † | Same task-design issue |
| [`structured-extraction/`](structured-extraction/) | 3/3 PASS | 3/3 PASS | 27B 100% on 20 fields; Coder-Next ~92% & 4× cheaper |
| [`ci-failure-debugging/`](ci-failure-debugging/) | 3/3 PASS | 3/3 PASS | Both clean; pick the cheaper |
| [`customer-support-triage/`](customer-support-triage/) | 3/3 PASS | 3/3 PASS | **Coder-Next 96.7% > 27B 86.7%** category accuracy AND faster AND cheaper |
| [`business-memo/`](business-memo/) | 2/3 PASS | 3/3 PASS | Both reliable on bias-detection; Coder-Next ships within word limit consistently |
| [`writing-editing/`](writing-editing/) | 0/3 | 2/3 PASS | 27B's 0/3 is a single-keyword miss on customer email (CEO + legal pass 5/5 every run) |
| [`project-management/`](project-management/) | 0/3 | 1/3 PASS | Both excellent on workstreams + decisions, both 2-3/6 on multi-week risks |

For the 9 lean entries, transcripts and deliverable artifacts are not mirrored in MMBT (to keep repo size manageable) but the **task prompts, input starters, ground truth, and grader scripts are all in `tooling/`** — meaning a reader with the right hardware can rerun any of these task families and produce their own transcripts + deliverables. See [`tooling/REPRODUCING.md`](../../../tooling/REPRODUCING.md) § "Reproducing the microbench" for the walkthrough.

## Per-entry layout

Each model entry under a published task family has:

- `README.md` — entry-specific writeup (this file is the per-model commentary)
- `cost.json` — wall, tokens, GPU, energy upper bound
- `grade.json` — programmatic verdict (PASS/FAIL/STRUCTURAL_PASS/etc) with per-dimension scores
- `label.json` — failure-mode classification per `tooling/FAILURE-TAXONOMY.md`
- `receipt.json` — exact vLLM args, harness git SHA, GPU snapshot
- `summary.json` — finish reason, iteration count, total tokens
- `transcript.jsonl` — full agent loop (model calls + tool calls + results)
- `deliverable/` — the actual artifacts the agent produced

Read `cost.json` + `grade.json` + `label.json` first — that's the headline. Then `summary.json` for run shape. Then drill into `deliverable/` for the actual output, and `transcript.jsonl` for the play-by-play of how it got there.

## Run config

All runs used:
- vLLM with `--max-model-len 262144`, `--temperature 0.3`, model-specific reasoning/tool parsers
- Harness with `--stuck-threshold 500` (long-horizon-friendly), `--docker-socket --gpus all`
- Sandbox: bench/agent-pilot/Dockerfile (Python 3.11 + git + curl + standard tools)
- Hardware: Tower2, 2× NVIDIA RTX PRO 6000 Blackwell Workstation Edition, AMD Threadripper PRO 7965WX, 252 GB RAM, 1600W PSU on dedicated 20A circuit. See `tooling/REPRODUCING.md` for the reproduction walkthrough.

Per-task starter inputs (the planted facts, schemas, audience briefs, etc.) are in this repo's `tooling/` folder (see [`tooling/REPRODUCING.md`](../../tooling/REPRODUCING.md) § "Reproducing the microbench")'s `agent-pilot/inputs/phase[2-3]_*/` directories. The ground-truth files (planted answers) live in `agent-pilot/graders/ground_truth/` to keep them out of the agent-mountable input dirs — verified pre-launch.

## Caveats

- **N=3 per cell.** Confidence intervals are wide. The point estimates above are not population estimates.
- **Hand-grading placeholders.** Phase 3 graders include subjective dimensions (prose quality 1-5, fabrication count, audience-tone fit, citation validity) that are placeholder fields awaiting human grading. The PASS/FAIL above is from the programmatic axis only — the structural pass on `market-research` does not assert citation validity.
- **Task-design issue.** `p1_testwrite` and `p1_refactor` use a shared starter (`logalyzer/`) with a known broken import (`from collections import Iterable` — Python 3.10+ removed this). Both models 0/3 PASS on these. The failure is a task-design / fix-the-starter question, not pure model failure. See findings.md § "Test-writing and refactoring task-design issue".
- **Two manually-advanced 27B runs.** `p3_doc_27b_v2` and `p3_doc_27b_v3` were SIGTERM'd mid-run after entering identical-call-loops (50-130+ writes of the same `brief.md` content, never able to compress to the 700-word limit). The chain advanced rather than waiting 5+ hours for the stuck-detector at iter 500. The pattern is documented as a 27B failure shape in `findings.md`, not a transient bug. Manual-advance summaries in those runs' `summary.json` mark them `wall_killed_identical_call_loop`.
