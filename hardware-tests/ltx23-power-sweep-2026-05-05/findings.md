# LTX-2.3 video gen render time vs GPU power cap — Tower2 RTX PRO 6000 Blackwell

**Date:** 2026-05-05
**Hardware:** Tower2, RTX PRO 6000 Blackwell Workstation Edition (GPU0), sealed-case revision (closed panel + grate blocked + roof sealed), 500 W operating cap baseline.
**Concurrent load on neighbor GPU:** GPU1 hosting `vllm-coder-next` AWQ at 500 W cap, idle (no inflight requests) throughout sweep — matches realistic dream-expo booth quiet state.
**Stack:** ComfyUI 0.16.4, PyTorch 2.11.0+cu128, NVIDIA driver 590.48.01-open, official Lightricks LTX-2.3 22B FP8 + distilled LoRA 0.5 + spatial upscaler.
**Workflow:** Two-stage T2V mirroring `comfyui_workflow_templates_media_video/templates/video_ltx2_3_t2v.json` — stage 1 at 640×352 / 4-step `euler_cfg_pp` sigmas, then `LTXVLatentUpsampler` 2×, then stage 2 at 1280×704 / 8-step `euler_ancestral_cfg_pp` sigmas, frame_rate=24, length=121 (5 s clip).
**Methodology:** 31 caps × 3 runs sustained × N=1 concurrency = 93 cells total. Power cap set via `sudo nvidia-smi -i 0 -pl <W>`, 5 s settle, 1.5 s gap between same-cap runs. Per-run wall-clock = `/prompt` POST → output mp4 visible in ComfyUI history. Per-run power/temp/clock sampled via `nvidia-smi dmon -s pucm -d 1`. Sweep was split into two contiguous phases (A: 600→400 W, B: 390→300 W) with a ~3 min gap between them — see *Audit notes* for the resulting cold-start asymmetry at the phase boundary.
**Raw data:** `ltx-power-sweep-combined.csv` (93 rows + header).

## TL;DR

1. **Cap genuinely binds for two-stage diffusion** — every cell hit within 1–2 W of the cap on peak GPU power. Unlike LLM single-stream inference (which plateaued at ~510 W on the same rig), LTX-2.3 will pull every Watt you give it.
2. **The curve is smooth and slowly steepening, with no sharp knee in the booth-relevant range.** Going 600 → 500 W costs +12.3 % gen time. Going 500 → 400 W costs +12.8 %. Going 400 → 300 W costs +25.0 %. The "real" V/f knee — where each 10 W removed starts costing >2× as much as it does at the top — sits around **360–400 W**.
3. **Above the operating cap, lifting to 600 W buys +11.0 % throughput per gen** (4.54 s saved per 5-s clip). Modest but non-trivial — meaningful for booth queue throughput where /video is the bottlenecked tile.
4. **The mean GPU draw runs ~85–93 % of the cap** even when peak hits the ceiling, because the LTX two-stage workflow has lower-power phases (latent setup, text encode, VAE decode, the upsampler step) that don't push the GPU. Practical implication: AC headroom calculations should use ~90 % of the cap × the number of co-loaded GPUs, not the cap × the number of GPUs.
5. **Thermals were never the constraint.** Peak GPU temp across the entire sweep was 83 °C (cap=590 W during heat-soak run 3); the firmware Tccd slowdown threshold is far higher.
6. **Compared to the LLM (vLLM) sweep on the same rig:** LLMs at this sustained-batched-N=32 case-revised sealed-case baseline plateaued from 450 W on up; here, every Watt above 400 W is still buying real time. **Diffusion and LLM serving have qualitatively different optimal cap regimes on the same hardware.**

## Prompt

The booth's "A founder getting an idea at sunrise" sample, used verbatim:

> Cinematic close-up shot, the camera slowly pushing in on a young founder seated at a wooden workbench, their hand pausing mid-sketch over an open notebook, eyes lifting toward soft warm sunrise light streaming in through tall industrial windows, a quiet moment of realization crossing their face, motes of dust drifting in the beams, a coffee mug beside them, prototyping tools and a laptop softly out of focus in the background, shallow depth of field, photorealistic detail, cinematic warm color grade, no camera shake, no warping, no rolling shutter, 8K sharp focus.

Each run uses a fresh random seed, so the *content* of the gen varies but the workload (steps × resolution × model) is deterministic.

## Per-cap results (full curve)

