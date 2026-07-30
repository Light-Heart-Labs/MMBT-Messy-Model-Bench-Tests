# Tower2 dual-GPU no-gap thermal study — 2026-07-29

Two RTX PRO 6000 Blackwell Workstation Edition GPUs were installed directly adjacent, with no open-slot air gap. GPU1 is the top card in `PCIEx16(G5)_1`; GPU0 is the bottom card in `PCIEx16(G5)_3`.

Each card runs an independent Qwen3.6-27B AWQ-INT4 vLLM engine with 32 concurrent requests. The study begins with a 600 W bottom / 400 W top cell and adds an equal 500/500 W cell matching an external 10-minute SM120 thermal-stress specification.

## Results

| Run | Bottom mean / max / fan | Top mean / max / fan | Throttling |
|---|---|---|---|
| [`ng-fan-eq30-sym250-r1`](ng-fan-eq30-sym250-r1/) | 51.28 C / 54 C / 30.0%, 1,200 RPM | 67.76 C / 73 C / 30.0%, 1,200 RPM | Internally admissible fixed-fan equilibrium n=1/3; counters zero |
| [`ng-fan-eq30-sym250-bump-r3-5m`](ng-fan-eq30-sym250-bump-r3-5m/) | 49.68°C / 54°C / 30.0%, 1,201 RPM | 62.28°C / 70°C / 30.0%, 1,201 RPM | Successful 5m extension; excluded as non-steady |
| [`ng-fan-eq30-sym250-bump-r2`](ng-fan-eq30-sym250-bump-r2/) | 48.12°C / 51°C / 30.0%, 1,201 RPM | 57.32°C / 64°C / 30.0%, 1,201 RPM | Successful 2m fixed-fan bump; excluded as intentionally non-steady |
| [`ng-fan-eq30-sym250-bump-r1-instrumentation-failure`](ng-fan-eq30-sym250-bump-r1-instrumentation-failure/) | Warmup only | Warmup only | Excluded: privilege-context bug prevented manual state; caught before measurement |
| [`ng-single-b-250-r3-excluded`](ng-single-b-250-r3-excluded/) | 53.66°C / 56°C / 31.8% mean | Isolated idle: 44.91°C / 47°C / 30.0% mean | Excluded: GPU0 fan and GPU1 temperature remained non-steady |
| [`ng-sym-250-r2`](ng-sym-250-r2/) | 52.73°C / 55°C / 31.2% mean | 67.61°C / 71°C / 40.5% mean | Thermally admissible n=1/3; counters zero; GPU1 clock channel flagged |
| [`ng-single-b-250-r2`](ng-single-b-250-r2/) | 53.47°C / 56°C / 31.5% mean | Isolated idle: 44.27°C / 46°C / 30.0% mean | Internally admissible n=1/3; thermal counters zero |
| [`ng-single-t-250-r5`](ng-single-t-250-r5/) | Isolated idle: 29.00°C / 29°C / 30.0% mean | 56.39°C / 59°C / 33.3% mean | Third admissible replicate; within-campaign n=3 validated |
| [`ng-single-t-250-r4`](ng-single-t-250-r4/) | Isolated idle: 29.00°C / 29°C / 30.0% mean | 56.35°C / 59°C / 33.2% mean | Internally admissible replicate; thermal counters zero |
| [`ng-single-t-250-r3-aborted`](ng-single-t-250-r3-aborted/) | Partial: isolated idle 29.00°C / 29°C / 30.0% | Partial: 55.78°C / 59°C / 32.7% | Excluded: external Sanctuary request at 7.404m |
| [`ng-single-t-250-r2`](ng-single-t-250-r2/) | Isolated idle: 28.90°C / 29°C / 30.0% mean | 55.86°C / 58°C / 32.9% mean | Internally admissible n=1/3; thermal counters zero |
| [`bottom-idle-top250-10m`](bottom-idle-top250-10m/) | Idle: 29.28°C / 32°C / 30.0% mean | 56.92°C / 60°C / 33.8% mean | No thermal counters; qualified by late GPU0 background-power activity |
| [`bottom250-top-idle-10m`](bottom250-top-idle-10m/) | 52.41°C / 55°C / 31.0% mean | Idle: 43.14°C / 45°C / 30.0% mean | No thermal or power-brake counter growth |
| [`both250-10m`](both250-10m/) | 51.85°C / 54°C / 30.7% mean | 66.97°C / 70°C / 40.1% mean | Power-limit derating only; thermal counters zero |
| [`bottom600-top400-2m`](bottom600-top400-2m/) | 76.25°C / 80°C / 45.4% mean | 76.58°C / 87°C / 45.2% mean | Power-limit derating; thermal counters zero |
| [`bottom600-top400-30m`](bottom600-top400-30m/) | 80.59°C / 84°C / 49.8% mean | 87.94°C / 92°C / 67.8% mean | Heat-associated boost loss under power cap; thermal counters zero |
| [`both500-10m`](both500-10m/) | 70.20°C / 74°C / 42.9% mean | 89.57°C / 93°C / 78.5% mean | Heat-associated boost loss; GPU1 SW thermal counter 1.054 s (0.176%) |
| [`both600-30m-aborted`](both600-30m-aborted/) | 74.97°C / 77°C / 45.6% mean | 92.65°C / 96°C / 99.4% mean | Safety abort at ~5m; GPU1 SW 5.84 s + HW 0.28 s |

