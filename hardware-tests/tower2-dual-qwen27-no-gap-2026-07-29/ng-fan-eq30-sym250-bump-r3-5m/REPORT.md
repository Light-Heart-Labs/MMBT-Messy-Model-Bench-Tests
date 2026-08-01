# Fixed-fan 250/250 W bump R3 — five-minute extension

- Run: `2026-07-30T03-22-46Z-ng-fan-eq30-sym250-bump-r3-5m`
- Cell: `NG-FAN-EQ30-SYM250-BUMP`
- Measured window: 5 minutes after 60 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: both physical fans on each card fixed at 30%
- Safety cutoff: 85°C
- Result: **successful safety extension; excluded as non-steady**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.975 W | 249.994 W |
| Mean / maximum temperature | 49.675 / 54°C | 62.276 / 70°C |
| End-of-window observed temperature | 52°C | 69°C |
| Mean commanded/current fan | 30.0% / 30.0% | 30.0% / 30.0% |
| Mean physical fan RPM | 1,200.594 | 1,200.674 |
| Mean graphics clock | 812.494 MHz | 791.243 MHz |
| Closing temperature slope | +0.7606°C/min | +2.1283°C/min |
| Completed request rate | 0.9600 req/s | 0.9600 req/s |

The equal-fan policy was maintained throughout: both fixed-policy quality gates
passed, all four fan streams were complete, and mean card-level RPM differed
by only 0.080 RPM. All thermal and hardware power-brake event counts remained
zero. Automatic fan control and both 600 W limits were verified after cleanup.

The top-minus-bottom mean temperature difference was 12.601°C; the
end-of-window observation was 17°C. The bottom card was approaching a plateau,
while the top still warmed at +2.1283°C/min over the closing three-minute
window. The trajectory bent substantially from R2's initial +6.199°C/min top
slope, but did not reach the <0.1°C/min steady-state criterion.

This establishes that 250/250 W at fixed 30/30% fans remains below the 85°C
safety boundary through five measured minutes. It does not yet establish an
equilibrium temperature. A guarded ten-minute extension is justified by the
observed 70°C maximum and 23°C remaining margin, but remains subject to the
same cutoff.
