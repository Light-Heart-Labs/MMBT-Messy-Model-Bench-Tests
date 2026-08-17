#!/usr/bin/env bash
# Argv-capture verification of the v2-brief + sandbox-network wiring through
# the PATCHED run_microbench.sh, without any endpoint or model. Same
# fake-python3/fake-curl technique as dryrun_argv_capture.sh.
#
# Hermetic (audit A4): operates on the checkout this script lives in (no
# hardcoded campaign-host path), touches nothing outside mktemp space, needs
# no docker, no endpoint, no fleet host. Exits 0 iff every check passed; the
# final line on success is ALL_V2_WIRING_CHECKS_PASSED.
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
export PATH="$TMP/bin:$PATH"

export BENCH_TEMP=0.7 BENCH_TOP_P=0.8 BENCH_TOP_K=20 BENCH_MIN_P=0.0
export BENCH_PRESENCE_PENALTY=1.5 BENCH_REPEAT_PENALTY=1.0
export BENCH_SEED=101 BENCH_SANDBOX_GPUS=none BENCH_PRESERVE_THINKING=true
export BENCH_MAX_OUTPUT_TOKENS_CAP=262144

run_case() { # name family briefs network label
  local name="$1" family="$2" briefs="$3" network="$4" label="$5"
  export BENCH_TEST_CAPTURE="$TMP/argv-$name.txt"
  export BENCH_TASK_ONLY="$family"
  if [ -n "$briefs" ]; then export BENCH_TASK_BRIEFS="$briefs"; else unset BENCH_TASK_BRIEFS || true; fi
  if [ -n "$network" ]; then export BENCH_SANDBOX_NETWORK="$network"; else unset BENCH_SANDBOX_NETWORK || true; fi
  bash "$REPO/tooling/scripts/run_microbench.sh" \
    Qwen3.8-27B-UD-Q4_K_XL 18101 "$label" 1 "" off 262144 > "$TMP/out-$name.txt" 2>&1
}

expect_line() { # capture-file exact-line
  if grep -qx -- "$2" "$1"; then echo "PASS  $2"; else echo "FAIL  wanted line: $2"; exit 1; fi
}
expect_absent() { # capture-file exact-line
  if grep -qx -- "$2" "$1"; then echo "FAIL  must NOT appear: $2"; exit 1; else echo "PASS  absent: $2"; fi
}

echo "== case 1: v2 + p3_market -> v2 brief + offline network =="
run_case c1 p3_market v2 mmbt-p3-offline q38-official-nothink-s101
expect_line "$TMP/argv-c1.txt" "$REPO/tooling/tasks/v2/task_market_research.md"
expect_line "$TMP/argv-c1.txt" "--sandbox-network"
expect_line "$TMP/argv-c1.txt" "mmbt-p3-offline"

echo "== case 2: v2 + p1_bugfix (no v2 brief, no network) -> v1 brief, no flag =="
run_case c2 p1_bugfix v2 "" q38-official-nothink-s101
expect_line "$TMP/argv-c2.txt" "$REPO/tooling/tasks/task_code_adoption.md"
expect_absent "$TMP/argv-c2.txt" "--sandbox-network"

echo "== case 3: v2 + p2_triage -> v2 brief, no network flag =="
run_case c3 p2_triage v2 "" q38-official-nothink-s101
expect_line "$TMP/argv-c3.txt" "$REPO/tooling/tasks/v2/task_triage.md"
expect_absent "$TMP/argv-c3.txt" "--sandbox-network"

echo "== case 4: env unset -> historical v1 behavior, even for p3_market =="
run_case c4 p3_market "" "" q38-official-nothink-s101
expect_line "$TMP/argv-c4.txt" "$REPO/tooling/tasks/task_market_research.md"
expect_absent "$TMP/argv-c4.txt" "--sandbox-network"
expect_absent "$TMP/argv-c4.txt" "$REPO/tooling/tasks/v2/task_market_research.md"

echo "== case 5: the six v2 families each resolve to their v2 brief =="
declare -A SIX=(
  [p2_triage]=task_triage.md
  [p3_doc]=task_doc_synthesis.md
  [p3_business]=task_business_memo.md
  [p3_market]=task_market_research.md
  [p3_writing]=task_writing_editing.md
  [p3_pm]=task_project_mgmt.md
)
for fam in "${!SIX[@]}"; do
  run_case "six-$fam" "$fam" v2 "" q38-official-nothink-s101
  expect_line "$TMP/argv-six-$fam.txt" "$REPO/tooling/tasks/v2/${SIX[$fam]}"
done

# Hermeticity regression assertion (audit A4c): the dry run must leave the
# checkout byte-clean - nothing in the throwaway areas, ignored files included.
# Empty leftover dirs are fine (git cannot track them); prune empties first.
rmdir "$REPO/logs" "$REPO/tooling/workspace" 2>/dev/null || true
residue=$(git -C "$REPO" status --porcelain --ignored=matching -- logs tooling/workspace)
if [ -n "$residue" ]; then
  echo "FAIL residue left in throwaway areas:"; printf '%s\n' "$residue"; exit 1
fi
echo "PASS post-run worktree clean (logs/ + tooling/workspace/ untouched)"

echo ALL_V2_WIRING_CHECKS_PASSED
