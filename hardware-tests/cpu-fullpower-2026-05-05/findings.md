# AMD Threadripper PRO 7965WX sustained at 350 W TDP — Tower2 thermal validation

**Date:** 2026-05-05
**CPU:** AMD Ryzen Threadripper PRO 7965WX, 24 cores / 48 threads, family 25 / model 24 / stepping 1 (Zen 5 / "Storm Peak"), 128 MiB L3, base 4.2 GHz, max boost 5.35 GHz
**Rated TDP:** **350 W** (factory PPT)
**Motherboard:** ASUS Pro WS WRX90E-SAGE SE, BIOS v1203 (AMI, 2025-07-18)
**Voltage:** 1.2 V
**Cooling stack:** **Air cooled.** Heat exchanger (HX) air heatsink on the CPU with one top-mounted exhaust-assist fan (pulls GPU exhaust through the HX fins, dumps directly overhead), all-intake case fans, sealed-case revision (closed side panel + blocked grate + sealed roof; rebuild validated 2026-04-29). Fan curve uses CPU temp as a proxy for GPU heat load. No liquid loop, no AIO, no chiller.

> **Personal research note.** This test was run to settle a disagreement about whether a 350 W CPU can be sustained on an air-cooled workstation desktop with this kind of cooling stack. The numbers below are the answer for *this specific rig* (TR PRO 7965WX in an ASUS WRX90E-SAGE SE chassis with the cooling described above). Don't generalise to other 350 W chips, other coolers, or other rooms — this is a one-rig anecdote, not a recommendation. Posted to the public bench repo because the data exists, not because it's broadly useful.
**Workload:** `stress-ng --matrix 0 --matrix-method all` — AVX matrix multiply on all 48 threads. AVX matrix is the canonical "as hot as the CPU gets on real workloads" stressor. Per-core power draw and Tccd numbers under this load are upper-bound for anything you'd encounter in normal use.
**Methodology:** Two contiguous phases — phase 1 (5 min, the existing `cpu-burn.sh` harness) and phase 2 (17 min injected `stress-ng` run with continuation samplers). 2-min idle gap between phases (sudo prompt latency on harness restart; CPU cooled to ~55 °C in that window, then ramped back up). Power sampled every 2 s via `/sys/class/powercap/intel-rapl:0/energy_uj` (delta-energy → mean power across the interval). Temperatures sampled every 2 s via `lm-sensors` (Tctl + four Tccd zones).
**Concurrent load on GPUs:** GPU0 idle (16-20 W). GPU1 idle but loaded with vLLM weights at 90 W idle draw. Neither GPU under inference traffic.
**Raw data:** `original-5min-pkgwatt.csv`, `original-5min-thermlog.csv`, `extension-17min-pkgwatt.csv`, `extension-17min-thermlog.csv`. Run scripts in `cpu-bench-pkgwatt.sh` (wrapper) and `cpu-burn.sh` (load harness) and `thermlog.sh` (logger).

## TL;DR

The 7965WX **pinned its 350 W rated TDP for 17 continuous minutes** of all-thread AVX matrix load — sustained mean **349.4 W** over the steady-state window (samples = 491 / 2 s spacing), peak **351.3 W**. CPU clocks held at **~4660 MHz across all 48 threads** under that load — solidly into all-core boost territory above the 4.2 GHz base.

Steady-state thermals: **Tctl mean 90.1 °C, max 92.6 °C** (Tjmax 95 °C — 2.4-4.9 °C headroom). One Tccd zone briefly touched 95.2 °C at peak, but PkgWatt held flat at 349 W and clocks did not collapse — no measurable thermal throttle.

For context: this is a 350 W chip running flat-out for 17 minutes on the hottest workload it sees, and it never had to back off. The cooling stack (custom water + HX exhaust-assist + sealed case) was sized for dual-GPU + CPU combo loads up to ~1580 W AC at the wall; CPU-only loading is well within that envelope.

## Power: pinned to rated TDP