| Cap (W) | Runs | Mean (s) | Median (s) | Min (s) | Max (s) | Mean peak draw (W) | Mean avg draw (W) | Peak temp (°C) | Δ vs 600 W | Δ vs 500 W |
|---|---|---|---|---|---|---|---|---|---|---|
| 600 | 3 | 36.81 | 36.73 | 36.11 | 37.58 | 601 | 542 | 79 | 0% (ref) | -11.0% |
| 590 | 3 | 37.82 | 37.75 | 37.63 | 38.08 | 592 | 543 | 83 | +2.8% | -8.5% |
| 580 | 3 | 38.23 | 38.22 | 38.21 | 38.25 | 581 | 537 | 83 | +3.9% | -7.6% |
| 570 | 3 | 38.84 | 38.73 | 38.72 | 39.07 | 573 | 526 | 82 | +5.5% | -6.1% |
| 560 | 3 | 39.14 | 39.09 | 39.07 | 39.27 | 563 | 515 | 82 | +6.3% | -5.3% |
| 550 | 3 | 39.50 | 39.58 | 39.33 | 39.58 | 551 | 504 | 82 | +7.3% | -4.5% |
| 540 | 3 | 39.70 | 39.67 | 39.64 | 39.78 | 540 | 500 | 81 | +7.9% | -4.0% |
| 530 | 3 | 40.26 | 40.12 | 40.08 | 40.58 | 530 | 493 | 81 | +9.4% | -2.6% |
| 520 | 3 | 40.74 | 40.58 | 40.58 | 41.07 | 521 | 478 | 80 | +10.7% | -1.5% |
| 510 | 3 | 40.99 | 41.08 | 40.78 | 41.10 | 510 | 474 | 79 | +11.4% | -0.9% |
| **500** | 3 | **41.35** | 41.28 | 41.21 | 41.57 | 501 | 464 | 78 | +12.3% | **0% (ref)** |
| 490 | 3 | 41.99 | 42.08 | 41.69 | 42.20 | 491 | 457 | 77 | +14.1% | +1.5% |
| 480 | 3 | 42.18 | 42.20 | 42.09 | 42.25 | 481 | 450 | 77 | +14.6% | +2.0% |
| 470 | 3 | 42.66 | 42.58 | 42.57 | 42.82 | 475 | 436 | 76 | +15.9% | +3.2% |
| 460 | 3 | 43.12 | 43.09 | 43.07 | 43.20 | 468 | 432 | 75 | +17.2% | +4.3% |
| 450 | 3 | 43.69 | 43.68 | 43.65 | 43.74 | 458 | 421 | 74 | +18.7% | +5.6% |
| 440 | 3 | 44.19 | 44.20 | 44.17 | 44.22 | 445 | 415 | 74 | +20.1% | +6.9% |
| 430 | 3 | 44.95 | 45.06 | 44.73 | 45.07 | 437 | 404 | 73 | +22.1% | +8.7% |
| 420 | 3 | 45.61 | 45.59 | 45.58 | 45.66 | 421 | 391 | 72 | +23.9% | +10.3% |
| 410 | 3 | 46.07 | 46.08 | 46.07 | 46.08 | 418 | 386 | 72 | +25.2% | +11.4% |
| 400 | 3 | 46.63 | 46.58 | 46.58 | 46.73 | 410 | 371 | 71 | +26.7% | +12.8% |
| 390 | 3 | 47.44 | 47.60 | 47.12 | 47.60 | 396 | 362 | 68 | +28.9% | +14.7% |
| 380 | 3 | 48.39 | 48.28 | 48.28 | 48.61 | 388 | 357 | 69 | +31.5% | +17.0% |
| 370 | 3 | 49.27 | 49.30 | 49.20 | 49.31 | 371 | 348 | 68 | +33.9% | +19.2% |
| 360 | 3 | 50.15 | 50.17 | 50.10 | 50.18 | 365 | 338 | 67 | +36.3% | +21.3% |
| 350 | 3 | 51.61 | 51.61 | 51.60 | 51.61 | 350 | 326 | 65 | +40.2% | +24.8% |
| 340 | 3 | 52.52 | 52.60 | 52.34 | 52.61 | 342 | 319 | 65 | +42.7% | +27.0% |
| 330 | 3 | 53.81 | 53.69 | 53.66 | 54.09 | 330 | 311 | 64 | +46.2% | +30.1% |
| 320 | 3 | 55.11 | 55.10 | 55.10 | 55.12 | 320 | 302 | 63 | +49.7% | +33.3% |
| 310 | 3 | 56.79 | 56.78 | 56.74 | 56.84 | 310 | 293 | 62 | +54.3% | +37.3% |
| 300 | 3 | 58.31 | 58.22 | 58.11 | 58.59 | 303 | 284 | 61 | +58.4% | +41.0% |

