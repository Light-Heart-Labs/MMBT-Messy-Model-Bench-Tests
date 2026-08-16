#!/usr/bin/env bash
# Dry-run 2: full-path request-BODY verification. Drives the PATCHED
# run_microbench.sh -> real harness.py -> a local echo endpoint and asserts
# the JSON actually sent on the wire carries the per-cell seed and the
# official-nothink sampler. One model turn (finish_reason=stop), then the
# harness writes summary + tarball like any completed cell. All throwaway
# artifacts are relocated to ~/corrective-dryrun/ afterwards.
set -euo pipefail

REPO=/home/michael/mmbt-qwen38-eaaa8ca
PORT=18999
ALIAS=echo-model-plumbtest
LABEL=plumbtest-nothink-s101
RUN="p2_extract_${LABEL}_v1"
OUT=/home/michael/corrective-dryrun
CAPTURE="$OUT/request-bodies.jsonl"
mkdir -p "$OUT"
rm -f "$CAPTURE"

python3 "$REPO/tooling/corrective/echo_endpoint.py" "$PORT" "$ALIAS" "$CAPTURE" &
EP_PID=$!
cleanup() {
  kill "$EP_PID" 2>/dev/null || true
  docker rm -f "bench-sandbox-$RUN" >/dev/null 2>&1 || true
}
trap cleanup EXIT
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
rm -rf "$REPO/tooling/workspace/$RUN" "$REPO/tooling/workspace/_input_$RUN"
ls "$OUT/$RUN"
echo REQUEST_BODY_PLUMB_VERIFIED
