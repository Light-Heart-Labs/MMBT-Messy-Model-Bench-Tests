# Validated lower-neighbor airflow assistance

This experiment isolates whether the fan on a cooler lower card can assist a
loaded upper card in Tower2's no-gap layout. GPU1/top remained saturated at
300 W and 100% utilization with its own fan fixed at 50% (about 1,678 RPM).
GPU0/bottom remained model-resident and idle while only its fan changed among
30%, 50%, and 70%. Three independently initialized Latin-order blocks provide
`n=3` for each setting.

## Validated result

Increasing only the idle lower card's fan from 30% (about 1,200 RPM) to 70%
(about 2,157 RPM):

- reduced loaded-top mean temperature by **4.984 C** (paired-block 95% CI
  **-5.313 to -4.655 C**);
- reduced loaded-top last-five-minute temperature by **5.281 C** (95% CI
  **-6.073 to -4.489 C**);
- increased loaded-top mean graphics clock by **15.090 MHz** (95% CI
  **+9.086 to +21.095 MHz**);
- increased loaded-top last-five-minute clock by **16.289 MHz** (95% CI
  **+13.675 to +18.903 MHz**);
- reduced mean request duration by **0.423 seconds** (95% CI
  **-0.523 to -0.323 seconds**); and
- added **3.911 W** of idle lower-card board power (95% CI
  **+3.233 to +4.589 W**).

The top card's mean temperature was 54.835, 52.074, and 49.851 C at 30%, 50%,
and 70% lower-fan duty, respectively. Its mean clock was 1,028.195,
1,038.612, and 1,043.286 MHz. Every cell held top power at 299.993 W, top fan
near 1,678 RPM, and top utilization at 100%. All thermal and hardware
power-brake counters remained zero.

## Interpretation

This is causal evidence of useful fan cooperation across the adjacent pair:
the cooler lower card can contribute pressure/flow that materially improves
the hotter upper card even when the lower GPU is doing no compute work. The
clock and latency gains are ordinary temperature-dependent boost behavior,
not recovery from a recorded thermal-throttle event. At this 300 W operating
point, spending about 3.9 W on the lower fans bought about 5 C of upper-card
thermal headroom and a modest, repeatable performance gain.

The result supports a stack-aware controller that drives lower-card assistance
from downstream or hottest-card demand instead of allowing each card to act
only on its own temperature. It does not yet establish the optimal dynamic
curve or prove a four-card outcome. Those require static power/fan surface
anchors followed by a background-service crossover against stock auto, equal
static, lower-biased static, top-temperature-led, and hottest-card-led control.

## Limits

- One two-card no-gap chassis and one 300 W top-loaded operating point.
- No calibrated ambient or local-inlet probes, so this is internally valid but
  not yet transferable to other chassis.
- No acoustic measurement and no direct fan-only wall-power measurement.
- The idle lower board-power increment includes fan-control-related board
  effects and should not be treated as a calibrated fan electrical curve.
- Three- and four-card behavior remains a bounded forecast until physically
  validated.

## Artifacts

- [`fan-isolation-neighbor-loadtop-observations-n3.csv`](fan-isolation-neighbor-loadtop-observations-n3.csv)
- [`fan-isolation-neighbor-loadtop-summary-n3.csv`](fan-isolation-neighbor-loadtop-summary-n3.csv)
- [`fan-isolation-neighbor-loadtop-effects-n3.csv`](fan-isolation-neighbor-loadtop-effects-n3.csv)
- [`fan-isolation-neighbor-loadtop-n3.png`](fan-isolation-neighbor-loadtop-n3.png)
