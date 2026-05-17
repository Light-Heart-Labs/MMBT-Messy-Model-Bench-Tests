# Threadripper PRO 7965WX sustained-TDP validation — 2026-05-05

A 22-minute (5 min + 17 min, 2 min gap) full-power test of the AMD Threadripper PRO 7965WX (24 cores / 48 threads, 350 W rated TDP) on Tower2's **air cooling stack** — HX heatsink with a top-mounted exhaust-assist fan in a sealed-case build, no liquid. Workload: `stress-ng --matrix` AVX matrix multiply on all 48 threads — the canonical "as hot as it gets" CPU stressor.

> **Personal research, not a recommendation.** This was run to settle a disagreement about whether a 350 W CPU can hold rated TDP on air cooling with this build. The numbers are for *this specific rig*; no claim is made that other 350 W parts on other coolers will behave the same. Published here because the data exists and the bench repo is the obvious place to keep it, not because it's broadly community-useful.

## Read order

1. **`findings.md`** — full writeup: power table (mean/peak/min by phase), thermal envelope, clock behaviour, cooling-stack explanation, audit notes.
2. **CSVs** — raw 2-second-interval samples:
   - `original-5min-pkgwatt.csv` / `original-5min-thermlog.csv` — phase 1 (5 min)
   - `extension-17min-pkgwatt.csv` / `extension-17min-thermlog.csv` — phase 2 (17 min)
   - PkgWatt files: `t_iso, energy_uj, watts`
   - Thermlog files: `t, cpu_tctl, cpu_ccd_max, cpu_mhz, gpu0_*, gpu1_*, nvme0..2`
3. **`readings.txt`** — one-shot snapshots taken mid-bench: `lscpu`, `cpupower frequency-info`, `sensors -A`, `nvidia-smi`, full `/proc/cpuinfo` MHz dump for all 48 threads.
4. **`bios-and-rapl.txt`** — `dmidecode` (BIOS, motherboard, processor, memory) and `intel-rapl` powercap constraint readouts. Confirms BIOS at v1203 (AMI 2025-07-18), motherboard ASUS Pro WS WRX90E-SAGE SE.
5. **`original-5min-run.log`** — full stdout from the 5-min `cpu-burn.sh` run (per-minute thermal snapshots + final PEAKS section).
6. **Scripts** — `cpu-bench-pkgwatt.sh` (wrapper), `cpu-burn.sh` (load harness), `thermlog.sh` (sampler).

## Headline

**349.4 W mean PkgWatt sustained across 17 minutes** of all-thread AVX matrix on a 350 W rated CPU = **99.8% of TDP, no throttle.** Tctl mean 90.1 °C (Tjmax 95 °C). All 48 threads sustained at 4.66 GHz across the full window. The HX air heatsink + exhaust-assist fan + sealed-case + all-intake fan stack is what lets the 7965WX sit at rated TDP on air on this workstation. Most observers wouldn't expect it; that's why the test was run. See `findings.md` §"Why this is surprising" for the explanation of the cooling path.

## Companion sweeps on the same rig

- `../ltx23-power-sweep-2026-05-05/` — LTX-2.3 video gen vs GPU power cap (cap genuinely binds for diffusion, +11% throughput at 600 W cap).
- `../vllm-power-sweep-2026-04-29/` — vLLM throughput vs GPU power cap (500 W within 3.3% of optimal for both 27B and Coder-Next AWQ across N=1 and N=32).

The trio characterises this rig's CPU + GPU behaviour at full sustained power. CPU result here is binary ("yes, holds rated TDP"); the GPU writeups are full curves.
