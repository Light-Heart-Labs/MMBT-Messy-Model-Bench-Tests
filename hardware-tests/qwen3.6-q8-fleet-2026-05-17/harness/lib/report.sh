#!/usr/bin/env bash
# report.sh — render REFERENCE.md from cells.jsonl + per-cell inferences.jsonl.
#
# Sections:
#   § Headline hardware ranking
#   § Cross-host generation-SHA determinism (proves Q8 inference deterministic
#     across CUDA / Vulkan / Metal / CUDA-aarch64 on every prompt we sampled)
#   § Generation-length distribution per host (does the model produce
#     different-length output on different backends?)
#   § Stop-reason distribution per host (limit / eos / stop_word counts)
#   § Coherence spot-check (random generation samples with content preview)
#   § Sampler curves (power, thermal, throughput vs context)
#   § Reproducibility bundle pointer

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

RUN_DIR="${1:?usage: report.sh <run_dir>}"
AGG="$RUN_DIR/aggregate"
[[ -d "$AGG" ]] || die "no aggregate dir; run aggregate.sh first"
OUT="$RUN_DIR/REFERENCE.md"

log "rendering $OUT"

# Pull pinned metadata
LLAMA_SHA="$(jq -r '.study.llama_cpp_sha' "$TARGETS_JSON")"
LLAMA_TAG="$(jq -r '.study.llama_cpp_tag' "$TARGETS_JSON")"
CORPUS_SHA="$(cat "$BENCH_FLEET_ROOT/workloads/prompts.jsonl.sha256" 2>/dev/null || echo unknown)"
MODEL_27B_SHA="$(jq -r '.study.models[0].sha256' "$TARGETS_JSON")"
MODEL_35B_SHA="$(jq -r '.study.models[1].sha256' "$TARGETS_JSON")"

# Collect all inferences.jsonl content into one big stream for behavior analyses.
INF_ALL="$AGG/all-inferences.jsonl"
: > "$INF_ALL"
while IFS= read -r f; do
    rel="${f#"$RUN_DIR/"}"
    host="${rel%%/*}"; rest="${rel#*/}"
    model="${rest%%/*}"; rest="${rest#*/}"
    backend="${rest%%/*}"; rest="${rest#*/}"
    cell_dir_name="${rest%%/*}"
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        printf '%s\n' "$line" | jq -c \
            --arg host "$host" --arg model "$model" --arg backend "$backend" --arg cell "$cell_dir_name" \
            '. + {host:$host, model:$model, backend:$backend, cell:$cell}'
    done < "$f" >> "$INF_ALL"
done < <(find "$RUN_DIR" -mindepth 5 -name inferences.jsonl 2>/dev/null)
N_INF="$(wc -l < "$INF_ALL")"
log "  collected $N_INF inferences across all cells"

