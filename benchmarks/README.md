# Benchmarks

Start here if your question is about model behavior on messy real-world tasks.
This tree is separate from `hardware-tests/`: these entries ask what a model
can actually produce when it has to research, code, audit, write, or build a
deliverable. Hardware throughput and buyer-value questions live in
[`../hardware-tests/README.md`](../hardware-tests/README.md).

## Reading Order

| If you want | Read first |
|---|---|
| Current model-selection synthesis | [`../COMPARISON.md`](../COMPARISON.md) |
| Single-table benchmark summary | [`../SCORECARD.md`](../SCORECARD.md) |
| Cross-cutting findings by date | [`findings-index.md`](findings-index.md) |
| How to replay or add a run | [`../tooling/README.md`](../tooling/README.md) |

## What Each Benchmark Answers

| Folder | Primary question | Best first file |
|---|---|---|
| [`dreamserver-75-pr-audit`](dreamserver-75-pr-audit/) | Can the model complete a long-horizon 75-PR maintainer audit at all? | [`dreamserver-75-pr-audit/README.md`](dreamserver-75-pr-audit/README.md) |
| [`dreamserver-1-pr-audit`](dreamserver-1-pr-audit/) | What is the floor task for local PR-audit competence? | [`dreamserver-1-pr-audit/README.md`](dreamserver-1-pr-audit/README.md) |
| [`wallstreet-intern-test`](wallstreet-intern-test/) | Can the model build a traceable investment memo and supporting artifacts? | [`wallstreet-intern-test/README.md`](wallstreet-intern-test/README.md) |
| [`microbench-2026-04-28`](microbench-2026-04-28/) | How do local models behave on 12 smaller task families at N=3? | [`microbench-2026-04-28/README.md`](microbench-2026-04-28/README.md) |
| [`microbench-phase-b-2026-05-02`](microbench-phase-b-2026-05-02/) | Which early microbench signals survive an N=10 expansion and 27B no-think arm? | [`microbench-phase-b-2026-05-02/README.md`](microbench-phase-b-2026-05-02/README.md) |

## Model Entry Shape

Most model-entry folders use some subset of these artifacts:

| File or folder | Meaning |
|---|---|
| `README.md` | Human-readable entry summary, caveats, and read order. |
| `grade.json` | Programmatic verdict and grader dimensions where a grader exists. |
| `label.json` | Failure-mode label from the repo taxonomy. |
| `receipt.json` | Model, harness, launch, token, and environment receipt. |
| `cost.json` | Wall time, token throughput, and rough energy/cost fields. |
| `summary.json` | Run-level finish reason and iteration/token totals. |
| `transcript.jsonl` | Full model/tool loop when the entry publishes it. |
| `deliverable/`, `report/`, `memo/`, `model/`, `prs/` | The actual artifacts the model produced. |

Read the benchmark README first, then the model-entry README, then the structured
JSON receipts before diving into transcripts or deliverables.

## Storage Notes

Some benchmark folders intentionally keep raw source documents, patches,
transcripts, and deliverables so claims stay auditable. Other entries are lean
on purpose and publish only receipts, grades, labels, and summaries. For the
repo-wide storage policy and current size hotspots, see
[`../REPO-SPACE.md`](../REPO-SPACE.md).
