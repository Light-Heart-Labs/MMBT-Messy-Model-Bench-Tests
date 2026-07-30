# Validation status

Validation requires at least three admissible independent replicates (`n >= 3`). Aborted, contaminated, non-steady, or otherwise excluded pilots remain published but do not count toward `n`.

Two validation levels are tracked:

- **Internal:** suitable for a Tower2/no-gap empirical model using GPU and workload telemetry.
- **Transferable:** additionally includes calibrated ambient and local-inlet measurements required for chassis/server design claims.

## Current counts

| Cell | Internal admissible | Required | Transferable admissible | Status |
|---|---:|---:|---:|---|
| NG-SYM-250 | 1 | 3 | 0 | Replicate 2 thermally admissible; clock channel flagged; two more internal replicates required |
| NG-SYM-500 | 1 | 3 | 0 | Two internal replicates plus environmental instrumentation required |
| NG-ASYM-600-400 | 1 | 3 | 0 | Two internal replicates plus environmental instrumentation required |
| NG-SINGLE-B-250 | 1 | 3 | 0 | R2 admissible; R3 excluded as non-steady after prior heat soak; two more internal replicates required |
| NG-SINGLE-T-250 | 3 | 3 | 0 | Within-campaign internally validated; cross-session and environmental validation pending |
| NG-FAN-EQ30-SYM250 | 1 | 3 | 0 | R1 admissible; R2/R3 closely reproduced it but failed the quantization-sensitive strict slope gate; define a prospective v2 plateau rule before further repeats |
| NG-FAN-EQ50-SYM250-V2-15M | 3 | 3 | 0 | Internally validated at n=3 with tight thermal, RPM, and throughput repeatability |
| NG-FAN-B70-T30-SYM250-V2-15M | 3 | 3 | 0 | Internally validated at n=3; all replicates repeated the cooler, more clock-balanced operating point |
| NG-FAN-B30-T70-SYM250-V2-15M | 3 | 3 | 0 | Internally validated at n=3; all replicates repeated the top throughput and clock deficit |
| NG-FAN-B60-T40-SYM250-V2-15M | 3 | 3 | 0 | Internally validated at n=3; frozen temperature interpolation error was +0.020/+0.277 C |
| NG-FAN-B40-T60-SYM250-V2-15M | 3 | 3 | 0 | Internally validated at n=3; frozen temperature interpolation error was +0.156/+0.584 C |
| NG-FAN-B40-T60-SYM200-V2-15M | 3 | 3 | 0 | Internally validated at n=3; completed paired crossover exposes execution-order/session heat as a material nuisance variable |
| NG-FAN-B60-T40-SYM200-V2-15M | 3 | 3 | 0 | Internally validated at n=3; block 3 reverses order and confirms session/heat-soak drift must be modeled |
| NG-FAN-B60-T40-SYM300-V2-15M | 2 | 3 | 0 | R1/R2 admissible; reversed block confirms later-run heat bias; one more replicate required |
| NG-FAN-B40-T60-SYM300-V2-15M | 2 | 3 | 0 | R1/R2 admissible with exact throughput reproduction; one more replicate and paired 60/40 blocks required |
| NG-FAN-B60-T40-SYM300-V3HOST-15M | 1 | 3 | 0 | First whole-system-reset replicate passed; raw campaign label R3 retained; two V3HOST replicates required |
| NG-FAN-B40-T60-SYM300-V3HOST-15M | 1 | 3 | 0 | First paired whole-system-reset replicate passed; raw contrast remains baseline/host-state confounded; two replicates required |
| NG-SYM-600 | 0 | 3 | 0 | Known failed pilot; do not repeat unchanged |

`NG-SINGLE-T-250` is the first cell to reach three internally admissible replicates. Replicates 2, 4, and 5 were independently initialized execution blocks with cleanup/cooldown between them, but all occurred during one campaign session. The cell is therefore validated for the internal Tower2/no-gap model with an explicit within-session limitation. No cell is transferable yet.

[`VALIDATION_REGISTRY.csv`](VALIDATION_REGISTRY.csv) is the machine-readable run ledger. Every future run must declare a stable `cell_id` and `replicate`, and the registry must state whether it counts toward internal and transferable validation. The optional `metric_exclusions` field removes quality-flagged channels from aggregation without discarding otherwise admissible thermal or workload evidence.

[`analysis/validation-aggregates.json`](analysis/validation-aggregates.json) and [`analysis/validation-aggregates.csv`](analysis/validation-aggregates.csv) are regenerated from the registry by `aggregate-validation.py`. They expose per-cell `n`, validation state, replicate membership, mean, sample standard deviation, coefficient of variation, and extrema for each modeled response.

## Immediate replication sequence

1. Complete three clean `NG-SINGLE-B-250` replicates.
2. Complete three clean `NG-SYM-250` anchor replicates, randomized across execution blocks with the isolation cells.
3. Repeat `NG-SINGLE-T-250` in a later session to quantify day/session effects.
4. Add calibrated environmental probes before promoting any cell to transferable status.
5. Expand to 400 W and 500 W only after the 250 W replicate variance and quality-control process are verified.
