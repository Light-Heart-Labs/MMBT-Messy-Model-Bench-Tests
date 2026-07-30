# 300 W V3HOST fan-policy crossover - block 1

This is the first 300/300 W paired block using whole-system start gates. It
compares bottom/top fixed-fan allocations 60/40 and 40/60 at the same total
command, workload, power caps, 15-minute measured duration, and telemetry
settings. Each policy is independently admissible at `n=1/3`; this block is
preliminary and is not a validated causal estimate.

## Raw contrast

The 40/60 run minus the preceding 60/40 run produced:

| Response | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean temperature | -1.645 C | -1.925 C |
| Last-five-minute temperature | -2.006 C | -2.201 C |
| Mean graphics clock | +14.917 MHz | +3.228 MHz |
| Last-five-minute graphics clock | +17.094 MHz | +4.172 MHz |
| Request rate | 0.0000 req/s | 0.0000 req/s |

The mean top-minus-bottom temperature gap narrowed by 0.280 C. Combined mean
graphics clock rose by 18.145 MHz, but aggregate request throughput was
unchanged.

## Why this is not yet the fan effect

The reversed-policy run began from GPUs that were 3/2 C cooler and an NVMe
maximum that was 1 C cooler. During load, CPU Tctl averaged 1.930 C lower and
the hottest NVMe averaged 1.251 C lower. The full raw contrast therefore mixes:

1. fan allocation;
2. initial GPU/chassis heat state;
3. residual session and host-load variation; and
4. ordinary replicate noise.

The bottom card's result is directionally consistent with the validated 250 W
observation that lower own-fan RPM accompanies higher local clocks under a
constant total fan budget. The top card gained clock despite receiving more
fan RPM, however, demonstrating that cooler session/host state can dominate the
small local RPM-clock relationship. Neither direction should be promoted as a
300 W causal coefficient from this block.

## What V3HOST improved

The older GPU-only-reset 300 W blocks showed whichever policy ran second
becoming warmer. Here, the later run was cooler, and the start/host channels
make the reason visible instead of leaving it latent. V3HOST is therefore a
substantial comparability improvement, but one-sided maximum gates are not
exact matching.

Future blocks alternate policy order and require at least three admissible
replicates per policy. Paired interpretation must retain start GPU, CPU, and
NVMe values plus loaded host means as covariates. A block that exceeds the
prospective matching tolerances in `STEADY_STATE_PROTOCOL_V2.md` may still
contribute individual-cell replication but cannot be treated as a tightly
matched causal pair.

Machine-readable source: [`300w-v3host-fan-policy-block1.csv`](300w-v3host-fan-policy-block1.csv).
