#!/usr/bin/env bash
# Batch-grades all completed Phase 2 runs.
set -e

BENCH=$(cd "$(dirname "$0")/.." && pwd)
LOGS_DIR="$BENCH/logs"
GT_DIR="$BENCH/graders/ground_truth"

for run_dir in "$LOGS_DIR"/p2_*/; do
  run=$(basename "$run_dir")
  tarball="$run_dir/workspace_final.tar.gz"
  if [ ! -f "$tarball" ]; then
    echo "SKIP $run (no workspace_final.tar.gz)"
    continue
  fi
  if [ -f "$run_dir/grade.json" ]; then
    echo "SKIP $run (already graded)"
    continue
  fi

  case "$run" in
    p2_extract_*) task=extraction; gt="$GT_DIR/phase2_extraction.json" ;;
    p2_ci_*) task=ci_failure; gt="" ;;
    p2_hallucination_*) task=hallucination; gt="$GT_DIR/phase2_hallucination.json" ;;
    p2_triage_*) task=triage; gt="$GT_DIR/phase2_triage.json" ;;
    *) echo "UNKNOWN run pattern: $run"; continue ;;
  esac

  workspace_dir="/tmp/grade_$run"
  rm -rf "$workspace_dir"
  mkdir -p "$workspace_dir"
  tar -xzf "$tarball" -C "$workspace_dir"

  # Each task uses its task-specific grader
  case "$task" in
    extraction)
      grader="$BENCH/graders/phase2_extraction_grade.py"
      args=("$workspace_dir" "$gt") ;;
    ci_failure)
      grader="$BENCH/graders/phase2_ci_failure_grade.py"
      args=("$workspace_dir") ;;
    hallucination)
      grader="$BENCH/graders/phase2_hallucination_grade.py"
      args=("$workspace_dir" "$gt") ;;
    triage)
      grader="$BENCH/graders/phase2_triage_grade.py"
      args=("$workspace_dir" "$gt") ;;
  esac

  echo "GRADE $run  (task=$task)"
  python3 "$grader" "${args[@]}" --out "$run_dir/grade.json" 2>&1 | tail -5 || \
    echo "  (grader failed)"
done
