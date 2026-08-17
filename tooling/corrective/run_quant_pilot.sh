#!/usr/bin/env bash
# Quant crossover pilot runner — bounded Tower2 maintenance window
# (PREREGISTRATION.md section 7; arm config: configs/quant-pilot.json).
#
# Grid: both models x {UD-Q4_K_XL, Q8_0} at the official-nothink sampler,
# seeds 101/211, 12 families = 96 cells, on Tower2's two RTX PRO 6000s with
# the GPU<->model assignment CROSSED between the two seeds (host_plan).
#
# Per seed the window runs two co-residency waves (config serving.waves):
#   wave 0: both models at UD-Q4_K_XL (one container per GPU)
#   wave 1: both models at Q8_0      (one container per GPU)
# Containers are torn down between waves (same GPU serves both quants of one
# model within a seed). Within a wave, task order is family-major with
# alternating model start — the SAME parity rule as run_crossover.sh: the
# model launched FIRST is the q38-side container when (seed_index +
# family_index) is even, q36-side when odd; the second launches
# BENCH_QUANTPILOT_STAGGER_SECS later (default 30) and both run concurrently.
#
# WINDOW-OPEN PREFLIGHT (fail-closed; evidence -> logs/corrective/):
#   1. hostname must be the pinned Tower2 identity;
#   2. DSV4 DRAIN WINDOW MUST BE OPEN: refuses while any drain.forbidden
#      container (deepseek-v4-flash-0731) is running. This script NEVER
#      stops DSV4 itself — the drain is orchestrator-owned;
#   3. both pinned GPU UUIDs present, power cap at power_cap_w on each, and
#      GPU memory drained (< serving.drained_gpu_max_mem_mib MiB);
#   4. pinned llama.cpp image present: Id + revision label must match;
#   5. all four pilot loopback ports free;
#   6. every model GGUF present with pinned byte size AND full sha256
#      (Qwen3.6 Q8_0 is not staged by this script — see
#      tooling/corrective/download-qwen36-q8_0.sh);
#   7. expected grid arithmetic (families x seeds x models = 96 cells).
#
# Serving: two llama-server containers per wave from the pinned image digest,
# llama-server argv BYTE-IDENTICAL to the historical lanes
# (ensure-q38-tower1-only.sh / ensure-q36-tower3-only.sh) except
# --model/--alias. Docker-level deltas (forced by the two-GPU topology) are
# enumerated in the config under serving._docker_deltas_vs_historical_lanes.
# The served binary is verified against the pinned llama-server sha256 after
# every container start. A serving manifest is generated per seed and passed
# to every cell via BENCH_SERVING_MANIFEST so each receipt carries lane
# provenance (GPU uuid, container, model sha, image digest).
#
# Cells run through cell_supervisor.py — live loop terminator, 3 h wall
# ceiling, delivery validation, quarantine + same-seed rerun ledger
# (logs/corrective/rerun_ledger.jsonl) — exactly like the main campaign.
# An exhausted infra cell aborts the window: stop and report, never improvise.
#
# WINDOW CLOSE: containers stopped + removed (window ledger:
# logs/corrective/quant-pilot/window_ledger.jsonl), evidence manifest built +
# fixed-N checked, and the DSV4 restore reminder printed. DSV4 restore +
# baseline verification is ORCHESTRATOR-OWNED; this script never restarts it.
#
# Usage:
#   bash tooling/corrective/run_quant_pilot.sh [--config tooling/corrective/configs/quant-pilot.json]
#        [--seeds 101,211] [--dry-run] [--max-infra-retries 3]
#
# --dry-run: read-only. Runs the preflight in report-only mode (file
# existence + byte size instead of full sha256), prints the full 96-cell
# plan and the exact docker argv per lane, and starts NOTHING.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLING="$(cd "$HERE/.." && pwd)"
REPO_ROOT="$(cd "$TOOLING/.." && pwd)"
CORR_LOGS="$REPO_ROOT/logs/corrective"
PILOT_LOGS="$CORR_LOGS/quant-pilot"
WINDOW_LEDGER="$PILOT_LOGS/window_ledger.jsonl"
STAGGER_SECS="${BENCH_QUANTPILOT_STAGGER_SECS:-30}"

