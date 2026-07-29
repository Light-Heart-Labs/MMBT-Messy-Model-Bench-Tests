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

The summarizer now reports target-relative power saturation, telemetry completeness, temperature-limit margin, steady-state slopes, sampled counter deltas, request rate, ambient statistics when supplied, and top-minus-bottom deltas.

## Required additions before transferable 3x/4x claims

At minimum, attach calibrated probes at room ambient, each card intake, the inter-card channel, and chassis exhaust. Record probe identifiers, placement photographs, calibration offsets, and sampling alignment. Add wall-power measurement if the public output will include facility power or energy-efficiency claims.

Until those measurements exist, three- and four-card results will be explicitly labeled as bounded, conditional forecasts based on internal GPU telemetry—not validated thermal design limits.
