# 500/500 W automatic-fan repeat R2 — excluded as nonsteady

- Run: `2026-07-31T21-56-47Z-no-gap-both500-10m-r2`
- Cell: `NG-SYM-500`, intended replicate 2
- Workload: independent Qwen3.6-27B AWQ-INT4 engine per GPU, 32 requests/GPU
- Warmup / measured / cooldown: 120 / 600 / 60 seconds
- Power: 500 W bottom / 500 W top
- Fan policy: NVIDIA automatic control on both cards
- Result: **completed safely but excluded from all validation counts**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 499.959 W | 499.981 W |
| Mean / last-5m / maximum temperature | 70.890 / 71.017 / 74 C | 89.623 / 89.718 / 93 C |
| Mean / maximum fan | 42.998 / 44% | 78.228 / 83% |
| Mean physical fan RPM | 1,515.607 | 2,354.127 |
| Mean / last-5m graphics clock | 2,514.734 / 2,514.419 MHz | 2,107.787 / 2,099.764 MHz |
| Mean request duration | 20.261 s | 20.925 s |
| Requests/s | 1.6000 | 1.5467 |
| Closing temperature slope | -0.0081 C/min | -0.2851 C/min |
| Closing fan slope | +0.1917 pp/min | **+0.3734 pp/min** |

Both GPUs held 100% utilization and approximately 500 W for the full measured
window. Isolation, completeness, power, fan telemetry, and automatic-policy
tracking gates passed. No sampled software-thermal, hardware-thermal, or
hardware-power-brake state was active. GPU1 accumulated 780,134 microseconds
of software-thermal counter time (0.130% of the measured window); hardware
thermal and power-brake counter deltas were zero.

GPU1 failed the preregistered steady-state gate because its automatic fan was
still increasing at +0.3734 percentage points/minute over the closing window.
The falling temperature and continuing fan ramp show that the controller had
not reached equilibrium even after ten measured minutes. The run therefore
does not count as replicate 2 and contributes no response to the validated
`NG-SYM-500` aggregate. A future clean replacement must use at least a
15-minute measured window while retaining the 94 C emergency cutoff.