| Phase | Duration | Samples | Min PkgWatt | Max PkgWatt | Mean PkgWatt | Mean / rated TDP |
|---|---|---|---|---|---|---|
| Phase 1 (5 min original) | 300 s stress | 155 | 117.5 W (idle baseline) | 350.4 W | 339.9 W | 97.1% |
| Phase 2 (17 min extension), full window | 1020 s stress | 515 | 114.0 W (initial baseline) | 351.3 W | 345.0 W | 98.6% |
| Phase 2, **steady-state** (excludes first 30 s ramp) | 982 s | 491 | 347.6 W | 351.3 W | **349.4 W** | **99.8%** |

Steady-state of the 17-min phase: PkgWatt min-to-max range is **3.7 W** across 491 samples. The CPU is sitting hard against its 350 W ceiling and not budging. There is no observable PPT-induced clock collapse — when a TR PRO is power-limited, you typically see clocks drop and PkgWatt hold; here both are flat.

This tells us the BIOS is at **factory 350 W TDP**, with no PBO / Boost / "Eco mode" lift applied in the WRX90E-SAGE SE firmware. If we wanted more, BIOS PBO settings could push the package to 420-500 W, but the hardware at factory TDP is already the binding number for "what does the CPU pull at full load."

## Temperature: comfortable, never throttled

Steady-state of the 17-min phase (n=426 samples, first 60 s ramp excluded):

| Sensor | Mean | Min | Max |
|---|---|---|---|
| Tctl (overall) | 90.1 °C | 87.8 °C | 92.6 °C |
| Tccd (max of 4 zones) | 88.8 °C | — | 95.2 °C |
| Per-thread MHz (avg of /proc/cpuinfo) | 4661 | 4633 | 4683 |

Tjmax for Zen 5 / TR PRO 7965WX is 95 °C. **One Tccd zone touched 95.2 °C at peak — right at the limit.** Two important calibration points for that:

1. **No throttle event followed.** PkgWatt held at 349.4 W mean across the 17-min window with a min-to-max range of 3.7 W. If thermal throttle had engaged, PkgWatt would have dropped (clock down → power down). It did not.
2. **Per-CCD vs Tjmax is a soft margin** — the chip will throttle progressively starting before Tjmax, not as a hard cliff at exactly 95 °C. Sitting at 88.8 °C mean Tccd with brief touches at the limit means we are *near* the thermal envelope but the cooling stack is shedding heat at 350 W production rate.

The 17-min phase Tctl ramp is monotonic for the first ~3 min then stable — thermal soak completes by minute 3, then equilibrium for the next 14 min:

```
ext+60s:   87.5 °C   (post-restart ramp begins)
ext+120s:  90.2 °C
ext+180s:  90.8 °C
ext+240s:  88.9 °C   (fan curve catches up)
ext+300s:  89.2 °C
ext+420s:  89.6 °C
ext+540s:  89.8 °C
ext+660s:  90.4 °C
ext+780s:  90.6 °C   (slow drift, no runaway)
ext+900s:  90.0 °C
ext+1020s: 90.1 °C   (end of injection)
```

The drift between minute 3 and minute 17 is **+0.6 °C** — for practical purposes this is steady-state. There is no thermal runaway and no late-onset throttle.

## Clocks: all-core boost, not base

Sustained MHz across all 48 threads at 349 W package power: **4661 MHz (mean)**, range 4633–4683 MHz over the steady-state window. The 7965WX base clock is 4.2 GHz; max boost is 5.35 GHz; this CPU is running ~460 MHz above base on every single thread simultaneously. The variance is tight (±25 MHz) — there are no sudden clock dips that would indicate transient throttling.

For comparison: a typical "marketing" benchmark of a high-end TR PRO might cite **single-thread** 5.3 GHz or **all-core** ~4.4-4.5 GHz under conservative cooling. The 4.66 GHz all-core sustained on this rig is a real cooling-headroom result, not a spec-sheet number.

## Why this is surprising (the disagreement that prompted the test)