During the 30-minute run, the bottom card settled near 81°C at 50% fan while drawing 600 W. The top card settled near 88°C at 69–71% fan while drawing 400 W. The top card therefore ran about 7.4°C hotter and required roughly 18 percentage points more fan despite consuming 200 W less, but neither GPU recorded hardware thermal slowdown, software thermal slowdown, or hardware power-brake events.

This establishes that the adjacent-card layout is stable at a 600/400 W split. It does not isolate the effect of spacing because the existing air-gap reference used 600/600 W. Direction-reversed and equal-cap cells are needed to separate vertical position, neighbor heat, and airflow-channel effects.

The equal 500/500 W cell held both cards at 100% utilization and approximately 500 W for 10 minutes. GPU1/top accumulated 1.054 seconds of software thermal slowdown—0.176% of the measured window—but the 1 Hz flag was never sampled active, hardware counters remained zero, and first-to-last five-minute frequency changed by only -0.37%. This is recorded as a noise-level boundary event, not meaningful sustained throttling. Its run directory includes the requested [`thermal-stress.png`](both500-10m/thermal-stress.png).

The attempted equal 600/600 W 30-minute cell hit the 96°C emergency cutoff after approximately five measured minutes. GPU1/top averaged only 589.7 W, ran at 99.4% mean fan, accumulated 5.84 seconds of software and 0.28 seconds of hardware thermal slowdown, and reported the software-thermal flag active at the cutoff sample. This is a confirmed thermal limit for the no-gap layout; the failed cell is preserved rather than extrapolated to 30 minutes.

The equal 250/250 W cell held both cards at 100% utilization and exactly 250 W for ten minutes. GPU0/bottom averaged 51.85°C at 30.7% fan and 803.6 MHz. GPU1/top averaged 66.97°C at 40.1% fan and 775.5 MHz. The 15.12°C positional temperature delta persisted at low power, but the mean frequency delta narrowed to 28.1 MHz and both thermal counters remained zero.

The first single-card isolation cell loaded only GPU0/bottom at 250 W while leaving the model-resident GPU1/top at 0% utilization. GPU0 stabilized at a 53.03°C last-five-minute mean. The idle top card rose from 31°C before the run to a 44.81°C last-five-minute mean while drawing only 21.8 W, directly measuring substantial bottom-to-top neighbor heating. This control is not ambient-normalized because external temperature probes were not yet attached.

