#!/usr/bin/env bash
# Dry-run 1: prove BENCH_SEED -> --seed and BENCH_TASK_ONLY -> single family
# through the PATCHED run_microbench.sh, without any endpoint or model.
# Same fake-python3/fake-curl technique as test_run_microbench_qwen38_transport.py.
#
# Hermetic (audit A4): operates on the checkout this script lives in (no
# hardcoded campaign-host path), touches nothing outside mktemp space, needs
# no docker, no endpoint, no fleet host. Exits 0 iff every check passed; the
# final line on success is ALL_ARGV_CHECKS_PASSED.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"
cat > "$TMP/bin/curl" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat > "$TMP/bin/python3" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" >> "$BENCH_TEST_CAPTURE"
EOF
chmod +x "$TMP/bin/curl" "$TMP/bin/python3"

export BENCH_TEST_CAPTURE="$TMP/argv.txt"
export PATH="$TMP/bin:$PATH"
export BENCH_TEMP=0.7 BENCH_TOP_P=0.8 BENCH_TOP_K=20 BENCH_MIN_P=0.0
export BENCH_PRESENCE_PENALTY=1.5 BENCH_REPEAT_PENALTY=1.0
export BENCH_SEED=101
export BENCH_TASK_ONLY=p2_extract
export BENCH_SANDBOX_GPUS=none
export BENCH_PRESERVE_THINKING=true
export BENCH_MAX_OUTPUT_TOKENS_CAP=262144

out=$(bash "$REPO/tooling/scripts/run_microbench.sh" \
  Qwen3.8-27B-UD-Q4_K_XL 18101 q38-official-nothink-s101 1 "" off 262144)

runs=$(grep -c "p2_extract_q38-official-nothink-s101_v1" <<< "$out" || true)
echo "$out" | grep -E "==> Microbench chain: |p2_"

harness_calls=$(grep -c "harness.py" "$BENCH_TEST_CAPTURE" || true)
echo "harness invocations captured: $harness_calls"

check() { # flag value
  if grep -A1 -x -- "$1" "$BENCH_TEST_CAPTURE" | tail -1 | grep -qx -- "$2"; then
    echo "PASS $1 $2"
  else
    echo "FAIL $1 (wanted $2)"; exit 1
  fi
}
check --seed 101
check --temperature 0.7
check --top-p 0.8
check --top-k 20
check --min-p 0.0
check --presence-penalty 1.5
check --repeat-penalty 1.0
check --thinking off
check --preserve-thinking on
check --max-model-len 262144
grep -qx -- "--gpus" "$BENCH_TEST_CAPTURE" && { echo "FAIL --gpus present"; exit 1; } || echo "PASS --gpus omitted"

total=$(grep -x -- "p2_extract_q38-official-nothink-s101_v1" "$BENCH_TEST_CAPTURE" | wc -l)
echo "run-name args in capture: $total (want 1: only the filtered family ran)"
[ "$total" = "1" ] || exit 1

# Hermeticity regression assertion (audit A4c): the dry run must leave the
# checkout byte-clean - nothing in the throwaway areas, ignored files included.
# Empty leftover dirs are fine (git cannot track them); prune empties first.
rmdir "$REPO/logs" "$REPO/tooling/workspace" 2>/dev/null || true
residue=$(git -C "$REPO" status --porcelain --ignored=matching -- logs tooling/workspace)
if [ -n "$residue" ]; then
  echo "FAIL residue left in throwaway areas:"; printf '%s\n' "$residue"; exit 1
fi
echo "PASS post-run worktree clean (logs/ + tooling/workspace/ untouched)"

echo ALL_ARGV_CHECKS_PASSED
