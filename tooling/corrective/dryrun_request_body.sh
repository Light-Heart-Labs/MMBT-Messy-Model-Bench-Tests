#!/usr/bin/env bash
# Dry-run 2: full-path request-BODY verification. Drives the PATCHED
# run_microbench.sh -> real harness.py -> a local echo endpoint and asserts
# the JSON actually sent on the wire carries the per-cell seed and the
# official-nothink sampler. One model turn (finish_reason=stop), then the
# harness writes summary + tarball like any completed cell. All throwaway
# artifacts are relocated out of the repo afterwards (default evidence dir:
# ~/corrective-dryrun/, override with DRYRUN_OUT=<dir>).
#
# NOT hermetic: needs docker, the locally built bench-sandbox:latest image,
# and the alpine image for cleanup. Runs on the campaign host, not in CI.
#
# Exit contract (audit A4a): exits 0 iff every wire/receipt check passed AND
# the post-run worktree is clean; the final line on success is
# REQUEST_BODY_PLUMB_VERIFIED.
#
# Cleanup contract (audit A4b): the sandbox container runs as root, so its
# workspace output under tooling/workspace/ is root-owned on the host. It is
# scrubbed INSIDE a container mounting ONLY the workspace dir - never with
# sudo.
#
# Regression assertion (audit A4c): after cleanup the script PROVES the
# worktree is clean - throwaway dirs gone, git status --porcelain (ignored
# included) empty in the throwaway areas, and zero root-owned files left
# under logs/ or tooling/workspace/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT=18999
ALIAS=echo-model-plumbtest
LABEL=plumbtest-nothink-s101
RUN="p2_extract_${LABEL}_v1"
WS="$REPO/tooling/workspace"
OUT="${DRYRUN_OUT:-$HOME/corrective-dryrun}"
CAPTURE="$OUT/request-bodies.jsonl"
mkdir -p "$OUT"
rm -f "$CAPTURE"
rm -rf "${OUT:?}/$RUN"   # stale evidence dir would nest the mv below

scrub_throwaway_workspace() {
  # Root-owned sandbox output: delete inside a container mounting only the
  # workspace dir (audit A4b - no sudo).
  if [ -e "$WS/$RUN" ] || [ -e "$WS/_input_$RUN" ]; then
    docker run --rm -v "$WS:/w" alpine rm -rf "/w/$RUN" "/w/_input_$RUN"
  fi
}

EP_PID=""
cleanup() {
  if [ -n "$EP_PID" ]; then kill "$EP_PID" 2>/dev/null || true; fi
  docker rm -f "bench-sandbox-$RUN" >/dev/null 2>&1 || true
  scrub_throwaway_workspace || true
}
trap cleanup EXIT

python3 "$REPO/tooling/corrective/echo_endpoint.py" "$PORT" "$ALIAS" "$CAPTURE" &
EP_PID=$!
sleep 1

export BENCH_TEMP=0.7 BENCH_TOP_P=0.8 BENCH_TOP_K=20 BENCH_MIN_P=0.0
export BENCH_PRESENCE_PENALTY=1.5 BENCH_REPEAT_PENALTY=1.0
export BENCH_SEED=101
export BENCH_TASK_ONLY=p2_extract
export BENCH_SANDBOX_GPUS=none
export BENCH_PRESERVE_THINKING=true
export BENCH_MAX_OUTPUT_TOKENS_CAP=262144

cd "$REPO"
rm -rf "logs/$RUN"
scrub_throwaway_workspace   # a stale root-owned tree from an aborted prior run
bash tooling/scripts/run_microbench.sh "$ALIAS" "$PORT" "$LABEL" 1 "" off 262144

echo "=== captured request body checks ==="
python3 - "$CAPTURE" "$REPO/logs/$RUN/receipt.json" <<'PY'
import json, sys
bodies = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
assert len(bodies) == 1, f"expected exactly 1 request, got {len(bodies)}"
b = bodies[0]
checks = {
    "seed": (b.get("seed"), 101),
    "temperature": (b.get("temperature"), 0.7),
    "top_p": (b.get("top_p"), 0.8),
    "top_k": (b.get("top_k"), 20),
    "min_p": (b.get("min_p"), 0.0),
    "presence_penalty": (b.get("presence_penalty"), 1.5),
    "repeat_penalty": (b.get("repeat_penalty"), 1.0),
    "chat_template_kwargs.enable_thinking":
        (b.get("chat_template_kwargs", {}).get("enable_thinking"), False),
    "chat_template_kwargs.preserve_thinking":
        (b.get("chat_template_kwargs", {}).get("preserve_thinking"), True),
    "reasoning_effort absent (nothink arm)": (b.get("reasoning_effort"), None),
}
fail = False
for name, (got, want) in checks.items():
    ok = got == want
    fail |= not ok
    print(("PASS" if ok else "FAIL"), name, "=", got, ("" if ok else f"(want {want})"))
receipt = json.load(open(sys.argv[2]))
d = receipt["inference_request_defaults"]
print("receipt seed:", d["seed"], "PASS" if d["seed"] == 101 else "FAIL")
print("receipt enable_thinking:", d["enable_thinking"],
      "PASS" if d["enable_thinking"] is False else "FAIL")
sys.exit(1 if fail or d["seed"] != 101 else 0)
PY

echo "=== relocating throwaway evidence out of logs/ ==="
mv "logs/$RUN" "$OUT/$RUN"
scrub_throwaway_workspace

echo "=== post-run worktree cleanliness (audit A4c regression assertion) ==="
if [ -e "logs/$RUN" ]; then
  echo "FAIL residue: logs/$RUN still present"; exit 1
fi
if [ -e "$WS/$RUN" ] || [ -e "$WS/_input_$RUN" ]; then
  echo "FAIL residue: workspace throwaway still present under $WS"; exit 1
fi
# Empty leftover dirs are fine (git cannot track them) but --ignored=matching
# still lists them - prune empties first; anything non-empty survives rmdir
# and trips the porcelain gate below.
rmdir "$REPO/logs" "$WS" 2>/dev/null || true
residue=$(git -C "$REPO" status --porcelain --ignored=matching -- logs tooling/workspace)
if [ -n "$residue" ]; then
  echo "FAIL residue in throwaway areas:"; printf '%s\n' "$residue"; exit 1
fi
rooty=$( { find "$WS" "$REPO/logs" -user root -print -quit 2>/dev/null; } || true)
if [ -n "$rooty" ]; then
  echo "FAIL residue: root-owned files remain: $rooty"; exit 1
fi
echo "PASS post-run worktree clean: throwaways gone, porcelain empty, no root-owned residue"
ls "$OUT/$RUN"
echo REQUEST_BODY_PLUMB_VERIFIED