The reverse isolation cell, `NG-SINGLE-T-250`, is the first to reach three internally admissible replicates. Across replicates 2, 4, and 5, the loaded top card averaged 56.200 ± 0.294°C, its last-five-minute temperature averaged 56.941 ± 0.140°C, and its fan averaged 33.137 ± 0.193%. Throughput was exactly 0.9067 requests/s in every run and all thermal/brake counters remained zero. The idle bottom card averaged 28.967 ± 0.058°C. This establishes within-campaign repeatability, not cross-chassis transferability; all three runs occurred in one campaign session and no calibrated ambient/local-inlet probes were available. See [`analysis/NG-SINGLE-T-250_VALIDATION.md`](analysis/NG-SINGLE-T-250_VALIDATION.md).

The first clean bottom-loaded replicate, `NG-SINGLE-B-250` R2, reproduced the directional-heating pilot under strict workload isolation. The 250 W bottom card averaged 53.465°C while the idle top card averaged 44.266°C and reached a 45.863°C last-five-minute mean at only 22.548 W. The corresponding clean reverse cell leaves the idle bottom card near 29°C, strengthening the evidence that coupling is strongly bottom-to-top. This cell remains `n=1/3`; coefficients will not be promoted into the validated model until two more admissible replicates exist.

The first clean symmetric replicate, `NG-SYM-250` R2, reproduced the pilot’s thermal result: 52.730°C bottom, 67.613°C top, and a 14.883°C positional delta at equal 250 W caps. Both temperature slopes reached steady state and all thermal/brake counters stayed at zero. GPU1’s clock channel reported a physically inconsistent fixed 180/405 MHz while power, utilization, and throughput remained high; that channel is explicitly excluded from frequency-model fitting until an independent sampler is added. The thermal, fan, power, request-performance, and event-counter channels remain admissible.

`NG-SINGLE-B-250` R3 completed cleanly but is excluded because the idle top temperature was still rising at +0.4834°C/min and the loaded bottom fan at +0.4158 pp/min over the closing three minutes. It followed an unrelated 600 W production heat load on the top card, showing that a cool GPU core does not prove the surrounding chassis/inter-card thermal mass has equilibrated. The run also validated the randomized NVML clock sampler: its 799.476 MHz GPU0 mean agreed with the primary logger’s 799.680 MHz mean to within 0.026%.

The first successful fixed-fan exposure, `NG-FAN-EQ30-SYM250-BUMP` R2,
held all four fans at 30% and approximately 1,201 RPM while both GPUs sustained
250 W and 100% utilization. Over the intentionally short two-minute measured
window, the bottom averaged 48.116°C and the top 57.321°C; the top-minus-bottom
mean was 9.205°C and the end-of-window gap was 13°C. Both cards were still
heating rapidly (+2.8106 and +6.1990°C/min), so this is control/safety
validation rather than equilibrium evidence. Manual states were verified
during load, all four RPM streams were complete, and automatic control was
verified after cleanup.

The five-minute R3 extension held the same 250/250 W and 30/30% policy with
mean physical fan speeds of 1,200.594 and 1,200.674 RPM. Bottom/top mean
temperatures were 49.675/62.276°C and maxima were 54/70°C. The observed
end-of-window gap reached 17°C, while the top closing slope slowed from R2's
+6.1990 to +2.1283°C/min. The cell remained non-steady but retained 23°C of
margin to the reported limit and recorded no thermal events, supporting a
guarded ten-minute extension.

The guarded ten-minute `NG-FAN-EQ30-SYM250` R1 run reached steady state and is
the first internally admissible fixed-fan equilibrium replicate. At equal
249.99 W power and equal 30% / approximately 1,200 RPM fan speed, the bottom
averaged 51.281 C while the top averaged 67.760 C: a 16.479 C positional
penalty with controller response removed. The top also averaged 31.677 MHz
lower and completed 0.8533 requests/s versus 0.9600 requests/s on the bottom.
All thermal/brake counters remained zero. This is `n=1/3` and lacks calibrated
ambient/local-inlet probes, so it supports the internal Tower2 model but is not
yet a transferable server-design coefficient.

