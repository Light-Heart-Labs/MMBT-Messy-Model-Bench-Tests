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
| NG-SINGLE-B-250 | 1 | 3 | 0 | Replicate 2 admissible; two more internal replicates required |
| NG-SINGLE-T-250 | 3 | 3 | 0 | Within-campaign internally validated; cross-session and environmental validation pending |
| NG-SYM-600 | 0 | 3 | 0 | Known failed pilot; do not repeat unchanged |

`NG-SINGLE-T-250` is the first cell to reach three internally admissible replicates. Replicates 2, 4, and 5 were independently initialized execution blocks with cleanup/cooldown between them, but all occurred during one campaign session. The cell is therefore validated for the internal Tower2/no-gap model with an explicit within-session limitation. No cell is transferable yet.

[`VALIDATION_REGISTRY.csv`](VALIDATION_REGISTRY.csv) is the machine-readable run ledger. Every future run must declare a stable `cell_id` and `replicate`, and the registry must state whether it counts toward internal and transferable validation.

[`analysis/validation-aggregates.json`](analysis/validation-aggregates.json) and [`analysis/validation-aggregates.csv`](analysis/validation-aggregates.csv) are regenerated from the registry by `aggregate-validation.py`. They expose per-cell `n`, validation state, replicate membership, mean, sample standard deviation, coefficient of variation, and extrema for each modeled response.

## Immediate replication sequence

1. Complete three clean `NG-SINGLE-B-250` replicates.
2. Complete three clean `NG-SYM-250` anchor replicates, randomized across execution blocks with the isolation cells.
3. Repeat `NG-SINGLE-T-250` in a later session to quantify day/session effects.
4. Add calibrated environmental probes before promoting any cell to transferable status.
5. Expand to 400 W and 500 W only after the 250 W replicate variance and quality-control process are verified.