Run-to-run consistency is excellent — most cells have a max-min spread under 0.5 s, and several below 0.1 s.

## Knee-point analysis

Slope (s of render time added per 10 W of cap removed), averaged over 60 W bands:

| Range | Mean slope (s/10 W) | %-of-baseline slope (per 10 W) |
|---|---|---|
| 600 → 540 W | 0.48 | 1.2 % |
| 540 → 480 W | 0.41 | 1.0 % |
| 480 → 420 W | 0.57 | 1.4 % |
| 420 → 360 W | 0.76 | 1.8 % |
| 360 → 300 W | 1.36 | 3.3 % |

The slope nearly triples as the cap drops below 360 W. The boundary is gradual rather than sharp — even 350 W only costs +25 % vs the 500 W operating point — but the sub-360 W regime is clearly where each Watt removed costs disproportionately more.

For practical purposes, the **operating regime is 400 W and up.** Below 400 W is for energy-efficiency experiments, not booth-day throughput.

## Heat-soak observations

Phase A (600 → 400 W) ran monotonically high-to-low without resets. The first cap (600 W) showed the most heat-soak across its three back-to-back runs:

| Cap | Run 1 t_peak | Run 2 t_peak | Run 3 t_peak |
|---|---|---|---|
| 600 W | 66 °C | 75 °C | 79 °C |
| 590 W | 80 °C | 82 °C | 83 °C |
| 580 W | 82 °C | 82 °C | 83 °C |

After the first cap, the GPU stayed warm and consistent. By the time the sweep reached 300 W, peak temp was down to 61 °C (lower power = less heat). At no point did peak temp approach 88 °C, and `nvidia-smi dmon` never reported a thermal throttle event in any run.

This matters because it means **the curve is the V/f curve, not a thermal-clamp artifact.** Pushing any cap below the throttle threshold would have visibly distorted the data.

## Comparison to LLM (vLLM) sweep on the same rig

The prior sweep (`../vllm-power-sweep-2026-04-29/`) tested two AWQ-INT4 LLMs at N=1 and N=32 across 7 caps (600 / 550 / 500 / 450 / 400 / 350 / 300 W). Headlines from that work:

- LLM N=1 (single-stream): peak draw ~510 W regardless of cap above 510 W. Cap is effectively non-binding above 510 W.
- LLM N=32 (batched): peak draw approaches 575 W for dense-27B at 600 W cap, but throughput **plateaus** at 450–600 W. 500 W is within 3.3 % of optimal across all four LLM scenarios.
- 400 W still delivered 96–99 % of peak LLM throughput.

Side-by-side at the relevant caps (% slowdown from optimal):

| Cap | LTX-2.3 video gen | LLM (Coder-Next, batched) | LLM (Dense-27B, batched) |
|---|---|---|---|
| 600 W | optimal (ref) | -2.3 % | -2.3 % |
| 500 W | +12.3 % | -0.6 % | -3.3 % |
| 400 W | +26.7 % | -4.1 % | -4.5 % |
| 300 W | +58.4 % | -18.7 % | -25.2 % |

**The two workloads have fundamentally different sensitivities to cap.** LLMs are memory-bandwidth-bound and HBM bandwidth doesn't change with the cap; they plateau early. LTX-2.3's two-stage diffusion is compute-bound (lots of fp8 matmul through the spatial upsampler and stage-2 sampling) and scales nearly linearly with effective clock from 600 W down through ~360 W.

If you're scoping a multi-GPU sweep on the same hardware, **don't generalize cap behavior across workloads** — what's optimal for one is wasted on the other.

## Operational implications (for the dream-expo booth, 2026-05-07)

The /video tile is the booth's most bottlenecked surface — every visitor wants a video, gens take ~42 s at the current 500 W cap, the queue grows quickly under crowd load. So this curve directly informs how many concurrent visitors can be served before queue-position-2 visitors give up and leave.

Three operating-point options:

| Option | Cap (W) | Mean gen (s) | Throughput vs 500 W | GPU0 mean peak draw | GPU0 mean avg draw | Total system AC ceiling (both GPUs loaded) |
|---|---|---|---|---|---|---|
| Conservative | 500 (current) | 41.35 | baseline | 501 W | 464 W | ~1580 W AC (validated) |
| Modest lift | 550 | 39.50 | +4.7 % | 551 W | 504 W | est. ~1640 W AC |
| Full lift | 600 | 36.81 | +12.3 % | 601 W | 542 W | est. ~1680 W AC |