[`STACKED_GPU_RESEARCH_PLAN.md`](STACKED_GPU_RESEARCH_PLAN.md) defines the controlled matrix, instrumentation, reduced-order thermal model, and publication formats intended to turn the two-card measurements into bounded three- and four-card stack forecasts.

[`COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md`](COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md) is the canonical execution plan with hypotheses, exact test tiers, acceptance and safety gates, statistical methods, data architecture, model validation, resource estimates, and the publication package.

[`INSTRUMENTATION_AUDIT.md`](INSTRUMENTATION_AUDIT.md) records the telemetry available on Tower2, the current environmental-sensor gap, the harness improvements made for the expanded matrix, and the boundary between internally useful measurements and transferable stack forecasts.

Beginning with the next run, the harness also records all four physical GPU
fans in `gpu-fan-telemetry.csv`: fans 0–1 are GPU0/bottom and fans 2–3 are
GPU1/top. Each sample includes current and target duty plus actual RPM, and new
runs cannot qualify if that channel is missing or incomplete. Fixed-fan
targets became available after replacing an obsolete 510 `nvidia-settings`
client with the 595.58.03 build matching the active driver. All published runs
before this sequence used the stock automatic controller. Loaded fixed-fan
cells now begin only after bump-test validation and require complete target,
duty, and RPM tracking.

[`VALIDATION_STATUS.md`](VALIDATION_STATUS.md) and [`VALIDATION_REGISTRY.csv`](VALIDATION_REGISTRY.csv) enforce the campaign-wide `n >= 3` rule. Qualified pilots and excluded runs remain visible but never count toward the three admissible replicates required for validation.

`aggregate-validation.py` regenerates the machine-readable [`validation-aggregates.json`](analysis/validation-aggregates.json) and [`validation-aggregates.csv`](analysis/validation-aggregates.csv) tables used to track replicate dispersion and determine when a cell actually reaches `n=3`.

[`analysis/FAN_AWARE_CLOSED_LOOP_INTERPRETATION.md`](analysis/FAN_AWARE_CLOSED_LOOP_INTERPRETATION.md)
separates what the stock automatic-controller results establish from the
fixed-airflow questions they cannot yet answer. Its machine-readable source
table is
[`analysis/auto-fan-operating-points.csv`](analysis/auto-fan-operating-points.csv);
fixed-fan observations are kept separately in
[`analysis/fan-controlled-operating-points.csv`](analysis/fan-controlled-operating-points.csv).

[`analysis/250W_PRELIMINARY_COUPLING.md`](analysis/250W_PRELIMINARY_COUPLING.md) compares the equal-load and bottom-only 250 W cells. It finds a strong bottom-to-top heating signal and no resolvable top-to-bottom penalty yet; the reverse isolation cell and randomized repeats are still required before fitting directional coefficients.

[`analysis/250W_FACTORIAL_COUPLING.md`](analysis/250W_FACTORIAL_COUPLING.md) adds the reverse isolation cell and derives preliminary closed-loop self-heating and directional coupling coefficients. Bottom-to-top coupling is approximately 0.042–0.047°C/W at this operating point; top-to-bottom coupling remains indistinguishable from zero. The reverse cell is quality-flagged and requires a clean repeat before model fitting.

## Read order

1. Each run directory's `REPORT.md` gives the human-readable result.
2. `summary.json` contains machine-readable aggregate statistics.
3. `gpu-telemetry.csv`, `gpu-fan-telemetry.csv` on new runs,
   `host-telemetry.csv`, and `requests.csv` contain the raw samples.
4. `nvidia-before.txt`, `nvidia-after.txt`, events, payloads, and logs preserve the audit trail.
5. `dual-vllm-qwen27-30m.sh` and `summarize-dual-vllm.py` are the tested harness and summarizer.

The 30-minute run also recorded high host CPU thermals: 95.8°C maximum Tctl and a 98.6°C maximum CCD reading. Host CPU/CCD temperature, not GPU throttling, was the principal safety observation.
