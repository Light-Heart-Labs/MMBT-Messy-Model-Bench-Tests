# Fixed-fan 250/250 W bump R2 — successful control validation

- Run: `2026-07-30T03-03-17Z-ng-fan-eq30-sym250-bump-r2`
- Cell: `NG-FAN-EQ30-SYM250-BUMP`
- Measured window: 2 minutes after 60 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: both physical fans on each card fixed at 30%
- Safety cutoff: 85°C
- Result: **successful bump; excluded from steady-state validation**

## Measured result

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 48.116 / 51°C | 57.321 / 64°C |
| End-of-window temperature | 50°C | 63°C |
| Mean commanded/current fan | 30.0% / 30.0% | 30.0% / 30.0% |
| Mean physical fan RPM | 1,201.017 | 1,201.404 |
| Mean graphics clock, primary | 814.911 MHz | 802.017 MHz |
| Mean graphics clock, independent NVML | 814.659 MHz | 801.806 MHz |
| Mean GPU utilization | 100% | 100% |
| Closing temperature slope | +2.8106°C/min | +6.1990°C/min |

All four physical fans delivered 120/120 expected measured samples. Each stayed
at exactly 30% target/current duty; individual RPMs remained between 1,198 and
1,205. Both GPU manual-control states were observed as `1` during load and
verified as `0` after automatic restoration.

No software-thermal, hardware-thermal, or hardware power-brake event was
observed. The software power-cap reason was expected because both cards held
their 250 W limits.

## Interpretation

This is the first successful loaded proof that Tower2 can independently control
and continuously verify all four GPU fans. At identical power and essentially
identical physical fan RPM, the top card averaged 9.205°C hotter and ended
13°C hotter. Its temperature also rose more than twice as fast over the short
window.

The bump is intentionally not a steady-state result: both temperature slopes
are far outside the admissibility threshold. It cannot yet answer what the
equilibrium top-position penalty is at 30% fan, nor can it be compared as an
equilibrium coefficient against the automatic-fan 250/250 cell. It validates
the control and safety path needed to collect that evidence.

The next 30/30 exposure should extend cautiously with the same 85°C cutoff
before attempting a standard 10-minute cell. Crossed-fan tests then determine
whether extra bottom-card airflow lowers the hotter top card's trajectory.