CONFIG="$HERE/configs/quant-pilot.json"
SEEDS_CSV=""
DRY_RUN=0
MAX_INFRA_RETRIES=3

while [ $# -gt 0 ]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --seeds) SEEDS_CSV="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --max-infra-retries) MAX_INFRA_RETRIES="$2"; shift 2 ;;
    -h|--help) grep "^#" "$0" | sed "s/^# \{0,1\}//"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -f "$CONFIG" ] || { echo "ERROR: config not found: $CONFIG" >&2; exit 2; }

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

cfg_get() { python3 -c '
import json, sys
cfg = json.load(open(sys.argv[1]))
cur = cfg
for k in sys.argv[2].split("."):
    cur = cur[int(k)] if isinstance(cur, list) else cur[k]
if isinstance(cur, (list, tuple)):
    print(" ".join(str(x) for x in cur))
else:
    print(cur)
' "$CONFIG" "$1"; }

ARM="$(cfg_get arm)"
FAMILIES=($(cfg_get families))
ALL_SEEDS=($(cfg_get seeds))
POWER_CAP_W="$(cfg_get power_cap_w)"
FORBIDDEN=($(cfg_get drain.forbidden_containers))
EXPECTED_HOSTNAME="$(cfg_get serving.expected_hostname)"
MODEL_STORE="$(cfg_get serving.model_store)"
EXPECTED_CTX="$(cfg_get serving.expected_ctx)"
EXPECTED_SLOTS="$(cfg_get serving.expected_slots)"
DRAINED_MAX_MIB="$(cfg_get serving.drained_gpu_max_mem_mib)"
READY_ATTEMPTS="$(cfg_get serving.readiness_attempts)"
READY_INTERVAL="$(cfg_get serving.readiness_interval_secs)"
IMAGE_REF="$(cfg_get image_reference)"
IMAGE_ID="$(cfg_get image_id)"
LLAMA_COMMIT="$(cfg_get llama_cpp_commit)"
LLAMA_BINARY_SHA256="$(cfg_get llama_server_sha256)"
N_WAVES="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["serving"]["waves"]))' "$CONFIG")"
MODEL_KEYS=($(python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1]))["models"].keys()))' "$CONFIG"))

