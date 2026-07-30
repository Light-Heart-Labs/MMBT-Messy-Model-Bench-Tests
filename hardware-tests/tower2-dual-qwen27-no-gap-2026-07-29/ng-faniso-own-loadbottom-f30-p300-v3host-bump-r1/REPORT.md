# Own-fan 30% bottom-loaded 300 W safety bump

- Run: `2026-07-30T21-22-21Z-ng-faniso-own-loadbottom-f30-p300-v3host-bump-r1`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F30-P300-V3HOST-BUMP`
- Purpose: qualify the first 30% loaded-fan condition before 15-minute cells
- Measured window: 120 seconds after 120 seconds loaded warmup
- Result: **qualification pass; safety-only and never an inferential replicate**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean / maximum board power | 299.994 / 300.04 W | 21.944 / 25.81 W |
| Mean / maximum temperature | 53.584 / 57 C | 40.342 / 42 C |
| Mean fan duty | 30.0% | 50.0% |
| Mean physical fan RPM | 1,200.586 | 1,678.934 |
| Mean graphics clock | 1,035.3 MHz | 180.5 MHz |
| GPU utilization | 100% | 0% |
| SW/HW thermal or HW-brake active samples | 0 | 0 |

The V3HOST preflight held continuously for 303 seconds and ended at 29/31 C
GPUs, 54.4 C CPU Tctl, and 39.9 C hottest NVMe. GPU0 then held its 300 W cap
at 30% fan with 28 C of observed margin to the 85 C emergency cutoff. The idle
neighbor stayed below its 50 W isolation limit. Workload isolation, fan target
tracking, four-fan RPM telemetry, independent NVML clocks, sampled slowdown
counters, and automatic cleanup all passed.

The original run process returned nonzero because the first implementation of
the qualification command requested a hardware power-brake key not emitted in
`counter_deltas_us`. The authoritative sampled key,
`sampled_counter_deltas_us.hw_power_brake_counter_us`, exists and is zero for
both GPUs. Commit `5a10c2f` corrected that schema mismatch; the preserved raw
run then passed the corrected prospective gate without modification or rerun.