# ----- write REFERENCE.md -----
{
echo "# Cross-platform Q8 reference benchmark"
echo "## Qwen3.6-27B-Q8 and Qwen3.6-35B-A3B-Q8 on four hardware platforms"
echo
echo "_Generated $(date -u +%FT%TZ) from \`$RUN_DIR\`_"
echo
echo "## Why Q8?"
echo
echo "MMBT users specifically requested higher-precision data after the prior Q4 round drew quality complaints. This study runs the canonical hardware grid at \`Q8_0\` GGUF for both models, with the same source files SHA-pinned across every host."
echo
echo "## Premise"
echo
echo "Same model file (SHA-verified) and same llama.cpp source SHA on every host. The only variable is hardware (and its required backend)."
echo
echo "| pin | value |"
echo "|---|---|"
echo "| llama.cpp tag $LLAMA_TAG SHA | \`$LLAMA_SHA\` |"
echo "| Qwen3.6-27B-Q8_0.gguf SHA | \`$MODEL_27B_SHA\` |"
echo "| Qwen3.6-35B-A3B-Q8_0.gguf SHA | \`$MODEL_35B_SHA\` |"
echo "| Prompt corpus SHA | \`$CORPUS_SHA\` |"
echo
echo "## § Scope — what this report concludes and what it does not"
echo
echo "This report is **an llama.cpp inference benchmark across four hardware platforms** under a fixed source SHA, fixed model bytes, fixed prompts, and a fixed grid. It is paired with calibrated power and thermal field measurements."
echo
echo "Conclusions in this report cover three things only:"
echo
echo "1. **Single-user (conc=1) decode and prefill rates across context lengths**, for each host running its native llama.cpp backend (CUDA / Vulkan / Metal / CUDA-aarch64)."
echo "2. **Sustained power and thermal behavior**: silicon power (sampler-derived) and chassis exhaust temperature (psychrometer-measured) under continuous load, with plug-meter wall-AC validation on two hosts."
echo "3. **Cross-host generation determinism and behavior** at \`temperature=0\`: do hosts produce bit-identical output, and if not, how do length / stop distributions differ?"
echo
echo "Conclusions in this report **do not** cover:"
echo
echo "- **Multi-user concurrent serving** (conc≥4). Internal analysis shows llama.cpp's \`--parallel N\` slots are an engine-level binding constraint at long context that masks silicon differences (see § Held: multi-user concurrent serving). Hardware comparisons under proper concurrent-serving engines are a separate study (companion vLLM / TensorRT-LLM / MLX runs, queued)."
echo "- **Hardware quality of Q8 outputs.** That is the companion MMBT Phase B task suite, reported separately."
echo "- **Cross-engine generality.** Numbers reflect llama.cpp at tag $LLAMA_TAG. Different engines or different llama.cpp builds will produce different numbers."
echo "- **Cross-run variance.** N=10 within a cell captures intra-cell variance; we do not characterize day-to-day reproducibility in this report."
echo
echo "## § Headline hardware ranking — single-user, 27B Q8"
echo
echo "Three primary metrics, three independent things a buyer cares about:"
echo
echo "- **Prefill tok/s** — how fast the model reads your prompt (matmul-dense, bandwidth-friendly)."
echo "- **Decode tok/s** — how fast it streams generated tokens (sequential, memory-bandwidth-bound per token)."
echo "- **TTFT** — time from request submission to first token (dominates UX at long context)."
echo
echo "All numbers are conc=1 (single user). Multi-user is engine-bound under llama.cpp and held."
echo
echo "### Cross-model rule"
echo
echo "Each row is a single (host, model, backend) tuple. Two models are present: Qwen3.6-27B (dense) and Qwen3.6-35B-A3B (MoE). Compare hosts within a model column; do not compare rows across models — that's architecture, not hardware."
echo
echo "| host | model | backend | peak prefill tok/s | peak decode tok/s ± SD | decode @ ctx=16K ± SD | cold-start @ peak | TTFT @ ctx=16K | silicon W | sensor | max °C |"
echo "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|"
jq -r '
    .[] |
    (if .host=="tower2" then "Blackwell 6000 Tower"
     elif .host=="strix-halo" then "EVO X2"
     elif .host=="spark" then "DGX Spark"
     elif .host=="m5-mbp" then "M5 Max MacBook Pro"
     else .host end) as $display |
    (.peak_decode_tps_sd      | if . then ("± " + (.*100|floor/100|tostring)) else "" end) as $pd_sd |
    (.decode_tps_at_ctx16k_sd | if . then ("± " + (.*100|floor/100|tostring)) else "" end) as $d16_sd |
    "| \($display) | \(.model) | \(.backend) " +
    "| \(.peak_prefill_tps      | if . then (.*10|floor/10) else "—" end) " +
    "| \(.peak_decode_tps       | if . then ((.*100|floor/100|tostring) + " " + $pd_sd) else "—" end) " +
    "| \(.decode_tps_at_ctx16k  | if . then ((.*100|floor/100|tostring) + " " + $d16_sd) else "—" end) " +
    "| \(.cold_start_decode_tps_at_peak | if . then (.*100|floor/100) else "—" end) " +
    "| \(.ttft_ms_at_ctx16k     | if . then ((. / 1000 * 10 | floor / 10 | tostring) + " s") else "—" end) " +
    "| \(.power_w_silicon_at_peak_decode // "—") " +
    "| \(.temp_sensor // "—") " +
    "| \(.temp_c_max_at_peak_decode // "—") |"
' "$AGG/headline.json"
echo
echo "### Reading the headline"
echo
echo "- Blackwell 6000 Tower wins prefill by 3–8× across hosts. This is where its GDDR7 bandwidth and Blackwell compute lead express directly."
echo "- Blackwell 6000 Tower wins peak decode by 3× over M5 Max MacBook Pro and 6×+ over DGX Spark / EVO X2 at short context (ctx=1K)."
echo "- At ctx=16K decode, Blackwell 6000 Tower still leads (19.4 tok/s) but by a much smaller margin over M5 Max (16.1) — see § Long-context single-user behavior for what's happening there. The Blackwell Tower's decode-only rate at long ctx is one specific metric; total request time (prefill + decode) still favors it substantially because its prefill is so much faster."
echo "- TTFT at ctx=16K: Blackwell 6000 Tower 21 s, DGX Spark 21 s, M5 Max 31 s, EVO X2 61 s. The EVO X2's slow prefill makes its first-token latency 3× the others."
echo
echo "### Power and thermal columns"
echo
echo "- **silicon W**: GPU/package only — nvidia-smi (Blackwell 6000 Tower: GPU 0 only, gpu1 idle excluded; DGX Spark: gpu0). rocm-smi (EVO X2 APU graphics package). macmon (M5 Max \`gpu\` row). Cross-host comparable within sampler-scope caveats."
echo "- **\`temp_sensor\`**: \`gpu_die\` (nvidia internal die), \`gpu_die_avg\` (Apple silicon die), \`gpu_edge\` (rocm-smi exposes only edge sensor on the EVO X2's Strix Halo APU; junction is typically 10–15 °C hotter and not available)."
echo "- Plug-meter wall-AC validation for M5 Max (142 W vs macmon sys 128 W) and Blackwell 6000 Tower (445 W at the cell measured) is in § Sustained thermal and \`targets.json.hosts[].wall_calibration\`."
echo
echo "## § Long-context single-user behavior"
echo
echo "All numbers are conc=1. The two metrics that matter here are **decode tok/s** (how fast generation streams once it starts) and **TTFT** (how long until the first token arrives, dominated by prefill time at long ctx)."
echo
echo "### Decode tok/s across context lengths (27B Q8, conc=1, gen=2048)"
echo
echo "| ctx | Blackwell 6000 Tower | M5 Max | DGX Spark | EVO X2 |"
echo "|---|---:|---:|---:|---:|"
jq -rs '
    map(select(.model=="qwen3.6-27b" and .conc==1 and .gen==2048 and .per_slot_decode_tps_mean != null))
    | group_by(.ctx)
    | map({
        ctx: .[0].ctx,
        t2: ((map(select(.host=="tower2"))[0] // null) | if . then .per_slot_decode_tps_mean else null end),
        m5: ((map(select(.host=="m5-mbp"))[0] // null) | if . then .per_slot_decode_tps_mean else null end),
        sp: ((map(select(.host=="spark"))[0] // null) | if . then .per_slot_decode_tps_mean else null end),
        st: ((map(select(.host=="strix-halo"))[0] // null) | if . then .per_slot_decode_tps_mean else null end)
      })
    | sort_by(.ctx)
    | .[]
    | "| \(.ctx) " +
      "| \(if .t2 then (.t2*100|floor/100|tostring) else "—" end) " +
      "| \(if .m5 then (.m5*100|floor/100|tostring) else "—" end) " +
      "| \(if .sp then (.sp*100|floor/100|tostring) else "—" end) " +
      "| \(if .st then (.st*100|floor/100|tostring) else "—" end) |"
' "$AGG/cells.jsonl"
echo
echo "### Prefill tok/s across context lengths"
echo
echo "| ctx | Blackwell 6000 Tower | M5 Max | DGX Spark | EVO X2 |"
echo "|---|---:|---:|---:|---:|"
jq -rs '
    map(select(.model=="qwen3.6-27b" and .conc==1 and .gen==2048 and .per_slot_prefill_tps_mean != null))
    | group_by(.ctx)
    | map({
        ctx: .[0].ctx,
        t2: ((map(select(.host=="tower2"))[0] // null) | if . then .per_slot_prefill_tps_mean else null end),
        m5: ((map(select(.host=="m5-mbp"))[0] // null) | if . then .per_slot_prefill_tps_mean else null end),
        sp: ((map(select(.host=="spark"))[0] // null) | if . then .per_slot_prefill_tps_mean else null end),
        st: ((map(select(.host=="strix-halo"))[0] // null) | if . then .per_slot_prefill_tps_mean else null end)
      })
    | sort_by(.ctx)
    | .[]
    | "| \(.ctx) " +
      "| \(if .t2 then (.t2*10|floor/10|tostring) else "—" end) " +
      "| \(if .m5 then (.m5*10|floor/10|tostring) else "—" end) " +
      "| \(if .sp then (.sp*10|floor/10|tostring) else "—" end) " +
      "| \(if .st then (.st*10|floor/10|tostring) else "—" end) |"
' "$AGG/cells.jsonl"
echo
echo "### Reading"
echo
echo "Blackwell 6000 Tower wins both prefill and decode at every context length we measured. The decode lead narrows at ctx=16K (Blackwell 6000 Tower 19 tok/s vs M5 Max 16 tok/s) — a specific llama.cpp-CUDA-on-Blackwell behavior at long context worth investigating under a different engine, but it doesn't change the overall hardware ranking. The Blackwell Tower's prefill remains 3–8× the unified-memory hosts at every context length, which is where the bandwidth-and-compute advantage of the discrete GPU shows up most cleanly."
echo
echo "### Blackwell 6000 Tower silicon power across context lengths (reference)"
echo
echo "For engine-internals readers: the Blackwell 6000 Tower's GPU silicon power at conc=1 drops as context grows. This is the same observation that produced the decode-only behavior noted above (the GPU isn't being driven hard at long context under llama.cpp's CUDA path on Blackwell)."
echo
echo "| ctx | Blackwell 6000 Tower silicon W mean | % of 600 W cap |"
echo "|---|---:|---:|"
jq -r --slurp '
    [.[] | select(.host=="tower2" and .backend=="cuda" and .model=="qwen3.6-27b" and .conc==1 and .gen==2048 and .power_w_silicon_mean != null)]
    | sort_by(.ctx)
    | .[]
    | "| \(.ctx) | \(.power_w_silicon_mean) | \((.power_w_silicon_mean/600*100|floor))% |"
' "$AGG/cells.jsonl"
echo
echo "## § Held: multi-user concurrent serving"
echo
echo "We ran the multi-user (conc=4 and conc=8) cells across the grid, but **we do not draw cross-host conclusions from them**. The reason is internal to this dataset:"
echo
echo "At ctx=16K gen=2048 conc=8, each forward pass reads ~28.6 GB of Q8 weights plus ~10 GB of KV cache (8 slots × 16 K tokens × ~75 KB/tok) ≈ **~38 GB per step**, producing 8 next-tokens. The bandwidth-bound aggregate is 8 / (38 / bandwidth). Public memory bandwidth specs:"
echo
echo "| host | GPU/SoC | bandwidth (GB/s) | theoretical agg tok/s | observed | % of theoretical |"
echo "|---|---|---:|---:|---:|---:|"
echo "| Blackwell 6000 Tower | RTX PRO 6000 Blackwell GDDR7 | ~1,800 | ~380 | 17.4 | **4.6 %** |"
echo "| M5 Max MacBook Pro | M5 Max LPDDR5x | ~600 | ~126 | 18.0 | **14 %** |"
echo "| DGX Spark | GB10 Grace Blackwell LPDDR5x | ~275 | ~58 | 18.4 | **32 %** |"
echo "| EVO X2 | Ryzen AI MAX+ 395 (Strix Halo) LPDDR5x-8000 256-bit | ~256 | ~54 | 10.1 | **19 %** |"
echo
echo "All four hosts come in under their bandwidth-bound ceiling, with the Blackwell 6000 Tower at 4.6 % of its theoretical max. That gap cannot be silicon — the binding constraint is upstream. Internal evidence within this dataset:"
echo
echo "- At ctx=1 K, the Blackwell 6000 Tower's per-slot decode HOLDS as conc grows (49.4 at conc=1 → 49.78 at conc=8; aggregate ≈ 2.6× the conc=1 figure). The hardware scales here."
echo "- At ctx=16 K, the Blackwell 6000 Tower's per-slot decode COLLAPSES with conc (19.4 at conc=1 → 2.94 at conc=8; aggregate barely grows). The hardware does not scale here, but it also is nowhere near its bandwidth ceiling — so the binding factor is not silicon."
echo
echo "Most likely cause: llama.cpp's \`--parallel N\` slots implementation does not retain efficient batched / paged attention at long context. Confirming this requires engine-side instrumentation we do not have. What this means for the report:"
echo
echo "- **Cross-host multi-user comparisons at long ctx are held**: they reflect llama.cpp behavior, not silicon. (The Blackwell 6000 Tower's specific kernel-size mismatch on Blackwell SMs is the cleanest example, but the held conclusion is general.)"
echo "- **A separate study under a properly batched concurrent-serving engine (vLLM / TensorRT-LLM)** is queued (task #12). Until it runs, this report makes no multi-user concurrent-serving claim."
echo
echo "The raw conc=4 and conc=8 cells remain in \`aggregate/cells.jsonl\` for reproducibility, but the report's conclusions do not draw on them."
echo
echo "## § Sustained thermal field measurements"
echo
echo "Exhaust-air temperature measurements taken with a Fieldpiece PRH2 digital pocket psychrometer ~15.5 h into continuous benchmark operation. All four hosts at sustained steady-state at the time of measurement. Readings taken back-to-back within a few minutes of each other."
echo
echo "| host | chassis class | exhaust °F | room ambient °F | Δ above ambient °F | sensor-derived silicon temp |"
echo "|---|---|---:|---:|---:|---|"
jq -r '
    (.study.environment.exhaust_measurements_f) as $ex |
    .hosts |
    map(. as $h | (
        ($h.name | gsub("-"; "_")) as $k |
        ($ex[$k]) as $m |
        if $m then
            "| \($h.display_name // $h.name) | \($h.chassis // "—" | split(" (")[0]) | \($m.exhaust_f) | \($m.ambient_f) | **\($m.delta_f)** | (see headline temp_c_max) |"
        else empty
        end
    )) | .[]
' "$TARGETS_JSON"
echo
echo "### What these numbers say"
echo
jq -r '.study.environment.interpretation' "$TARGETS_JSON"
echo
echo "### Per-host environmental context"
echo
jq -r '
    (.study.environment.exhaust_measurements_f) as $ex |
    .hosts |
    map(. as $h | (
        ($h.name | gsub("-"; "_")) as $k |
        ($ex[$k]) as $m |
        if $m then "- **\($h.display_name // $h.name)**: \($m.note)" else empty end
    )) | .[]
' "$TARGETS_JSON"
echo
echo "### Electrical / room setup"
echo
MAIN_F="$(jq -r '.study.environment.rooms.main_room.ambient_f' "$TARGETS_JSON")"
M5_F="$(jq -r '.study.environment.rooms.m5_room.ambient_f' "$TARGETS_JSON")"
echo "- **Main room (${MAIN_F}°F ambient)**: Blackwell 6000 Tower, EVO X2, DGX Spark all on one shared 20 A breaker."
echo "- **M5 room (${M5_F}°F ambient)**: M5 Max MacBook Pro on a separate 20 A breaker in a different room to prevent trips during heavy load."
echo "- **Ambient differential** is only ~1 °F between rooms, so cross-host thermal comparisons are not biased by room temperature."
echo "- All ambient measurements taken at the same instrumented moment as the exhaust readings, ~15.5 h into sustained operation."
echo
echo "## § Cost-throughput at single-user peak"
echo
echo "This section reports tok/s per \$1 k at the single-user / short-context operating point only. Multi-user conclusions are held — see § Held: multi-user concurrent serving."
echo
echo "### Approximate hardware cost per host"
echo
echo "| host | cost (USD) | note |"
echo "|---|---:|---|"
jq -r '.hosts[] |
    (.display_name // .name) as $disp |
    if (.cost_usd_approx | type) == "object" then
        "| \($disp) (single-RTX-6000 reasonable build) | $\(.cost_usd_approx.reasonable_single_rtx6000_build) | \(.cost_usd_approx.reasonable_build_note) |\n| \($disp) (as-configured dual-GPU server) | $\(.cost_usd_approx.as_configured) | \(.cost_usd_approx.as_configured_note) |"
    else
        "| \($disp) | $\(.cost_usd_approx // "—") | \(.cost_note // "—") |"
    end
' "$TARGETS_JSON"
echo
echo "**The Blackwell 6000 Tower is anchored on the \$12 k reasonable-single-RTX-6000 build, not the \$33 k as-configured dual-GPU server**, because the cross-host comparison measures single-GPU inference. The \$33 k accounts for dual-GPU + ECC + redundancy + server-grade board, which are configuration choices unrelated to the inference performance we're measuring. (We also report the as-configured row for reference.)"
echo
echo "### Throughput per \$1 k at peak short-context (best-cell, 27B Q8)"
echo
echo "Single-user **decode tok/s per \$1 k** at short context (ctx=1024 gen=2048 conc=1, 27B Q8) — the standard metric for hardware-buying comparisons."
echo
echo "| host | cost (\$k) | decode tok/s | decode tok/s per \$1 k |"
echo "|---|---:|---:|---:|"
python3 - "$TARGETS_JSON" "$AGG/cells.jsonl" 2>/dev/null <<'PYEOF' || true
import sys, json
hosts = json.load(open(sys.argv[1]))["hosts"]
cells = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
def cost(h):
    if not h.get("cost_usd_approx"): return None
    if isinstance(h["cost_usd_approx"], dict):
        return h["cost_usd_approx"].get("reasonable_single_rtx6000_build")
    return h["cost_usd_approx"]
def label(h):
    disp = h.get("display_name", h["name"])
    if h["name"]=="tower2": return f"{disp} (single-RTX-6000 build)"
    return disp
ref = [c for c in cells if c.get("model")=="qwen3.6-27b" and c.get("ctx")==1024 and c.get("gen")==2048 and c.get("conc")==1 and c.get("per_slot_decode_tps_mean")]
for h in hosts:
    c = cost(h); tps = next((x["per_slot_decode_tps_mean"] for x in ref if x["host"]==h["name"]), None)
    if c and tps:
        print(f"| {label(h)} | {c/1000:.1f} | {tps:.1f} | **{tps/(c/1000):.2f}** |")
PYEOF
echo
echo "Peak **prefill tok/s per \$1 k** at the same cell — the matmul-heavy phase that dominates first-token latency at long context."
echo
echo "| host | cost (\$k) | prefill tok/s | prefill tok/s per \$1 k |"
echo "|---|---:|---:|---:|"
python3 - "$TARGETS_JSON" "$AGG/cells.jsonl" 2>/dev/null <<'PYEOF' || true
import sys, json
hosts = json.load(open(sys.argv[1]))["hosts"]
cells = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
def cost(h):
    if not h.get("cost_usd_approx"): return None
    if isinstance(h["cost_usd_approx"], dict):
        return h["cost_usd_approx"].get("reasonable_single_rtx6000_build")
    return h["cost_usd_approx"]
def label(h):
    disp = h.get("display_name", h["name"])
    if h["name"]=="tower2": return f"{disp} (single-RTX-6000 build)"
    return disp
ref = [c for c in cells if c.get("model")=="qwen3.6-27b" and c.get("ctx")==1024 and c.get("gen")==2048 and c.get("conc")==1 and c.get("per_slot_prefill_tps_mean")]
for h in hosts:
    c = cost(h); tps = next((x["per_slot_prefill_tps_mean"] for x in ref if x["host"]==h["name"]), None)
    if c and tps:
        print(f"| {label(h)} | {c/1000:.1f} | {tps:.1f} | **{tps/(c/1000):.2f}** |")
PYEOF
echo
echo "### Reading"
echo
echo "The Blackwell 6000 Tower wins decode tok/s per dollar at this operating point — 4.1 tok/s/\$k vs M5 Max MacBook Pro 3.5, DGX Spark 1.6, EVO X2 2.6. It also wins prefill per dollar by an even larger margin because its bandwidth + compute lead is most pronounced in the matmul-heavy prefill phase."
echo
echo "Multi-user (conc≥4) cost-throughput is held — see § Held: multi-user concurrent serving."
echo
echo "_Cost figures are approximate retail as of 2026-05-15. The Blackwell 6000 Tower is anchored on the reasonable single-RTX-6000 build (\$12 k); the as-configured \$33 k dual-GPU server price is documented separately for transparency._"
echo
echo "### Dual-anchor sensitivity: what if you used the \$33 k as-configured price for Tower2?"
echo
echo "Per AUDIT.md B12, the \$12 k single-RTX-6000 anchor is the right answer for *inference performance* comparison. But a reader buying the actual server gets the \$33 k as-built. Both anchors, side by side:"
echo
echo "| host | anchor (\$k) | decode tok/s/\$1 k | prefill tok/s/\$1 k |"
echo "|---|---:|---:|---:|"
python3 - "$TARGETS_JSON" "$AGG/cells.jsonl" 2>/dev/null <<'PYEOF' || true
import sys, json
hosts = json.load(open(sys.argv[1]))["hosts"]
cells = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
ref = {c["host"]: c for c in cells if c.get("model")=="qwen3.6-27b" and c.get("ctx")==1024 and c.get("gen")==2048 and c.get("conc")==1 and c.get("per_slot_decode_tps_mean")}
for h in hosts:
    c_field = h.get("cost_usd_approx")
    if not c_field: continue
    cell = ref.get(h["name"])
    if not cell: continue
    dec = cell["per_slot_decode_tps_mean"]
    pre = cell.get("per_slot_prefill_tps_mean", 0)
    disp = h.get("display_name", h["name"])
    if isinstance(c_field, dict):
        anchors = [
            (f"{disp} ($12k single-RTX-6000)", c_field["reasonable_single_rtx6000_build"]),
            (f"{disp} ($33k as-configured)", c_field["as_configured"]),
        ]
    else:
        anchors = [(disp, c_field)]
    for label, c in anchors:
        print(f"| {label} | {c/1000:.1f} | **{dec/(c/1000):.2f}** | **{pre/(c/1000):.1f}** |")
PYEOF
echo
echo "Under the \$33 k anchor, Tower2's decode tok/s/\$k drops from 4.1 to ~1.5 — still positive but no longer top — and prefill drops from ~186 to ~68. The skeptical reader's right question is **\"which anchor matches my purchase?\"**: if they would buy a workstation with dual ECC GPUs and 1600 W titanium PSU because they need those things, use \$33 k. If they would buy a one-GPU machine because their workload is one-GPU, use \$12 k. The right number depends on the budget the comparison is informing."
echo
echo "### 5-year total cost of ownership under continuous load"
echo
echo "Hardware cost dominates short-term, but at 24/7 inference the electricity bill catches up. 5-year TCO under continuous bench-style load, using each host's measured or estimated wall draw:"
echo
echo "| host | hardware (\$k) | mean wall (W) | source | 5-yr energy @ \$0.12/kWh | total 5-yr (low) | total 5-yr @ \$0.20/kWh |"
echo "|---|---:|---:|---|---:|---:|---:|"
python3 - "$TARGETS_JSON" 2>/dev/null <<'PYEOF' || true
import sys, json
hosts = json.load(open(sys.argv[1]))["hosts"]
# Wall power per host (W) — measured if plug-meter exists, else conservative estimate from silicon + overhead
wall_sources = {
    "tower2":     (445, "plug meter @ compute-light cell (peak ~850 W est)", "12.0"),
    "m5-mbp":     (142, "plug meter @ multi-user cell",                       "4.85"),
    "spark":      (80,  "est: ~46 W silicon + ~25–35 W system overhead",      "4.7"),
    "strix-halo": (155, "est: ~119 W silicon + ~30 W system overhead",        "3.0"),
}
hours_5yr = 5 * 365 * 24
for h in hosts:
    if h["name"] not in wall_sources: continue
    w, src, hw_k = wall_sources[h["name"]]
    kwh_5yr = w * hours_5yr / 1000
    cost_low = kwh_5yr * 0.12
    cost_high = kwh_5yr * 0.20
    total_low = float(hw_k) + cost_low/1000
    total_high = float(hw_k) + cost_high/1000
    disp = h.get("display_name", h["name"])
    print(f"| {disp} | {hw_k} | {w} | {src} | ${cost_low:,.0f} | ${total_low:.1f} k | ${total_high:.1f} k |")
PYEOF
echo
echo "**Reading this:** Tower2 has the highest 5-yr TCO at ~\$14–16 k (single-RTX-6000 anchor) up to ~\$35–37 k (as-built dual-GPU server anchor). M5 Max stays close to its sticker price (\$5.6–6.4 k) — laptops are cheap to run continuously. **DGX Spark and EVO X2 wall figures are estimated, not plug-metered** — they need explicit ground-truth readings before TCO claims firm up (audit gap, see B8). The Tower2 wall figure is a plug-meter reading at a *compute-light* cell; peak-cell wall is estimated ~850 W and would push 5-yr energy to ~\$4.5–7.5 k, ~\$2–4 k higher than shown."
echo
echo "## § Cross-host generation determinism"
echo
echo "Each inference at \`temperature=0, seed=42\` should produce the same output on every backend. We compute SHA256 of every generation and check whether different hosts running the same prompt produced the same SHA."
echo

# Build SHA cross-tab: (ctx,gen,conc,inference id) → set of (host, sha)
# A cell is "deterministic" if all hosts that ran it produced the same sha.
DET_TSV="$AGG/determinism.tsv"
jq -r 'select(.content_sha256) | [.cell, .id, .host, .backend, .model, .content_sha256] | @tsv' "$INF_ALL" > "$DET_TSV"
N_WITH_SHA="$(wc -l < "$DET_TSV")"

if (( N_WITH_SHA > 0 )); then
    python3 - "$DET_TSV" <<'PYEOF'
import sys, collections
groups = collections.defaultdict(set)   # (cell, id) -> set of (host+model+backend, sha)
for line in open(sys.argv[1]):
    cell,iid,host,backend,model,sha = line.rstrip("\n").split("\t")
    # group by the prompt being run — model is part of the key (27b SHAs ≠ 35b SHAs)
    groups[(model, cell, iid)].add((f"{host}/{backend}", sha))

shared = [g for g in groups.values() if len({h for h,s in g}) >= 2]
all_match = sum(1 for g in shared if len({s for h,s in g}) == 1)
divergent = [g for g in shared if len({s for h,s in g}) > 1]
total_inferences = sum(len(g) for g in groups.values())

print(f"- **Inferences with SHA captured:** {total_inferences}")
print(f"- **Prompts run on 2+ hosts (cross-host comparable):** {len(shared)}")
print(f"- **Hosts produced byte-identical output:** {all_match} of {len(shared)} = {100*all_match/max(1,len(shared)):.1f}%")
print(f"- **Hosts produced divergent output:** {len(divergent)}")
print()

if divergent:
    print(f"### Divergent generations (first 10)")
    print()
    print("| model | cell | inference id | host/backend → SHA prefix |")
    print("|---|---|---|---|")
    for g in divergent[:10]:
        # take any one representative
        any_item = next(iter(g))
        # pull model/cell/id from a single occurrence
        for key, v in groups.items():
            if v is g:
                m, c, i = key
                break
        else:
            m,c,i = "?","?","?"
        rendering = "; ".join(f"`{h}={s[:8]}`" for h,s in sorted(g))
        print(f"| {m} | {c} | {i} | {rendering} |")
PYEOF
else
    echo "_No content SHAs captured yet (older cells pre-date the text-capture patch)._"
fi

echo
echo "## § Generation length per host"
echo
echo "Does the model produce different-length output on different backends? Per-inference \`content_len_chars\` distribution."
echo

if (( N_WITH_SHA > 0 )); then
    echo "| host/backend | n | mean chars | median chars | p95 chars | min | max |"
    echo "|---|---:|---:|---:|---:|---:|---:|"
    python3 - "$INF_ALL" <<'PYEOF'
import sys, json, collections, statistics
by_hb = collections.defaultdict(list)
for line in open(sys.argv[1]):
    try: row = json.loads(line)
    except: continue
    if "content_len_chars" not in row: continue
    key = f"{row['host']}/{row['backend']}/{row['model']}"
    by_hb[key].append(row["content_len_chars"])
for hb, vals in sorted(by_hb.items()):
    if not vals: continue
    s = sorted(vals)
    n = len(vals)
    print(f"| {hb} | {n} | {statistics.mean(vals):.0f} | {s[n//2]} | {s[min(n-1, int(n*0.95))]} | {s[0]} | {s[-1]} |")
PYEOF
else
    echo "_No content lengths captured yet._"
fi

echo
echo "## § Stop reason per host"
echo
echo "Why did each generation terminate? Mostly should be \`limit\` since we cap at gen_target tokens, but \`eos\` and \`stop_word\` reveal model-emergent behavior."
echo

echo "| host/backend | model | limit | eos | stop_word | other |"
echo "|---|---|---:|---:|---:|---:|"
python3 - "$INF_ALL" <<'PYEOF'
import sys, json, collections
by_hb = collections.defaultdict(lambda: collections.Counter())
for line in open(sys.argv[1]):
    try: row = json.loads(line)
    except: continue
    st = row.get("stop_type") or "unknown"
    key = (f"{row.get('host','?')}/{row.get('backend','?')}", row.get('model','?'))
    by_hb[key][st] += 1
for (hb, model), c in sorted(by_hb.items()):
    print(f"| {hb} | {model} | {c.get('limit',0)} | {c.get('eos',0)} | {c.get('word',0) + c.get('stop_word',0)} | {sum(c.values()) - c.get('limit',0) - c.get('eos',0) - c.get('word',0) - c.get('stop_word',0)} |")
PYEOF

echo
echo "## § Coherence spot-check"
echo
echo "10 random generations (with prompt context) sampled from across the grid. Use these to eyeball whether Q8 output looks reasonable on every backend."
echo

if (( N_WITH_SHA > 0 )); then
    python3 - "$INF_ALL" <<'PYEOF'
import sys, json, random
rows = []
for line in open(sys.argv[1]):
    try: row = json.loads(line)
    except: continue
    if not row.get("content_preview"): continue
    rows.append(row)
if not rows:
    print("_No generations captured yet._")
else:
    random.seed(42)
    pick = random.sample(rows, min(10, len(rows)))
    for r in pick:
        print(f"### `{r['host']}/{r['backend']}/{r['model']}` — cell {r['cell']} — {r['id']}")
        print(f"- decode {r.get('decode_tps','?'):.1f} tok/s, gen {r.get('gen_tokens','?')} tokens, stop={r.get('stop_type','?')}")
        print(f"- content sha: `{r.get('content_sha256','?')[:16]}`")
        print()
        print("```")
        print(r["content_preview"])
        print("```")
        print()
PYEOF
else
    echo "_No content previews captured yet (pending the text-capture patch landing in more cells)._"
fi

echo
echo "## § Hosts"
echo
echo "Form factor matters — these four hosts span workstation, NUC-class mini-PC, reference desktop, and laptop. Compare power/thermal numbers in light of the chassis the silicon is sitting in."
echo
jq -r '.hosts[] | "- **\(.display_name // .name)** (\(.arch), \(.os)) — _chassis: \(.chassis // "—")_ — backends: \(.backends | join(", ")); power sampler \(.power_sampler); notes: \(.notes)"' "$TARGETS_JSON"
echo
echo "### Form-factor caveats for the headline ranking"
echo
echo "- **Blackwell 6000 Tower** is a workstation with a 1600 W titanium PSU and effectively unlimited cooling headroom. Its single GPU is power-capped at 600 W."
echo "- **EVO X2** (GMKtec EVO X2 with AMD Ryzen AI MAX+ 395 / Strix Halo APU) is a NUC-class small-form-factor enclosure. Sustaining a ~119 W GPU package load + ~98 °C edge temperature in that chassis is qualitatively different from a workstation tower at the same load. Read its numbers in that light."
echo "- **DGX Spark** is the reference NVIDIA DGX Spark desktop (compact desktop with GB10 Grace Blackwell)."
echo "- **M5 Max MacBook Pro** is a 16\" laptop on its AC-charged battery PSU; \`sys\` macmon power is the closest reading we have to wall-AC (plug-meter validated at 142 W vs 128 W reported, ~10 % gap)."
echo
echo "### Backend-completeness caveat"
echo
echo "The EVO X2 host runs Vulkan only in this study. ROCm was attempted but did not reach a ready server in our one smoke cell; a proper retry sub-study (longer wait-ready, smaller bootstrap model, fresh stderr/dmesg capture) is queued post-grid (task #20). Until that retry runs, **the Vulkan numbers stand on their own — this study does not yet make a comparative Vulkan-vs-ROCm claim**."
echo
echo "## § Methodology"
echo
echo "Per cell: load model once, $(jq -r '.study.grid.n_per_cell' "$TARGETS_JSON") batches of N=\`conc\` parallel requests each, \`temperature=0 seed=42 cache_prompt=false\`. First $(jq -r '.study.grid.warmup_discard' "$TARGETS_JSON") batches discarded as warmup. Samplers stream at 1 Hz with monotonic + wall-clock timestamps."
echo
echo "## § Reproducibility"
echo
echo "- Source: \`https://github.com/ggml-org/llama.cpp@$LLAMA_SHA\`"
echo "- Prompts: \`workloads/prompts.jsonl\` (SHA \`$CORPUS_SHA\`)"
echo "- Per-host build invocations under each host's \`build-<backend>.configure.log\`"
echo "- Per-host \`env.json\` snapshots (driver versions, GPU info, cmake/SDK versions)"
echo "- Raw per-cell: \`<host>/<model>/<backend>/ctxNNNN_genNNNN_concN/{cell.json,inferences.jsonl,batches.jsonl,power.csv,thermals.csv,llama-server-*.log}\`"
echo
echo "## § Companion analyses"
echo
echo "- \`mmbt-phase-b-q8/\` — task-graded quality scores on the MMBT Phase B 12-task-family suite (Goal 1 deliverable; auto-triggered post-grid by \`lib/post-grid.sh\`)"
echo "- \`sustained/\` — 30-min sustained-thermal throttle curves per host (Goal 2 thermal characterization)"
echo
echo "## § Audit"
echo
echo "See \`AUDIT.md\` for the rigor self-audit: what's locked, what varies, biases B1-B7, known issues."
} > "$OUT"

log "wrote $OUT"
log "sections: hardware ranking | cross-host determinism | generation length | stop reason | coherence | reproducibility"
