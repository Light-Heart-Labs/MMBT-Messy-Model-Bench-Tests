# Bottom-card own-fan isolation at 70% - replicate 2

- Source run: `2026-07-30T23-40-55Z-ng-faniso-own-saturated-loadbottom-f70-v3host-15m-r2`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F70-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 2, sequence 2 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=2/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 22.340 W |
| Mean / maximum temperature | 50.840 / 53 C | 39.449 / 40 C |
| Last-five-minute temperature | 51.042 C | 40.000 C |
| Fan duty / mean physical RPM | 70% / 2,157.143 | 50% / 1,678.118 |
| Mean / last-five-minute graphics clock | 1,023.361 / 1,020.393 MHz | 180.373 / 180.250 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.814 seconds mean
request duration. Its closing five one-minute temperature medians were exactly
51/51/51/51/51 C. All frozen gates passed, and no software thermal, hardware
thermal, or hardware power-brake activity or counter growth occurred.

R2 moved 70% from third to second yet reproduced R1 within +0.026 C mean
temperature, -0.006 C last-five-minute temperature, -1.874 MHz mean clock, and
+0.004 seconds mean request duration. Relative to the R2 50% cell it removed
2.219 C but reduced mean clock by 3.543 MHz and increased mean request duration
by 0.081 seconds, closely repeating the R1 direction.
