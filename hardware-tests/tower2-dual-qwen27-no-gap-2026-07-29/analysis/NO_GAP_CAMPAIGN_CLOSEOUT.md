# Tower2 no-gap campaign closeout

## Campaign state

The no-gap phase is complete for its highest-value objective: measuring how fan allocation, power, and card position interact in a two-card stack and producing bounded planning evidence for larger stacks. The repository contains raw 1 Hz telemetry, checksums, per-run summaries and figures, a run registry, regenerated validation aggregates, paired-effect tables, and explicit exclusions.

Internally validated populations include the 250 W fixed-fan matrix, 300 W V3HOST paired blocks, own-fan and neighbor-fan isolation experiments, 350 W fixed-fan matrix, and the safe 400 W 120-point matrix. The automatic-fan 500 W anchor is internally informative at n=2 but not n=3. No population is transferable because calibrated ambient and local-inlet measurements were not installed.

## What is now supported

- Card position creates a large and repeatable no-gap penalty. At 500/500 W automatic fan, the top averages about 18.9 C hotter and 428 MHz slower while demanding about 803 more fan RPM.
- Lower-card fan assistance benefits a loaded upper card. The direct neighbor-isolation experiment measured a 4.984 C reduction in loaded-top mean temperature from increasing the lower fan from 30% to 70%.
- At equal total fan budget, lower-biased allocation improves upper-card clock and latency increasingly across validated 250, 350, and 400 W populations. At 400 W, B70T50 minus B50T70 improves top last-five-minute temperature by 0.876 C and clock by 22.874 MHz, with paired n=3 confidence intervals excluding zero.
- Fan RPM must be modeled alongside fan percentage, temperature, power, position, workload performance, and execution order. Percentage alone is not a portable airflow unit.
- High-power automatic control can enter a bounded, quantized late-run fan limit cycle even when GPU temperature is flat. A stack-aware controller and a prospective controller-aware validation rule are justified follow-up work.
- The existing 3x/4x stack-height envelope is suitable for planning bounds only. It is not a measured prediction, and its additive 350/400 W four-card scenarios crossing 100 C are warnings, not safety guarantees.

## Deliberately closed or deferred cells

| Cell or activity | Disposition |
|---|---|
| `NG-SYM-250` automatic fan | Deferred; richer fixed-fan n=3 evidence exists at 250 W |
| `NG-SINGLE-B-250` | Deferred; lower value than spacing and controller validation |
| Legacy 300 W V2 blocks | Superseded by V3HOST n=3 blocks |
| EQ30 strict-slope repeats | Superseded by the prospective v2 fixed-fan plateau protocol |
| Original 400 W 100-point matrix | Retired after safety boundary; replaced by validated 120-point matrix |
| `NG-SYM-500` | Closed at informative n=2; additional automatic-fan repeats require a prospective controller-aware plateau rule |
| `NG-SYM-600` | Retired as unsafe unchanged |
| 600/400 W asymmetric anchor | Retained as a useful n=1 boundary observation, not foundational validation |

## Highest-value next round

Restore a controlled physical gap and repeat a deliberately small matched set rather than another broad no-gap sweep:

1. Instrument ambient plus both card inlets with calibrated probes.
2. Repeat matched n=3 anchors at 250, 350, and 400 W using the same fixed-fan policies and randomized/Latin execution order.
3. Add one safe 500 W automatic or controller-driven anchor only after defining the prospective plateau rule.
4. Swap card positions in at least one matched block to separate card identity from position.
5. Fit spacing-response coefficients only from matched no-gap/gap pairs; use them to interpolate smaller gaps with uncertainty, not as unqualified point predictions.
6. Build and validate the fail-safe background fan service: drive lower-stack assistance from upper-card temperature, log commanded percentage and physical RPM, restore automatic control on stale telemetry/process failure, and compare it against matched static policies.
7. Use any future 3x/4x physical stack to validate—not originate—the stack-height model, starting at low power and escalating only after measured inlet and temperature margins pass.

The campaign should now be considered wrapped. Further no-gap runs have lower information value than spacing, calibrated inlet data, card-position swaps, and controller validation.

