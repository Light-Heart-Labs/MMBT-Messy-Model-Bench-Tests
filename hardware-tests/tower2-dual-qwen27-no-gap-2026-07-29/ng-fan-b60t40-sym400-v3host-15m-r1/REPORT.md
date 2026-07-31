# 400/400 W B60T40 fixed-fan R1 safety abort

- Run: `2026-07-31T13:30:58Z-ng-fan-b60t40-sym400-v3host-15m-r1`
- Cell: `NG-FAN-B60T40-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **safety abort; excluded from validation**

The independent 1 Hz guard stopped the run when GPU1/top reached the frozen
85 C cutoff after approximately 4.0 of 15 measured minutes. The block runner
then restored automatic fan control, 600 W power limits, production
containers, and services, and correctly prohibited the third policy.

| Partial-window metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Samples | 968 | 968 |
| Mean board power | 399.991 W | 399.994 W |
| Mean / maximum temperature | 62.467 / 67 C | 78.043 / 85 C |
| Fan / mean RPM | 60% / 1,917.341 | 40% / 1,439.136 |
| Mean graphics clock | 1,750.913 MHz | 1,523.657 MHz |
| Temperature slope | positive | +2.091 C/min |

The emergency sample printed nonzero lifetime thermal counters, but the
audited GPU1 baselines and final samples were identical: software thermal
6,894,602 to 6,894,602 microseconds and hardware thermal 280,003 to 280,003
microseconds. Sampled slowdown flags were also inactive throughout. This is a
temperature safety-boundary result, not observed NVIDIA thermal throttling.

The partial window was incomplete and non-steady and does not count toward
`n`. [`partial-summary.json`](partial-summary.json) and
[`thermal-stress.png`](thermal-stress.png) preserve the diagnostic aggregate
and time series.