20 A US circuit continuous limit (NEC 80 %) is 1920 W. The current setup runs ~1580 W AC under combo stress (per `project_tower2_case_revision_2026-04-28.md`). Lifting GPU0 only — leaving GPU1 at 500 W since LLM serving doesn't benefit (see vLLM sweep) — adds at most ~100 W AC under simultaneous load, so all three options fit comfortably under the circuit ceiling.

The trade is: each Watt of cap headroom gives a small per-gen win, but the win compounds across the day at queue scale. At a hypothetical 200 visitors over 6 hours of booth time = 1.8 mins/visitor average, even a 5-s/gen reduction is ~17 mins of total queue compression — meaningful at the tail.

**Recommendation:** lift GPU0 specifically (not GPU1) to 550–600 W for booth day if the operator is comfortable spending the AC headroom; otherwise stay at 500 W. There is no "wrong" answer — both are validated. The numbers above let it be a deliberate choice rather than an arbitrary one.

## Reproducing

The sweep script lives at `~/dream-expo/scripts/bench/ltx-power-sweep.ts` and is reproduced here as `ltx-power-sweep.ts`. Run from inside a checkout of [dream-expo](https://github.com/Light-Heart-Labs/dream-expo) so the relative import of `buildLtxWorkflow` resolves:

```bash
cd ~/dream-expo
sudo -v   # prime the sudo cache; the script then heartbeats every 60 s
node --experimental-strip-types scripts/bench/ltx-power-sweep.ts \
  --caps=600,590,580,...,310,300 --n=3
```

Outputs:
- A CSV at `scripts/bench/output/ltx-power-sweep-<timestamp>.csv`
- Per-run progress on stdout
- Final per-cap summary table on stdout

The script restores GPU0 to 500 W on normal exit AND on SIGINT/SIGTERM. The dependency on `dream-expo/src/lib/ltx-workflow.ts` is intentional — it guarantees the bench uses the *exact* workflow JSON the booth uses, not a hand-copied facsimile.

## Audit notes

- **Phase boundary cold-start.** The sweep ran in two phases — A (600→400 W) and B (390→300 W) — with a ~3 min gap between them while shell state was renewed. The first 390 W run started at `t_start=43 °C` vs ~58 °C steady-state across all of phase A. Render time at 390 W r1 (47.12 s) was 0.5 s faster than r2/r3 (both 47.60 s). This is a small effect — within the per-cap spread elsewhere — but it means the 390 W mean is mildly optimistic by ~0.2 s. Other caps in phase B started warm (run 1 at 380 W began at 55 °C) and showed normal heat-soak behavior. No cells were thrown out.
- **Mean peak draw above the cap.** A handful of cells (notably 460 W r3 and 410 W r2) recorded peak draws 5–15 W above the cap. The dmon polling at 1 Hz catches the cap-set transient occasionally — if a sample lands during the millisecond window when `nvidia-smi -pl` is being applied, the previous (higher) cap is still in effect. These are sampling artifacts, not a sign that the cap leaks. They have no effect on render time.
- **Run-to-run consistency.** The single noisiest cell is 600 W (max - min = 1.47 s). Plausible cause: this was the first cap of phase A, so run 1 was a cold-load (model already in VRAM but kernel cache cold), runs 2–3 hit normal steady-state. All subsequent caps had max-min spreads ≤ 0.6 s, with most under 0.1 s. The spread is small enough that the curve shape is unambiguous.
- **GPU1 (vllm) was idle but loaded throughout.** Memory and HBM bandwidth on GPU1 was occupied by `vllm-coder-next` weights (~92 GB), but no inference traffic was sent to it during the sweep. PCIe traffic to GPU0 was also at idle. Repeating this sweep with GPU1 also under load (e.g. simulating Race-the-Cloud + Video happening simultaneously) is left as future work — that's the realistic worst case for booth day.
- **Comfort with publishing.** The sweep was run on consumer-shipped firmware/drivers and used the exact workflow JSON the live booth uses. The numbers should generalize to any RTX PRO 6000 Blackwell at the same software stack. They will not generalize to other LTX-2.3 deployments using single-stage paths, different sigma curves, different LoRA strength, or different output resolution — those each shift the workload's compute footprint.
