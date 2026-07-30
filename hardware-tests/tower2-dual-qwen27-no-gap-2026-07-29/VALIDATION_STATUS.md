# Validation status

Validation requires at least three admissible independent replicates (`n >= 3`). Aborted, contaminated, non-steady, or otherwise excluded pilots remain published but do not count toward `n`.

Two validation levels are tracked:

- **Internal:** suitable for a Tower2/no-gap empirical model using GPU and workload telemetry.
- **Transferable:** additionally includes calibrated ambient and local-inlet measurements required for chassis/server design claims.

## Current counts

| Cell | Internal admissible | Required | Transferable admissible | Status |
|---|---:|---:|---:|---|
| NG-SYM-250 | 0 | 3 | 0 | Clean n=3 campaign required |
| NG-SYM-500 | 1 | 3 | 0 | Two internal replicates plus environmental instrumentation required |
| NG-ASYM-600-400 | 1 | 3 | 0 | Two internal replicates plus environmental instrumentation required |
| NG-SINGLE-B-250 | 0 | 3 | 0 | Clean n=3 campaign required |
| NG-SINGLE-T-250 | 2 | 3 | 0 | Replicates 2 and 4 admissible; one more internal replicate required |
| NG-SYM-600 | 0 | 3 | 0 | Known failed pilot; do not repeat unchanged |

No cell is validated yet. Existing results are pilots, boundary evidence, or individual admissible internal replicates.

[`VALIDATION_REGISTRY.csv`](VALIDATION_REGISTRY.csv) is the machine-readable run ledger. Every future run must declare a stable `cell_id` and `replicate`, and the registry must state whether it counts toward internal and transferable validation.

[`analysis/validation-aggregates.json`](analysis/validation-aggregates.json) and [`analysis/validation-aggregates.csv`](analysis/validation-aggregates.csv) are regenerated from the registry by `aggregate-validation.py`. They expose per-cell `n`, validation state, replicate membership, mean, sample standard deviation, coefficient of variation, and extrema for each modeled response.

## Immediate replication sequence

1. Cleanly isolate and repeat `NG-SINGLE-T-250` until three admissible replicates exist.
2. Complete three clean `NG-SINGLE-B-250` replicates.
3. Complete three clean `NG-SYM-250` anchor replicates, randomized across sessions with the isolation cells.
4. Add calibrated environmental probes before promoting any cell to transferable status.
5. Expand to 400 W and 500 W only after the 250 W replicate variance and quality-control process are verified.
