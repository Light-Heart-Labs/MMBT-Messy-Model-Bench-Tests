# Repo Space And Data Layout

This repo stores benchmark evidence, not just prose. That makes it useful, but
it also means raw artifacts can grow quickly. The goal is to keep enough data
for claims to be auditable while avoiding duplicate or low-value bulk.

## Snapshot

Measured on the working tree on 2026-05-17:

| Area | Size |
|---|---:|
| `hardware-tests/` | 107.66 MiB |
| `hardware-tests/qwen3.6-q8-fleet-2026-05-17/` | 105.41 MiB |
| `benchmarks/` | 92.62 MiB |
| `tooling/` | 0.39 MiB |

Largest file families:

| Extension | Files | Raw size | Gzip size at level 6 | Potential saving |
|---|---:|---:|---:|---:|
| `.csv` | 909 | 77.04 MiB | 13.53 MiB | 82.4% |
| `.jsonl` | 753 | 30.56 MiB | 2.28 MiB | 92.5% |
| `.patch` | 150 | 22.72 MiB | 5.00 MiB | 78.0% |
| `.htm` | 33 | 26.88 MiB | 2.21 MiB | 91.8% |
| `.html` | 54 | 17.37 MiB | 2.17 MiB | 87.5% |

The only exact duplicate over 1 MiB found in this snapshot is the Qwen fleet
prompt corpus:

- `hardware-tests/qwen3.6-q8-fleet-2026-05-17/workloads/prompts.jsonl`
- `hardware-tests/qwen3.6-q8-fleet-2026-05-17/harness/workloads/prompts.jsonl`

Those files are byte-identical and cost about 6.07 MiB each. They were left in
place in this PR because the harness copy helps the vendored harness remain
standalone. A future cleanup can remove one copy if the harness default paths
are changed and verified.

## Keep In Git By Default

- `README.md`, findings, audit notes, manifests, and source-of-truth claim docs.
- Small structured receipts: `cell.json`, `grade.json`, `label.json`,
  `summary.json`, `cost.json`, and compact aggregate CSVs.
- Canonical headline tables used by published prose.
- Scripts needed to regenerate derived outputs.

## Compress Or Externalize By Default

- Long sampler time series such as `power.csv` and `thermals.csv`.
- Full `inferences.jsonl` and transcript JSONL files when a compact receipt is
  enough for the claim.
- Raw SEC filings, PDFs, HTML pages, and large patches that can be recovered
  from a source URL plus hash.
- Generated visual artifacts when the source data and render script are present.

If a large raw artifact is needed for auditability, prefer `*.gz` plus a
sidecar SHA256 file. If an artifact is needed only for archival completeness,
prefer a GitHub release asset or another immutable object store and keep the
URL, SHA256, byte count, and retrieval date in the repo.

## Suggested Next Cleanup

1. Decide whether published bundles must be runnable standalone, or only
   auditable inside the repo. That determines whether duplicate prompt corpora
   should stay.
2. Convert raw sampler CSVs and long JSONL traces to `*.gz`, then update readers
   and docs to treat compressed text as the canonical raw format.
3. Add a CI check that fails on exact duplicate files over 1 MiB unless the path
   is allowlisted in a manifest.
4. For new benchmark entries, require a README at every public landing folder
   and a manifest line for every large raw artifact.