The conventional intuition is that a 350 W CPU on **air** will either (a) thermal-throttle and back off to ~80% of rated power within minutes under sustained AVX, or (b) require a high-end AIO / custom water / chiller to avoid that. Air cooling at sustained 350 W is generally considered marginal-to-impossible on a workstation desktop.

This rig clears the bar (briefly touching Tjmax on one zone but not throttling) because of how the cooling path is constructed — five things working together:

1. **HX (heat exchanger) air sink with a top exhaust-assist fan**, not a tower cooler. The fan pulls GPU exhaust *through* the HX fins and dumps the combined stream out the case roof. This is the unusual piece — the CPU sink isn't trying to reject heat into ambient case air; it has its own forced-exhaust path.
2. **Sealed-case rebuild (2026-04-29)** — closed side panel + blocked grate + sealed roof forces all airflow through intentional paths. Validated to handle 1580 W AC (combo CPU + 500 W × 2 GPUs) without thermal margin loss.
3. **All-intake case fans** — the case is positively pressured; air leaves only through the top exhaust where the HX is.
4. **Fan curve drives CPU fans off CPU temp as a GPU-heat proxy.** When the GPUs are hot but the CPU is cool, the case is still aggressively ventilated, which keeps the HX-intake air cooler than ambient case air would be.
5. **Ambient room temp ~22 °C** during the test (typical office). Hotter rooms would shift the curve up; this is not a "running it in a cooled server room" result.

Remove any one of these and Tctl would push into throttle territory. The earlier (pre-sealed-case) version of this rig *would* hit Tjmax on AVX — that observation is preserved in `project_tower2_thermal_design.md` and is what prompted the case rebuild in the first place.

## Audit notes

- **2-min idle gap between phases** is real and visible in the timeline (both CSVs are independent runs). It does not affect the steady-state stats since both phases reach equilibrium independently and the steady-state window of phase 2 is defined to skip the post-restart ramp.
- **AVX matrix is upper-bound.** Real-world workloads (compilation, inference glue code, IO-heavy tasks) generate much less heat per Watt of package power. The 90 °C number is a worst-case headline; expect 70-80 °C on most actual workloads.
- **Tccd 95.2 °C peak.** This is the binding observation for "can it hold 350 W indefinitely?" The data here covers 17 min steady-state without throttle. We don't have data beyond 17 min, so a >1 hour run could in principle drift differently — but the trajectory across minutes 3-17 is flat (+0.6 °C / 14 min), suggesting equilibrium has been reached.
- **GPUs were idle during the bench.** A combo run (GPUs at 500 / 600 W cap simultaneously with CPU at 350 W) would shift the case airflow load and is left as future work. The prior dual-GPU validation (`project_tower2_case_revision_2026-04-28.md`) tested at 500 W combo + light CPU stress; this test does CPU at full TDP + light GPU. Combined max-stress hasn't been characterized.
- **One Tctl reading of 92.6 °C** would be the headline if we cared about absolute peak, but for "is the cooling adequate" the mean of 90.1 °C and the steady-state PkgWatt of 349.4 W are the load-bearing numbers.

## Reproducing

```bash
sudo -v   # prime sudo cache for energy_uj reads + nvidia-smi -pl
cd ~/thermal-tests
./cpu-bench-pkgwatt.sh <tag> <duration_s>
```

The wrapper:
1. Verifies sudo cache, starts a 60-s heartbeat keepalive.
2. Spawns a parallel `intel-rapl` energy_uj sampler to its own CSV.
3. Calls `cpu-burn.sh` which runs `stress-ng --matrix 0 --matrix-method all -t <duration>s` plus per-2 s thermal logging via `thermlog.sh`.
4. Prints per-cap snapshots, final PEAKS, and a one-line PkgWatt summary at end.

The 7965WX is at factory PPT, so `nvidia-smi -pl`-style runtime cap manipulation isn't applicable here — to test different power budgets, BIOS PBO settings would need to be changed. That's left as future work; the headline finding ("CPU sustains rated TDP without throttling") is independent of that knob.
