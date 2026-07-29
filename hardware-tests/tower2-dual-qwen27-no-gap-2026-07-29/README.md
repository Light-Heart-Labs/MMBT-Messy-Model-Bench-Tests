# Tower2 dual-GPU no-gap thermal study — 2026-07-29

Two RTX PRO 6000 Blackwell Workstation Edition GPUs were installed directly adjacent, with no open-slot air gap. GPU1 is the top card in `PCIEx16(G5)_1`; GPU0 is the bottom card in `PCIEx16(G5)_3`.

Each card runs an independent Qwen3.6-27B AWQ-INT4 vLLM engine with 32 concurrent requests. The study begins with a 600 W bottom / 400 W top cell and adds an equal 500/500 W cell matching an external 10-minute SM120 thermal-stress specification.

## Results

| Run | Bottom mean / max / fan | Top mean / max / fan | Throttling |
|---|---|---|---|
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

[`STACKED_GPU_RESEARCH_PLAN.md`](STACKED_GPU_RESEARCH_PLAN.md) defines the controlled matrix, instrumentation, reduced-order thermal model, and publication formats intended to turn the two-card measurements into bounded three- and four-card stack forecasts.

[`COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md`](COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md) is the canonical execution plan with hypotheses, exact test tiers, acceptance and safety gates, statistical methods, data architecture, model validation, resource estimates, and the publication package.

[`INSTRUMENTATION_AUDIT.md`](INSTRUMENTATION_AUDIT.md) records the telemetry available on Tower2, the current environmental-sensor gap, the harness improvements made for the expanded matrix, and the boundary between internally useful measurements and transferable stack forecasts.

[`analysis/250W_PRELIMINARY_COUPLING.md`](analysis/250W_PRELIMINARY_COUPLING.md) compares the equal-load and bottom-only 250 W cells. It finds a strong bottom-to-top heating signal and no resolvable top-to-bottom penalty yet; the reverse isolation cell and randomized repeats are still required before fitting directional coefficients.

[`analysis/250W_FACTORIAL_COUPLING.md`](analysis/250W_FACTORIAL_COUPLING.md) adds the reverse isolation cell and derives preliminary closed-loop self-heating and directional coupling coefficients. Bottom-to-top coupling is approximately 0.042–0.047°C/W at this operating point; top-to-bottom coupling remains indistinguishable from zero. The reverse cell is quality-flagged and requires a clean repeat before model fitting.

## Read order

1. Each run directory's `REPORT.md` gives the human-readable result.
2. `summary.json` contains machine-readable aggregate statistics.
3. `gpu-telemetry.csv`, `host-telemetry.csv`, and `requests.csv` contain the raw samples.
4. `nvidia-before.txt`, `nvidia-after.txt`, events, payloads, and logs preserve the audit trail.
5. `dual-vllm-qwen27-30m.sh` and `summarize-dual-vllm.py` are the tested harness and summarizer.

The 30-minute run also recorded high host CPU thermals: 95.8°C maximum Tctl and a 98.6°C maximum CCD reading. Host CPU/CCD temperature, not GPU throttling, was the principal safety observation.
