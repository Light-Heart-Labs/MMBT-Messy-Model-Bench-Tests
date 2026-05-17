# How to read this repo

MMBT is a deliberately messy local-AI benchmark corpus. Two pages of writing per claim is normal; raw data and audit notes sit next to polished tables. That can be disorienting. This page tells you what to read first and how to weigh what you find.

## The 30-second tour

Start here, in order:

1. **`README.md`** — overall framing and current corpus state.
2. **`SCORECARD.md`** — one-table model selection guide.
3. **`COMPARISON.md`** — head-to-head model comparisons.
4. **`KNOWN-LIMITATIONS.md`** — caveats on what we measured.
5. **`NOT-HERE-YET.md`** — what we **didn't** measure (and where PRs are welcome).
6. **`claims.yaml`** — every claim in the repo with a status tag (strong / provisional / held / retracted).

If a number in this repo isn't in `claims.yaml`, it shouldn't be cited as a conclusion.

## The four altitudes

Everything in this repo lives at one of four altitudes. Higher means more polished, more confident; lower means more raw, more provisional.

```
            ┌──────────────────────────────────┐
            │ Reference layer                  │   README, SCORECARD, COMPARISON,
            │  (polished, narrow, stable)      │   KNOWN-LIMITATIONS, NOT-HERE-YET,
            │                                  │   claims.yaml, HOW-TO-READ
            └──────────────────────────────────┘
                          ▲
            ┌──────────────────────────────────┐
            │ Evidence layer                   │   hardware-tests/*/findings.md,
            │  (curated, claim-scoped)         │   benchmarks/*/findings.md, AUDIT.md,
            │                                  │   manifest.json, aggregate/headline.*
            └──────────────────────────────────┘
                          ▲
            ┌──────────────────────────────────┐
            │ Tooling layer                    │   hardware-tests/*/harness/,
            │  (reproducibility)               │   tooling/, agent-pilot/scripts/
            │                                  │
            └──────────────────────────────────┘
                          ▲
            ┌──────────────────────────────────┐
            │ Raw / archive layer              │   per-cell directories, .error files,
            │  (transparency, not load-bearing)│   power/thermal CSVs, retracted drafts,
            │                                  │   superseded findings docs
            └──────────────────────────────────┘
```

Read top-down. The Reference layer is what we stand behind. The Evidence layer is what we ran. The Tooling layer is how we ran it. The Raw layer is what came out — kept for transparency and reproducibility, not because we expect you to read it.

## Status vocabulary (used in `claims.yaml` and `manifest.json`)

| status | meaning |
|---|---|
| **canonical** | Load-bearing for a claim in this repo. Cite freely with attribution. |
| **provisional** | Single-study evidence; methodology sound but narrow. Cite with caveat. |
| **preliminary** | Present in the data, NOT yet a claim. Useful as a teaser of what's coming. |
| **held** | The data exists; we deliberately don't draw a conclusion (usually an engine or upstream constraint masks the question). |
| **retracted** | Was claimed in an earlier draft, now withdrawn. Kept findable for citation chasing. |
| **archive** | Older drafts kept for history; superseded by current Reference/Evidence layer. |
| **strong** | (for claims) Multiple independent reproducers, full audit, no known methodology gaps. We do not yet have anything tagged `strong`. |

If a claim doesn't carry a status, treat it as `provisional` at best.

## How to read a benchmark directory

Every benchmark bundle (e.g. `hardware-tests/qwen3.6-q8-fleet-2026-05-17/`) is shaped roughly like:

```
<bundle>/
├── README.md                  ← entry point — read this first
├── findings.md                ← the full write-up — read this second
├── AUDIT.md                   ← the rigor self-check — read this third if you're going to cite
├── manifest.json              ← machine-readable status (canonical/preliminary/etc)
├── NOTES-FOR-REVIEWERS.md     ← optional, asks for feedback on specific framings
├── aggregate/                 ← cross-cell rollups (CSV/JSON/TSV) — derived from raw
├── audit/                     ← claim-specific defenses (e.g. semantic-equivalence audits)
├── harness/                   ← vendored copy of the bench harness used (reproducibility)
├── workloads/                 ← the prompts/inputs used (SHA-pinned)
├── <host>/<model>/<backend>/  ← raw per-cell data (cell.json, inferences.jsonl, power.csv, thermals.csv)
└── sustained/                 ← supplementary studies (often labeled preliminary)
```

The first three files (`README.md`, `findings.md`, `AUDIT.md`) are the reading order for a serious reviewer. The aggregate CSVs let you redraw the report tables; the raw cells let you re-derive the aggregates; the harness lets you re-run from scratch.

## What to do if you find a discrepancy

- **Doc says X, table says Y** → trust the table, file an issue noting the doc drift.
- **Table says X, raw cells say Y** → trust the raw cells, file an issue noting aggregation drift.
- **Two files in the same bundle conflict** → check `manifest.json` for which is `canonical`; the other is likely `archive` or `superseded`.
- **A claim in `findings.md` isn't in `claims.yaml`** → file an issue; this is a process gap, not a finding.

## Where things are going

The corpus is being actively curated toward the structure above. Not every bundle has a `manifest.json` yet (the `qwen3.6-q8-fleet-2026-05-17` hardware bundle is the first); older bundles will get retrofitted. If you're reading an older bundle and the manifest is missing, treat its claims as `provisional` and check `claims.yaml` for the specific claim's status.

`NOT-HERE-YET.md` is the explicit roadmap of what's missing. If something you'd want to cite isn't there, it's either in NOT-HERE-YET (and you can wait or contribute) or it's a process gap (and you should file).
