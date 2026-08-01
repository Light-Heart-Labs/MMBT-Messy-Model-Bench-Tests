# Validated 400/400 W 120-point fixed-fan study (`n=3`)

Three independently initialized 15-minute blocks completed with rotated order:

- R1: EQ60, B70T50, B50T70
- R2: B70T50, B50T70, EQ60
- R3: B50T70, EQ60, B70T50

All nine cells passed isolation, saturated-power, fan/RPM tracking,
independent-clock, completeness, quantized steady-state, and slowdown-counter
gates. Each GPU averaged approximately 400 W at 100% utilization. There were
zero software-thermal, hardware-thermal, or hardware-power-brake events and
zero corresponding thermal/brake counter deltas.

| Policy | Top mean temp | Top last-5m temp | Top mean clock | Top last-5m clock | Top mean latency | Bottom mean temp |
|---|---:|---:|---:|---:|---:|---:|
| EQ60 | 77.056 C | 78.508 C | 1,521.845 MHz | 1,499.337 MHz | 22.673 s | 61.666 C |
| B70T50 | 76.188 C | 77.148 C | 1,539.177 MHz | 1,523.985 MHz | 22.581 s | 60.872 C |
| B50T70 | 76.545 C | 78.024 C | 1,522.446 MHz | 1,501.111 MHz | 22.671 s | 61.520 C |

## Direction-reversed paired effect

The causal contrast is B70T50 minus B50T70: identical total commanded fan
duty, near-identical total physical RPM, but opposite allocation between the
lower and upper cards.

| Response | R1 | R2 | R3 | Paired mean | 95% CI (Student t, df=2) |
|---|---:|---:|---:|---:|---:|
| Top mean temperature | -0.567 C | -0.853 C | +0.349 C | -0.357 C | [-1.917, +1.203] C |
| Top last-5m temperature | -0.961 C | -0.980 C | -0.688 C | **-0.876 C** | **[-1.282, -0.470] C** |
| Top mean clock | +19.177 MHz | +25.309 MHz | +5.705 MHz | +16.730 MHz | [-8.182, +41.642] MHz |
| Top last-5m clock | +23.610 MHz | +24.420 MHz | +20.591 MHz | **+22.874 MHz** | **[+17.861, +27.886] MHz** |
| Top mean request duration | -0.108 s | -0.133 s | -0.029 s | -0.090 s | [-0.225, +0.045] s |
| Bottom mean temperature | -0.899 C | -1.018 C | -0.027 C | -0.648 C | [-1.992, +0.696] C |

## Interpretation

At a fixed 120-point fan budget, allocating 20 more duty points to the lower
card and 20 fewer to the upper card improved the upper card's closing
steady-state temperature and clock in all three independent blocks. The
confidence intervals for both last-five-minute effects exclude zero. This is
direct evidence that airflow assistance from the lower card materially
benefits the upper card in this no-gap two-card stack; independent per-card
automatic fan control leaves system-level performance on the table.

Whole-window means include warmup and residual session-order variation. Their
effect directions generally agree, but their `n=3` intervals include zero and
must not be described as separately conclusive. The preregistered steady-state
responses are the cleaner controller-design coefficients.

## Scope and controller implication

The validated coefficient applies to this Tower2 chassis, no-gap geometry,
Qwen3.6-27B AWQ-INT4 workload, 400/400 W caps, and a 120-point total card-fan
budget. It supports a stack-aware fan controller that increases lower-card
airflow based on upper-card thermal demand. It does not yet establish a
universal coefficient for other gaps, chassis flow fields, power levels, or
three/four-card stacks; those remain bounded forecasts until matched physical
validation exists.

Artifacts:

- [`400w-static-fan-120point-observations-n3.csv`](400w-static-fan-120point-observations-n3.csv)
- [`400w-static-fan-120point-effects-n3.csv`](400w-static-fan-120point-effects-n3.csv)
- [`400w-static-fan-120point-policy-summary-n3.csv`](400w-static-fan-120point-policy-summary-n3.csv)
- [`400w-static-fan-120point-validated-n3.png`](400w-static-fan-120point-validated-n3.png)
