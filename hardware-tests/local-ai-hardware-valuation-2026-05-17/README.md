# Local AI hardware valuation snapshot - 2026-05-17

This is a derived analysis, not a new benchmark run. It turns the cross-platform
Q8 hardware results into a repeatable "value investor" view of local AI
hardware: what are you paying for memory capacity, memory bandwidth, and
measured inference speed?

The goal is not to name one permanent winner. Prices move, software stacks
improve, and the right machine depends on whether you need CUDA, Metal, Vulkan,
Linux appliance behavior, laptop portability, or raw discrete-GPU speed. The
goal is to give readers a small set of durable ratios they can recompute when
the market changes.

## Files

| File | Purpose |
|---|---|
| `inputs/systems.csv` | Editable price/spec snapshot. Update this when prices change. |
| `outputs/valuation.csv` | Generated ratios. Do not hand-edit; regenerate from the script. |
| `../../qwen3.6-q8-fleet-2026-05-17/aggregate/canonical-headline.csv` | Measured MMBT 27B Q8 prefill/decode inputs. (The legacy `headline.csv` still works as a `--headline` override; `canonical-headline.csv` is the non-deprecated source.) |
| `../../../tooling/scripts/hardware_valuation.py` | Recomputes the valuation table from the two CSV inputs. |

Regenerate after a price refresh:

```bash
python tooling/scripts/hardware_valuation.py
```

## Mental model

Read local AI hardware value in four passes:

1. **Fit**: can the machine hold the model, KV cache, and runtime overhead?
   The first ratio is `$/usable AI GB`.
2. **Feed**: how much memory bandwidth is available to stream weights and KV
   during inference? The second ratio is `$/GB/s`.
3. **Prove**: what speed did it actually produce on a pinned workload? The
   measured ratios are `$/decode tok/s` and `$/prefill tok/s`.
4. **Survive**: what does it cost to run, cool, and operate with the software
   stack you need? This snapshot includes a rough 5-year energy line, but the
   wall-power measurements are not equally strong across hosts.

Prefer dollar-denominated ratios when explaining value:

| Metric | Formula | Reads as | Better |
|---|---:|---|---:|
| `$/usable AI GB` | `price / memory_gb_for_value` | cost of model-fitting capacity | lower |
| `$/GB/s` | `price / memory_bandwidth_gbps` | cost of bandwidth | lower |
| `$/decode tok/s` | `price / measured_decode_tps` | cost of measured streaming speed | lower |
| `$/prefill tok/s` | `price / measured_prefill_tps` | cost of measured prompt-read speed | lower |
| `capacity_bandwidth_score` | `memory_gb_for_value * memory_bandwidth_gbps` | crude capacity-times-bandwidth scale | higher |

`tok/s per $1k` is still generated because it is common in benchmark writeups,
but it is easier to misread. If you use it, say "higher is better" every time.
For buyer-facing prose, `$/tok/s` is usually clearer.

## Snapshot read

Current generated output, using the bundled price/spec assumptions:

| System | Price | Usable AI GB | GB/s | `$/GB` | `$/GB/s` | 27B Q8 decode | `$/decode tok/s` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Blackwell 6000 Tower, single-RTX-6000 anchor | $12,000 | 96 | 1792 | $125.00 | $6.70 | 49.78 | $241.04 |
| Blackwell 6000 Tower, as-configured server | $33,000 | 96 | 1792 | $343.75 | $18.42 | 49.78 | $662.86 |
| M5 Max MacBook Pro 16 | $4,850 | 128 | 614 | $37.89 | $7.90 | 16.78 | $288.97 |
| NVIDIA DGX Spark | $4,699 | 121 | 273 | $38.83 | $17.21 | 7.60 | $618.21 |
| EVO X2 / Strix Halo | $3,000 | 124 | 256 | $24.19 | $11.72 | 7.82 | $383.59 |
| Framework Strix Halo mainboard 128GB | $2,699 | 124 | 256 | $21.77 | $10.54 | - | - |

The Framework row is included as a market-comparison input only. It is a
mainboard-only candidate, not a complete system, and it has no MMBT throughput
measurement.

## Reading the Spark / Strix / M5 cluster

Under this snapshot, DGX Spark does not look like a cheap memory asset. It is
close to M5 Max on price, but buys less than half the memory bandwidth and less
than half the measured 27B Q8 decode speed in this workload. Its premium has to
be justified by the NVIDIA software stack, CUDA compatibility, ConnectX, DGX OS,
support posture, or another NVIDIA-specific requirement.

EVO X2 / Strix Halo is cheaper on capacity and bandwidth. It is roughly similar
to DGX Spark on measured 27B Q8 decode in this dataset, while Spark is much
stronger on prefill. That makes Strix Halo look attractive as a cheap-capacity
local AI box, but the repo's backend findings matter: Vulkan worked, ROCm did
not in this snapshot, and the small chassis ran hot.

M5 Max is the cleanest "balanced memory appliance" row here: same capacity class
as Spark, much higher bandwidth, and much better measured decode. Its tradeoff
is ecosystem, not raw memory value: Metal/macOS is not CUDA/Linux, and that
matters for some serving stacks.

The Blackwell 6000 Tower is the opposite profile: expensive capacity, excellent
bandwidth, excellent measured speed. It is a speed purchase, not the cheapest
way to buy 100 GB-class memory.

## What this can and cannot settle

This analysis can support narrow statements like:

- "At this price snapshot, System A is cheaper than System B per usable AI GB."
- "At this price snapshot, System A buys bandwidth more cheaply than System B."
- "On MMBT's pinned 27B Q8 single-user workload, System A costs less per
  measured decode tok/s than System B."

It should not be used alone to claim:

- best hardware for every model size or quantization
- best multi-user serving hardware
- best system after future driver/backend changes
- best total cost of ownership without plug-metered wall power on every host
- best choice for buyers who require a specific software ecosystem

## Better plots

For a trusted hardware-buying page, make these charts from `outputs/valuation.csv`:

1. **Capacity vs bandwidth**: x-axis usable AI GB, y-axis GB/s, bubble size
   price, color software ecosystem. This shows what kind of asset each system is.
2. **Price vs capacity-bandwidth score**: add a trendline. Systems far below
   the line are cheap memory assets; systems above it need a software or
   performance premium.
3. **Price vs measured decode tok/s**: only include systems with the same model,
   quant, engine class, and concurrency status.
4. **`$/tok/s` by workload**: separate decode, prefill, and TTFT-sensitive
   workloads. A single blended score hides too much.

## Make it more defensible

To turn this from a useful snapshot into a more trusted source of truth:

- Refresh `inputs/systems.csv` with source URL, region, tax/shipping stance, and
  exact SKU before publishing a price conclusion.
- Keep both advertised memory and conservative usable AI memory. Use the
  conservative column for default valuation.
- Add plug-meter wall power for the same cell on every host, then report
  energy/token and 5-year TCO with multiple electricity prices.
- Add best-stack rows per hardware class: vLLM/TensorRT-LLM on NVIDIA, MLX on
  Apple, ROCm and Vulkan on AMD. Do not make buyers price broken software paths
  as if they are working paths.
- Repeat canonical cells across days and randomize run order to catch thermal,
  firmware, and background-load drift.
- Separate single-user, batch-serving, and long-context serving. They are
  different investments.
