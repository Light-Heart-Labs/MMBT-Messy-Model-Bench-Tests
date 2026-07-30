# Tower2 instrumentation and harness audit

**Audit date:** 2026-07-29  
**Scope:** Current Tower2 no-gap RTX PRO 6000 Blackwell test configuration

## Available measurements

The installed NVIDIA 595.58.03 driver exposes the following per-GPU fields through `nvidia-smi`:

- GPU core temperature and distance to the GPU temperature limit
- average and instantaneous board power
- configured and enforced power limits
- graphics, SM, and memory clocks
- GPU and memory-controller utilization
- fan percentage, performance state, and memory use
- instantaneous software power-cap, software thermal, hardware thermal, and hardware power-brake reasons
- cumulative microsecond counters for each of those four clock-event reasons

Host telemetry available through `lm-sensors` and `/proc` includes CPU package/CCD temperatures, CPU frequency, and NVMe temperatures. GPU memory temperature is reported as unavailable by this driver/card combination.

The active X/NV-CONTROL server exposes four physical GPU fan targets through
`nvidia-settings`. Fans 0–1 map to GPU0/bottom and fans 2–3 map to GPU1/top;
the mapping was confirmed while the two GPUs occupied unequal live fan states
and each fan pair matched its GPU's independent `nvidia-smi` duty. Available
fields are current duty, target duty, and actual per-fan RPM. At the 30% idle
floor, the four fans report approximately 1,200 RPM.

`nvidia-smi fan.speed` is the intended percentage of the product's maximum
noise-tolerance fan speed; it is not direct airflow and must not be treated as
linear CFM. Actual RPM is a better mechanical control measurement, but RPM
also is not equivalent to airflow through an obstructed stack.

## Missing measurements

No external environmental probes are currently attached. Tower2 therefore cannot directly record:

- room ambient temperature;
- each GPU's local intake temperature;
- inter-card air temperature;
- chassis exhaust temperature;
- air velocity or volumetric flow;
- wall or PSU-input power;
- sound pressure.

NVIDIA DCGM and `nv-hostengine` are also not installed. NVML/NVIDIA-SMI telemetry is sufficient for the present core study, but DCGM profiling metrics would add SM occupancy, tensor utilization, DRAM activity, PCIe/NVLink activity, and more robust counter collection.

Runs without physical inlet/ambient measurements remain useful for within-session card and power comparisons, but they are not environmentally normalized and must not be treated as transferable chassis forecasts.

## Harness changes made after the audit

The canonical `dual-vllm-qwen27-30m.sh` harness now:

- supports independent GPU0 and GPU1 worker counts, including one loaded card and one model-resident idle card;
- accepts 100 ms or slower NVIDIA telemetry intervals;
- records temperature-limit margin and cumulative clock-event counters in every GPU sample;
- records an optional manually measured ambient temperature;
- rejects starts above configured per-GPU temperature thresholds;
- rejects starts while the resident Sanctuary endpoint has running or waiting requests;
- aborts if a hardware thermal or hardware power-brake counter increases;
- records before/after NVIDIA XML, host state, container state, and Sanctuary metrics;
- writes target power, per-GPU concurrency, start gates, and telemetry cadence into `run-config.json`;
- generates SHA-256 hashes for the completed run artifacts after cleanup.
- records stable matrix-cell and replicate identifiers for the `n >= 3` validation ledger;
- stops the OpenClaw gateway to clear its GPU embedding workers, aborts if a worker respawns, and restores the service after cleanup;
- isolates external request sources before evaluating the start-temperature gates, waits for both GPUs to reach 0% utilization and the configured temperature limits, and restores any service stopped during preflight even if the run is rejected;
- requires a configurable continuous quiescent soak after both GPUs first satisfy the utilization/temperature gates, resetting the soak if either condition is violated, and records the five-second preflight trace in `preflight-telemetry.csv`;
- applies a configurable maximum-power cutoff to every nominally idle GPU;
- verifies that Sanctuary's cumulative successful-request delta exactly matches the controlled request log before a run can pass;
- emits machine-readable internal and transferable admissibility candidates;
- records a second graphics/SM/memory-clock stream through direct NVML calls at a randomized 173–274 ms cadence, independent of the fixed-period primary telemetry logger.
- records all four physical GPU fans continuously at 1 Hz in
  `gpu-fan-telemetry.csv`, including current duty, target duty, actual RPM,
  GPU/card-position mapping, completeness, and target-tracking error;
- requires complete nonzero four-fan telemetry for new runs to qualify as
  internally admissible, and places per-fan/per-GPU RPM distributions in
  `summary.json` and standardized PNG reports.

The independent NVML stream was added after `NG-SYM-250` replicate 2 reported a physically inconsistent fixed 180 MHz graphics/SM and 405 MHz memory clock while GPU1 simultaneously held 250 W, 100% utilization, and substantial request throughput. The thermal and workload channels passed, but the affected primary-clock metrics are excluded from validation aggregation. The jittered stream is preserved and summarized separately so clock-source disagreements remain visible rather than being silently reconciled.

`NG-SINGLE-B-250` replicate 3 then validated the new stream against the primary logger: 799.476 versus 799.680 MHz mean graphics clock. That run was excluded thermally because a preceding 600 W production heat load left the idle top card warming at +0.4834°C/min through the closing window. This prompted the continuous quiescent-soak requirement; core-temperature admission alone does not control unmeasured chassis and inter-card thermal history.

## Fixed-fan control status

NV-CONTROL advertises `GPUFanControlState` and `GPUTargetFanSpeed`, but a
fail-safe idle mapping test on 2026-07-29 found that target assignments return
`Unknown Error` under the current X-server configuration. Both GPU control
states were explicitly restored to automatic mode after the test. No
fixed-fan result has been collected, and the presence of queryable attributes
must not be described as working manual fan control.

The likely missing prerequisite is an X-server Coolbits fan-control option.
Enabling it would require an X configuration change and display-server restart
or host reboot, which was not attempted while Tower2 was serving a live 600 W
GPU1 production workload. Until a controlled maintenance window is approved,
the campaign can collect actual RPM under the stock controller but cannot yet
execute the fixed-fan identification matrix.

The summarizer now reports target-relative power saturation, telemetry completeness, temperature-limit margin, steady-state slopes, sampled counter deltas, request rate, ambient statistics when supplied, top-minus-bottom deltas, and independent NVML clock distributions. The validation registry supports per-run `metric_exclusions`, allowing a bad sensor channel to be removed from a model without discarding otherwise admissible thermal evidence.

## Required additions before transferable 3x/4x claims

At minimum, attach calibrated probes at room ambient, each card intake, the inter-card channel, and chassis exhaust. Record probe identifiers, placement photographs, calibration offsets, and sampling alignment. Add wall-power measurement if the public output will include facility power or energy-efficiency claims.

Until those measurements exist, three- and four-card results will be explicitly labeled as bounded, conditional forecasts based on internal GPU telemetry—not validated thermal design limits.
