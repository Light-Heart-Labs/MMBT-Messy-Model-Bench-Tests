# Validated 300 W V3HOST fan-policy analysis

Both fixed-fan policies now contain three internally admissible runs. The
per-policy `n=3` populations establish repeatability, while only crossover
blocks 2 and 3 meet the prospective start/host matching rule closely enough
for the causal policy contrast. Block 1 remains in the public record but is
excluded from that contrast because its session state differed materially.

## Matched two-block estimate

Values are the mean of block-2 and block-3 effects, reported as bottom/top
60/40 minus 40/60:

| Response | GPU0 / bottom | GPU1 / top | Combined |
|---|---:|---:|---:|
| Mean temperature | -0.394 C | -0.146 C | -0.540 C |
| Last-five-minute temperature | -0.509 C | -0.044 C | -0.553 C |
| Mean graphics clock | -7.859 MHz | +5.556 MHz | -2.303 MHz |
| Last-five-minute graphics clock | -8.426 MHz | +5.269 MHz | -3.157 MHz |
| Mean request duration | +0.135 s | -0.172 s | -0.038 s |
| Request rate | 0.0000 req/s | 0.0000 req/s | 0.0000 req/s |

## What is validated

The repeatable result is a small **redistribution** of clock and latency:
assigning more fan RPM to a card lowers that card's clock and lengthens its
request duration, while the lower-RPM card moves oppositely. Total request
rate is unchanged and combined clock changes only slightly.

The thermal effect is not robust. Block 2 cooled both cards by
0.777/0.508 C; block 3 changed them by -0.011/+0.216 C. Averaging yields a
small apparent benefit, but its sign/magnitude is not sufficiently stable to
claim that bottom-biased airflow reliably cools both cards at 300 W. The
250 W result remains stronger; the power-by-fan-policy interaction is itself
an important finding.

The likely local fan-power tax remains a hypothesis because fan electrical
power is not independently metered. Own-fan and neighbor-fan isolation sweeps
are required to separate fan electrical consumption, local cooling, and
shared through-stack airflow.

Machine-readable effects:
[`300w-v3host-fan-policy-effects-n3.csv`](300w-v3host-fan-policy-effects-n3.csv).
