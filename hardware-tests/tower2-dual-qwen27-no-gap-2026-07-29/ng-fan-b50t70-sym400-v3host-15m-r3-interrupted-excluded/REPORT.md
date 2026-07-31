# Interrupted 400/400 W B50T70 attempt — excluded

- Run: `2026-07-31T18-46-37Z-ng-fan-b50t70-sym400-v3host-15m-r3`
- Intended cell: `NG-FAN-B50T70-SYM400-V3HOST-15M`, replicate 3
- Result: **user-interrupted during the first measured cell; excluded from all inference**

The campaign was stopped for an acoustically quiet call approximately three
minutes into the measured window. The remote process group required an
explicit interrupt and the machine was then placed in a verified quiet state:
zero GPU utilization, no compute processes, and both card fans at 30%.

This directory preserves the partial raw telemetry and operational record for
auditability. It has no completed summary, did not pass the preregistered
duration or cleanup gates, and contributes no samples to R3 or any fitted
effect. The subsequent clean R3 block restarted from the beginning.

