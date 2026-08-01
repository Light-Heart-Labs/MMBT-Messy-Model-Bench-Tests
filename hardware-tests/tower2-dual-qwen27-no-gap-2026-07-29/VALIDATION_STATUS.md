# Validation status

Validation requires at least three admissible independent replicates (`n >= 3`). Aborted, contaminated, non-steady, or otherwise excluded pilots remain published but do not count toward `n`.

Two validation levels are tracked:

- **Internal:** suitable for a Tower2/no-gap empirical model using GPU and workload telemetry.
- **Transferable:** additionally includes calibrated ambient and local-inlet measurements required for chassis/server design claims.

## Current counts

| Cell | Internal admissible | Required | Transferable admissible | Status |
|---|---:|---:|---:|---|
| NG-SYM-250 | 1 | 3 | 0 | Replicate 2 thermally admissible; clock channel flagged; two more internal replicates required |
| NG-SYM-500 | 1 | 3 | 0 | R2 10-minute repeat completed but is excluded because GPU1 automatic fan remained at +0.3734 pp/min; two 15-minute internal replicates plus environmental instrumentation required |
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
| NG-FAN-B60-T40-SYM300-V3HOST-15M | 3 | 3 | 0 | Internally validated at n=3; R3 includes an admitted sub-second GPU0 request-boundary transient; paired blocks show clock/latency redistribution but weak thermal effect |
| NG-FAN-B40-T60-SYM300-V3HOST-15M | 3 | 3 | 0 | Internally validated at n=3; tightly matched blocks 2/3 repeat clock/latency redistribution while the apparent thermal advantage does not reproduce |
| NG-FANISO-OWN-LOADBOTTOM-F30-V3HOST-15M | 3 | 3 | 0 | Internally validated; all three Latin-order blocks passed; 30-to-50% thermal and latency improvements are paired-block consistent |
| NG-FANISO-OWN-LOADBOTTOM-F50-V3HOST-15M | 3 | 3 | 0 | Internally validated; best observed mean latency/clock point in the completed own-fan sweep |
| NG-FANISO-OWN-LOADBOTTOM-F70-V3HOST-15M | 3 | 3 | 0 | Internally validated; maximum tested local/neighbor cooling with a repeated latency penalty versus 50% |
| NG-FANISO-NEIGHBOR-LOADTOP-F30-V3HOST-15M | 3 | 3 | 0 | Internally validated; all three Latin-order blocks passed |
| NG-FANISO-NEIGHBOR-LOADTOP-F50-V3HOST-15M | 3 | 3 | 0 | Internally validated; monotonic intermediate thermal/performance response |
| NG-FANISO-NEIGHBOR-LOADTOP-F70-V3HOST-15M | 3 | 3 | 0 | Internally validated; 30-to-70% lower-fan assistance removed 4.984 C from loaded top mean temperature |
| NG-FAN-EQ50-SYM350-V3HOST-15M | 3 | 3 | 0 | Internally validated; stable equal 50/50 reference across all three blocks |
| NG-FAN-B40T60-SYM350-V3HOST-15M | 3 | 3 | 0 | Internally validated; direction-reversed comparison passed all three blocks |
| NG-FAN-B60T40-SYM350-V3HOST-15M | 3 | 3 | 0 | Internally validated; lower-biased allocation improved top clock and latency in every paired block |
| NG-FAN-EQ50-SYM400-V3HOST-15M | 1 | 3 | 0 | R1 admissible but marginal at 84 C maximum; original 100-point budget retired at 400 W |
| NG-FAN-B60T40-SYM400-V3HOST-15M | 0 | 3 | 0 | R1 safety-aborted at 85 C after ~4 measured minutes; do not repeat unchanged |
| NG-FAN-B40T60-SYM400-V3HOST-15M | 0 | 3 | 0 | Not run because the R1 block correctly fail-stopped after B60T40 |
| NG-FAN-EQ60-SYM400-V3HOST-15M | 3 | 3 | 0 | Internally validated; all three rotated blocks held 400 W/100% with exact fan/RPM tracking and zero thermal/brake events |
| NG-FAN-B50T70-SYM400-V3HOST-15M | 3 | 3 | 0 | Internally validated; clean R3 restarted after a separately retained user-interrupted attempt |
| NG-FAN-B70T50-SYM400-V3HOST-15M | 3 | 3 | 0 | Internally validated; versus B50T70, top last-5m temperature -0.876 C and clock +22.874 MHz with 95% CIs excluding zero |
| NG-SYM-600 | 0 | 3 | 0 | Known failed pilot; do not repeat unchanged |

`NG-SINGLE-T-250` is the first cell to reach three internally admissible replicates. Replicates 2, 4, and 5 were independently initialized execution blocks with cleanup/cooldown between them, but all occurred during one campaign session. The cell is therefore validated for the internal Tower2/no-gap model with an explicit within-session limitation. No cell is transferable yet.

[`VALIDATION_REGISTRY.csv`](VALIDATION_REGISTRY.csv) is the machine-readable run ledger. Every future run must declare a stable `cell_id` and `replicate`, and the registry must state whether it counts toward internal and transferable validation. The optional `metric_exclusions` field removes quality-flagged channels from aggregation without discarding otherwise admissible thermal or workload evidence.

[`analysis/validation-aggregates.json`](analysis/validation-aggregates.json) and [`analysis/validation-aggregates.csv`](analysis/validation-aggregates.csv) are regenerated from the registry by `aggregate-validation.py`. They expose per-cell `n`, validation state, replicate membership, mean, sample standard deviation, coefficient of variation, and extrema for each modeled response.

## Immediate replication sequence

1. Build the cross-power evidence-grade table from validated 250, 350, and 400 W fixed-fan populations; keep 200/300 W order-confounded estimates explicitly provisional.
2. Complete missing clean anchor replicates (`NG-SINGLE-B-250`, `NG-SYM-250`, and `NG-SYM-500`) only when their information gain exceeds another matched crossover.
3. Validate the stack-aware background fan controller against matched static policies, including fail-safe restoration and service-restart behavior.
4. Repeat key cells after restoring a physical gap to identify the spacing-response coefficient.
5. Add calibrated ambient and per-card inlet probes before promoting any cell or 3x/4x forecast to transferable server-design status.