if [ -n "$SEEDS_CSV" ]; then
  SEEDS=(${SEEDS_CSV//,/ })
  for s in "${SEEDS[@]}"; do
    ok=0; for a in "${ALL_SEEDS[@]}"; do [ "$s" = "$a" ] && ok=1; done
    [ "$ok" = "1" ] || die "seed $s is not in arm $ARM (fixed-N design: no extra seeds)"
  done
else
  SEEDS=("${ALL_SEEDS[@]}")
fi

phase_of_seed() { python3 -c '
import json, sys
cfg = json.load(open(sys.argv[1])); seed = int(sys.argv[2])
for phase, plan in cfg["host_plan"].items():
    if seed in plan["seeds"]:
        print(phase); raise SystemExit(0)
raise SystemExit(1)
' "$CONFIG" "$1"; }

plan_field() { cfg_get "host_plan.$1.$2.$3"; }      # phase model_key field
model_field() { cfg_get "models.$1.$2"; }           # model_key field
wave_field() { cfg_get "serving.waves.$1.$2"; }     # wave_index field

ledger() { # one JSON object per line, single-writer append
  mkdir -p "$PILOT_LOGS"
  printf '%s\n' "$1" >> "$WINDOW_LEDGER"
}

# ---------- DSV4 restore reminder (window close) --------------------------

DSV4_ID="(unknown)"
DSV4_IMAGE="(unknown)"
DSV4_EXISTS=0

capture_dsv4_identity() {
  local c="${FORBIDDEN[0]}"
  if docker container inspect "$c" >/dev/null 2>&1; then
    DSV4_EXISTS=1
    DSV4_ID="$(docker container inspect "$c" --format '{{.Id}}')"
    DSV4_IMAGE="$(docker container inspect "$c" --format '{{.Config.Image}}')"
  fi
}

print_restore_reminder() {
  cat <<EOF

==================== QUANT-PILOT WINDOW CLOSE ====================
All quant-pilot containers this run started have been stopped and
removed (window ledger: $WINDOW_LEDGER).

DSV4 RESTORE IS ORCHESTRATOR-OWNED (PREREGISTRATION.md section 7):
  1. Restart production DSV4: container ${FORBIDDEN[0]}
     (id at window open: $DSV4_ID, image: $DSV4_IMAGE).
  2. Verify restored serving against the baseline captured at window
     open BEFORE declaring the maintenance window closed.
This runner never starts or stops DSV4 itself.
==================================================================
EOF
}

# ---------- container lifecycle ------------------------------------------

ACTIVE_CONTAINERS=""
WINDOW_OPENED=0

emergency_teardown() {
  local rc=$?
  if [ -n "$ACTIVE_CONTAINERS" ]; then
    log "abnormal exit (rc=$rc): tearing down active pilot containers: $ACTIVE_CONTAINERS"
    local c
    for c in $ACTIVE_CONTAINERS; do
      docker stop -t 60 "$c" >/dev/null 2>&1 || true
      docker rm "$c" >/dev/null 2>&1 || true
      ledger "{\"t\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"action\":\"emergency-teardown\",\"container\":\"$c\",\"rc\":$rc}"
    done
    ACTIVE_CONTAINERS=""
  fi
  if [ "$WINDOW_OPENED" = "1" ]; then
    print_restore_reminder
  fi
}
trap emergency_teardown EXIT

endpoint_matches() { # port alias
  curl -fsS --max-time 5 "http://127.0.0.1:${1}/v1/models" 2>/dev/null |
    python3 -c 'import json,sys
expected,ctx=sys.argv[1],int(sys.argv[2])
payload=json.load(sys.stdin)
items=payload.get("data", []) + payload.get("models", [])
ids=[]
contexts=[]
for item in items:
    if not isinstance(item, dict):
        continue
    ids.extend(str(item.get(key, "")) for key in ("id", "name", "model"))
    meta=item.get("meta") or {}
    if meta.get("n_ctx") is not None:
        contexts.append(int(meta["n_ctx"]))
raise SystemExit(0 if expected in ids and ctx in contexts else 1)' \
      "$2" "$EXPECTED_CTX"
}

start_container() { # model_key seed phase
  local mk="$1" seed="$2" phase="$3"
  local alias model_rel model_sha profile container port gpu_uuid used_mib
  alias="$(model_field "$mk" alias)"
  model_rel="$(model_field "$mk" model_rel)"
  model_sha="$(model_field "$mk" model_sha256)"
  profile="$(model_field "$mk" server_profile)"
  container="$(model_field "$mk" container_base)-s${seed}"
  port="$(plan_field "$phase" "$mk" port)"
  gpu_uuid="$(plan_field "$phase" "$mk" gpu_uuid)"

  # fail-closed: never adopt or replace an existing container of this name
  if docker container inspect "$container" >/dev/null 2>&1; then
    die "container $container already exists — inspect + remove it manually (this runner never adopts or auto-deletes containers)"
  fi

  # the target GPU must be drained right now
  used_mib="$(nvidia-smi --id="$gpu_uuid" --query-gpu=memory.used --format=csv,noheader,nounits | head -1)"
  awk -v value="$used_mib" -v cap="$DRAINED_MAX_MIB" 'BEGIN { exit !(value+0 < cap+0) }' ||
    die "GPU $gpu_uuid is not drained (${used_mib} MiB used, want < ${DRAINED_MAX_MIB}); refusing to start $container"

  log "starting $container (model=$alias gpu=$gpu_uuid port=$port)"
  # llama-server argv below is byte-identical to the historical lanes
  # (ensure-q38-tower1-only.sh / ensure-q36-tower3-only.sh) except
  # --model/--alias. Docker-level deltas are documented in the config.
  docker run -d --name "$container" --restart=no --gpus "device=${gpu_uuid}" --shm-size 8g \
    --label mmbt.campaign=qwen-corrective-quant-pilot \
    --label "mmbt.model-sha256=$model_sha" \
    --label "mmbt.server-profile=$profile" \
    --label "mmbt.quantpilot.seed=$seed" \
    --label "mmbt.quantpilot.model-key=$mk" \
    --label "mmbt.quantpilot.gpu-uuid=$gpu_uuid" \
    --read-only --tmpfs /tmp:rw,nosuid,size=1g --tmpfs /root/.nv:rw,nosuid,size=2g \
    -v "${MODEL_STORE}:/models:ro" \
    -p "127.0.0.1:${port}:8080" \
    "$IMAGE_REF" \
    --model "/models/${model_rel}" \
    --alias "$alias" \
    --host 0.0.0.0 --port 8080 \
    --n-gpu-layers 999 \
    --ctx-size "$EXPECTED_CTX" \
    --batch-size 2048 --threads 4 --parallel "$EXPECTED_SLOTS" \
    --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 \
    --jinja --reasoning-format none --no-context-shift --metrics >/dev/null

  ACTIVE_CONTAINERS="$ACTIVE_CONTAINERS $container"
  local cid
  cid="$(docker container inspect "$container" --format '{{.Id}}')"
  ledger "{\"t\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"action\":\"start\",\"container\":\"$container\",\"id\":\"$cid\",\"model_key\":\"$mk\",\"seed\":$seed,\"gpu_uuid\":\"$gpu_uuid\",\"port\":$port,\"image\":\"$IMAGE_REF\"}"

  # pinned-binary proof for THIS serving container
  local binary_sha
  binary_sha="$(docker exec "$container" sha256sum /app/llama-server | awk '{print $1}')"
  [ "$binary_sha" = "$LLAMA_BINARY_SHA256" ] ||
    die "$container serves an unexpected llama-server binary ($binary_sha, want $LLAMA_BINARY_SHA256)"

  local i
  for i in $(seq 1 "$READY_ATTEMPTS"); do
    if endpoint_matches "$port" "$alias"; then
      log "$container ready on 127.0.0.1:$port ($alias, ctx $EXPECTED_CTX)"
      return 0
    fi
    if ! docker inspect "$container" --format '{{.State.Running}}' 2>/dev/null | grep -Fxq true; then
      docker logs --tail 80 "$container" >&2 || true
      die "$container exited before readiness"
    fi
    sleep "$READY_INTERVAL"
  done
  docker logs --tail 80 "$container" >&2 || true
  die "$container failed readiness deadline"
}

stop_container() { # container
  local c="$1" cid
  cid="$(docker container inspect "$c" --format '{{.Id}}' 2>/dev/null || echo unknown)"
  docker stop -t 60 "$c" >/dev/null
  docker rm "$c" >/dev/null
  ACTIVE_CONTAINERS="$(printf '%s' "$ACTIVE_CONTAINERS" | sed "s/ $c//")"
  ledger "{\"t\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"action\":\"stop+rm\",\"container\":\"$c\",\"id\":\"$cid\"}"
}

# ---------- serving manifest (per seed) ----------------------------------

write_serving_manifest() { # seed phase -> prints path
  local seed="$1" phase="$2"
  local out="$PILOT_LOGS/serving-manifest-quant-pilot-s${seed}.json"
  mkdir -p "$PILOT_LOGS"
  python3 - "$CONFIG" "$seed" "$phase" "$out" "$REPO_ROOT" <<'PY'
import datetime, hashlib, json, subprocess, sys

cfg_path, seed, phase, out, repo_root = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
cfg = json.load(open(cfg_path))
plan = cfg["host_plan"][phase]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run(*argv):
    return subprocess.run(argv, capture_output=True, text=True).stdout.strip()

image_ref = cfg["image_reference"]
live_image_id = run("docker", "image", "inspect", image_ref, "--format", "{{.Id}}")
live_revision = run("docker", "image", "inspect", image_ref, "--format",
                    '{{ index .Config.Labels "org.opencontainers.image.revision" }}')
gpu_rows = {}
for line in run("nvidia-smi", "--query-gpu=index,uuid,name,power.limit,memory.total",
                "--format=csv,noheader,nounits").splitlines():
    idx, uuid, name, cap, mem = [x.strip() for x in line.split(",")]
    gpu_rows[uuid] = {"index": int(idx), "name": name,
                      "power_limit_w": float(cap), "memory_total_mib": int(mem)}

lanes = []
for lane_index, (mk, m) in enumerate(sorted(cfg["models"].items())):
    lp = plan[mk]
    uuid = lp["gpu_uuid"]
    live = gpu_rows.get(uuid, {})
    lanes.append({
        "lane_index": lane_index,
        "coordinator_port": lp["port"],
        "inference_host": lp["tower"],
        "container": f"{m['container_base']}-s{seed}",
        "model_key": mk,
        "model_alias": m["alias"],
        "quant": m["quant"],
        "model_path": f"{cfg['serving']['model_store']}/{m['model_rel']}",
        "model_sha256": m["model_sha256"],
        "model_byte_size": m["model_size"],
        "server_profile": m["server_profile"],
        "gpu_index": lp["gpu_index"],
        "gpu_uuid": uuid,
        "gpu_name": live.get("name") or cfg["serving"]["gpus"][str(lp["gpu_index"])]["name"],
        "gpu_power_limit_w": int(live.get("power_limit_w", cfg["power_cap_w"])),
        "gpu_memory_mib": live.get("memory_total_mib"),
    })

manifest = {
    "schema_version": 2,
    "status": "started",
    "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "campaign": {
        "name": "qwen-corrective-quant-pilot",
        "arm": cfg["arm"],
        "protocol_ref": cfg["protocol_ref"],
        "seed": seed,
        "phase": phase,
        "config": cfg_path,
        "config_sha256": sha256_file(cfg_path),
        "repo_git_sha": run("git", "-C", repo_root, "rev-parse", "HEAD") or None,
    },
    "runtime": {
        "engine": "llama.cpp",
        "image_reference": image_ref,
        "image_id": live_image_id,
        "image_id_pinned": cfg["image_id"],
        "llama_cpp_commit": live_revision,
        "llama_cpp_commit_pinned": cfg["llama_cpp_commit"],
        "llama_server_sha256_pinned": cfg["llama_server_sha256"],
    },
    "topology": {
        "kind": "two local single-GPU llama.cpp replicas on Tower2 loopback (quant pilot, GPU<->model crossed between seeds)",
        "coordinator_host": run("hostname"),
        "lane_ports": sorted(l["coordinator_port"] for l in lanes),
        "slots_per_replica": cfg["serving"]["expected_slots"],
        "context_tokens_per_slot": cfg["serving"]["expected_ctx"],
        "lanes": lanes,
    },
}
assert live_image_id == cfg["image_id"], f"image id drifted: {live_image_id}"
assert live_revision == cfg["llama_cpp_commit"], f"image revision drifted: {live_revision}"
with open(out, "w") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)
    f.write("\n")
print(out)
PY
}

# ---------- preflight ----------------------------------------------------

preflight() {
  local fail=0
  local record="$CORR_LOGS/preflight-$ARM-$(date -u +%Y%m%dT%H%M%SZ).json"
  mkdir -p "$CORR_LOGS"
  local results=()
  local ok

  # 1. host identity
  ok=1
  local host; host="$(hostname)"
  [ "$host" = "$EXPECTED_HOSTNAME" ] || { ok=0; fail=1; }
  results+=("{\"check\":\"hostname\",\"want\":\"$EXPECTED_HOSTNAME\",\"got\":\"$host\",\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
  log "preflight hostname: $host (want $EXPECTED_HOSTNAME): $( [ $ok = 1 ] && echo PASS || echo FAIL )"

  # 2. DSV4 drain window open (refuse while forbidden containers run)
  ok=1
  local names c
  names="$(docker ps --format '{{.Names}}')"
  for c in "${FORBIDDEN[@]}"; do
    if grep -Fxq "$c" <<< "$names"; then ok=0; fi
  done
  [ "$ok" = "1" ] || fail=1
  capture_dsv4_identity
  results+=("{\"check\":\"dsv4_drain_window\",\"forbidden\":\"${FORBIDDEN[*]}\",\"running\":\"${names//$'\n'/,}\",\"dsv4_container_id\":\"$DSV4_ID\",\"dsv4_image\":\"$DSV4_IMAGE\",\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
  log "preflight DSV4 drain window: $( [ $ok = 1 ] && echo "PASS (no forbidden container running)" || echo "FAIL (${FORBIDDEN[*]} still serving — drain is orchestrator-owned, this runner will NOT stop it)" )"

  # 3. GPUs: pinned UUIDs, power cap, drained memory
  local gpu_csv
  gpu_csv="$(nvidia-smi --query-gpu=uuid,power.limit,memory.used --format=csv,noheader,nounits)"
  local mk phase uuid
  for uuid in $(python3 -c 'import json,sys
cfg=json.load(open(sys.argv[1]))
print(" ".join(sorted({g["uuid"] for g in cfg["serving"]["gpus"].values()})))' "$CONFIG"); do
    ok=1
    local row cap used
    row="$(grep -F "$uuid" <<< "$gpu_csv" || true)"
    if [ -z "$row" ]; then
      ok=0
    else
      cap="$(cut -d, -f2 <<< "$row" | tr -d ' ')"
      used="$(cut -d, -f3 <<< "$row" | tr -d ' ')"
      awk -v c="$cap" -v want="$POWER_CAP_W" 'BEGIN { exit (c+0 == want+0) ? 0 : 1 }' || ok=0
      if [ "$DRY_RUN" = "0" ]; then
        awk -v u="$used" -v m="$DRAINED_MAX_MIB" 'BEGIN { exit (u+0 < m+0) ? 0 : 1 }' || ok=0
      fi
    fi
    [ "$ok" = "1" ] || fail=1
    results+=("{\"check\":\"gpu\",\"uuid\":\"$uuid\",\"want_cap_w\":$POWER_CAP_W,\"row\":\"${row:-MISSING}\",\"drained_max_mib\":$DRAINED_MAX_MIB,\"mem_checked\":$( [ "$DRY_RUN" = "0" ] && echo true || echo false ),\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
    log "preflight GPU $uuid: $( [ $ok = 1 ] && echo PASS || echo FAIL ) (${row:-MISSING})"
  done

  # 4. pinned image identity
  ok=1
  local live_id live_rev
  live_id="$(docker image inspect "$IMAGE_REF" --format '{{.Id}}' 2>/dev/null || echo MISSING)"
  live_rev="$(docker image inspect "$IMAGE_REF" --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' 2>/dev/null || echo MISSING)"
  [ "$live_id" = "$IMAGE_ID" ] || ok=0
  [ "$live_rev" = "$LLAMA_COMMIT" ] || ok=0
  [ "$ok" = "1" ] || fail=1
  results+=("{\"check\":\"image\",\"ref\":\"$IMAGE_REF\",\"want_id\":\"$IMAGE_ID\",\"got_id\":\"$live_id\",\"want_revision\":\"$LLAMA_COMMIT\",\"got_revision\":\"$live_rev\",\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
  log "preflight image: $( [ $ok = 1 ] && echo PASS || echo FAIL ) (id $live_id)"

  # 5. pilot ports free
  local port
  for port in $(python3 -c 'import json,sys
cfg=json.load(open(sys.argv[1]))
ports=set()
for plan in cfg["host_plan"].values():
    for k, v in plan.items():
        if isinstance(v, dict) and "port" in v:
            ports.add(v["port"])
print(" ".join(str(p) for p in sorted(ports)))' "$CONFIG"); do
    ok=1
    if ss -tln 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]${port}\$"; then ok=0; fi
    [ "$ok" = "1" ] || fail=1
    results+=("{\"check\":\"port_free\",\"port\":$port,\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
    log "preflight port $port free: $( [ $ok = 1 ] && echo PASS || echo FAIL )"
  done

  # 6. model artifacts (existence + size always; full sha256 in real mode)
  for mk in "${MODEL_KEYS[@]}"; do
    ok=1
    local rel want_size want_sha path got_size got_sha="(skipped)"
    rel="$(model_field "$mk" model_rel)"
    want_size="$(model_field "$mk" model_size)"
    want_sha="$(model_field "$mk" model_sha256)"
    path="$MODEL_STORE/$rel"
    if [ ! -f "$path" ]; then
      ok=0; got_size=MISSING
      if [ "$mk" = "q36_q8" ]; then
        log "preflight model $mk: $path is MISSING — stage it with tooling/corrective/download-qwen36-q8_0.sh before the window"
      fi
    else
      got_size="$(stat -c %s "$path")"
      [ "$got_size" = "$want_size" ] || ok=0
      if [ "$DRY_RUN" = "0" ] && [ "$ok" = "1" ]; then
        log "preflight model $mk: hashing $path ($got_size bytes)..."
        got_sha="$(sha256sum "$path" | awk '{print $1}')"
        [ "$got_sha" = "$want_sha" ] || ok=0
      fi
    fi
    [ "$ok" = "1" ] || fail=1
    results+=("{\"check\":\"model\",\"model_key\":\"$mk\",\"path\":\"$path\",\"want_size\":$want_size,\"got_size\":\"$got_size\",\"want_sha256\":\"$want_sha\",\"got_sha256\":\"$got_sha\",\"sha_checked\":$( [ "$DRY_RUN" = "0" ] && echo true || echo false ),\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
    log "preflight model $mk: $( [ $ok = 1 ] && echo PASS || echo FAIL ) ($path)"
  done

  # 7. fixed-N grid arithmetic
  ok=1
  local n_cells
  n_cells=$(( ${#FAMILIES[@]} * ${#ALL_SEEDS[@]} * ${#MODEL_KEYS[@]} ))
  [ "$n_cells" = "96" ] || { ok=0; fail=1; }
  results+=("{\"check\":\"grid\",\"families\":${#FAMILIES[@]},\"seeds\":${#ALL_SEEDS[@]},\"models\":${#MODEL_KEYS[@]},\"cells\":$n_cells,\"want\":96,\"pass\":$( [ $ok = 1 ] && echo true || echo false )}")
  log "preflight grid: ${#FAMILIES[@]} families x ${#ALL_SEEDS[@]} seeds x ${#MODEL_KEYS[@]} models = $n_cells cells (want 96): $( [ $ok = 1 ] && echo PASS || echo FAIL )"

  {
    echo "{\"arm\":\"$ARM\",\"t\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"dry_run\":$( [ "$DRY_RUN" = "1" ] && echo true || echo false ),\"stagger_secs\":$STAGGER_SECS,"
    echo "\"interleave_rule\":\"first model = q38-side container if (seed_index + family_index) even else q36-side\","
    echo "\"pass\":$( [ $fail = 0 ] && echo true || echo false ),\"checks\":["
    local IFS=,; echo "${results[*]}"
    echo "]}"
  } > "$record"
  log "preflight record -> $record"
  return $fail
}

# ---------- plan + execution ---------------------------------------------

log "arm=$ARM seeds=${SEEDS[*]} families=${#FAMILIES[@]} waves=$N_WAVES dry_run=$DRY_RUN"

PREFLIGHT_OK=1
if preflight; then
  PREFLIGHT_OK=1
else
  PREFLIGHT_OK=0
  if [ "$DRY_RUN" = "1" ]; then
    log "preflight FAILED (dry-run: continuing to print the plan; a DSV4-drain failure is EXPECTED while production serves)"
  else
    die "preflight failed — refusing to open the quant-pilot window"
  fi
fi

for seed in "${SEEDS[@]}"; do
  # Parity is keyed to the seed's position in the arm's FIXED seed list (not
  # the invocation subset), so a partial re-invocation (--seeds 211) keeps
  # the exact interleave the full window would have used.
  seed_index=-1; _i=-1
  for _a in "${ALL_SEEDS[@]}"; do _i=$((_i + 1)); [ "$_a" = "$seed" ] && seed_index=$_i; done
  [ "$seed_index" -ge 0 ] || die "seed $seed not in arm seed list"
  phase="$(phase_of_seed "$seed")" || die "seed $seed not in host_plan"

  if [ "$DRY_RUN" = "0" ]; then
    manifest_path="$(write_serving_manifest "$seed" "$phase" | tail -1)"
    export BENCH_SERVING_MANIFEST="$manifest_path"
    log "seed $seed serving manifest -> $manifest_path"
    WINDOW_OPENED=1
  fi

  wave_index=-1
  while [ $((wave_index + 1)) -lt "$N_WAVES" ]; do
    wave_index=$((wave_index + 1))
    wave_quant="$(wave_field "$wave_index" quant)"
    wave_keys=($(wave_field "$wave_index" model_keys))
    mk_q38="${wave_keys[0]}"; mk_q36="${wave_keys[1]}"

    if [ "$DRY_RUN" = "1" ]; then
      for mk in "${wave_keys[@]}"; do
        gpu_uuid="$(plan_field "$phase" "$mk" gpu_uuid)"
        port="$(plan_field "$phase" "$mk" port)"
        alias="$(model_field "$mk" alias)"
        rel="$(model_field "$mk" model_rel)"
        container="$(model_field "$mk" container_base)-s${seed}"
        log "PLAN seed=$seed wave=$wave_quant container=$container gpu=$gpu_uuid port=$port"
        echo "  docker run -d --name $container --restart=no --gpus device=$gpu_uuid --shm-size 8g --label mmbt.campaign=qwen-corrective-quant-pilot --label mmbt.model-sha256=$(model_field "$mk" model_sha256) --label mmbt.server-profile=$(model_field "$mk" server_profile) --label mmbt.quantpilot.seed=$seed --label mmbt.quantpilot.model-key=$mk --label mmbt.quantpilot.gpu-uuid=$gpu_uuid --read-only --tmpfs /tmp:rw,nosuid,size=1g --tmpfs /root/.nv:rw,nosuid,size=2g -v ${MODEL_STORE}:/models:ro -p 127.0.0.1:${port}:8080 $IMAGE_REF --model /models/${rel} --alias $alias --host 0.0.0.0 --port 8080 --n-gpu-layers 999 --ctx-size $EXPECTED_CTX --batch-size 2048 --threads 4 --parallel $EXPECTED_SLOTS --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --jinja --reasoning-format none --no-context-shift --metrics"
      done
    else
      start_container "$mk_q38" "$seed" "$phase"
      start_container "$mk_q36" "$seed" "$phase"
    fi

    fam_index=-1
    for family in "${FAMILIES[@]}"; do
      fam_index=$((fam_index + 1))
      if [ $(( (seed_index + fam_index) % 2 )) -eq 0 ]; then
        first="$mk_q38"; second="$mk_q36"
      else
        first="$mk_q36"; second="$mk_q38"
      fi

      if [ "$DRY_RUN" = "1" ]; then
        python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$first" \
          --family "$family" --seed "$seed" --dry-run
        python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$second" \
          --family "$family" --seed "$seed" --dry-run
        continue
      fi

      log "seed $seed wave $wave_quant family $family: start order $first -> $second (stagger ${STAGGER_SECS}s)"
      python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$first" \
        --family "$family" --seed "$seed" --max-infra-retries "$MAX_INFRA_RETRIES" &
      pid_first=$!
      sleep "$STAGGER_SECS"
      python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$second" \
        --family "$family" --seed "$seed" --max-infra-retries "$MAX_INFRA_RETRIES" &
      pid_second=$!

      rc_first=0; rc_second=0
      wait "$pid_first" || rc_first=$?
      wait "$pid_second" || rc_second=$?
      if [ "$rc_first" != "0" ] || [ "$rc_second" != "0" ]; then
        die "cell supervisor failed (rc $first=$rc_first $second=$rc_second) at seed $seed wave $wave_quant family $family — stop and report (see $CORR_LOGS/rerun_ledger.jsonl)"
      fi
    done

    if [ "$DRY_RUN" = "0" ]; then
      stop_container "$(model_field "$mk_q38" container_base)-s${seed}"
      stop_container "$(model_field "$mk_q36" container_base)-s${seed}"
      log "seed $seed wave $wave_quant complete; containers torn down"
    fi
  done
done

if [ "$DRY_RUN" = "1" ]; then
  log "dry-run complete: plan printed above; preflight $( [ "$PREFLIGHT_OK" = "1" ] && echo PASSED || echo FAILED ); nothing was started"
  exit 0
fi

log "all quant-pilot cells complete; building evidence manifest"
python3 "$HERE/evidence_manifest.py" build --config "$CONFIG" \
  --out "$CORR_LOGS/manifest-$ARM.jsonl" ||
  die "evidence manifest build reported missing cells — stop and report"
python3 "$HERE/evidence_manifest.py" check --config "$CONFIG" \
  --manifest "$CORR_LOGS/manifest-$ARM.jsonl" ||
  die "fixed-N balance check FAILED for $ARM — stop and report"

log "quant-pilot window complete for seeds ${SEEDS[*]}; manifest -> $CORR_LOGS/manifest-$ARM.jsonl"
