#!/usr/bin/env bash
# Batch-grades all completed Phase 1 runs against the logalyzer baseline.
# Skips runs that were killed mid-flight (no workspace_final.tar.gz).
set -e

BENCH=$(cd "$(dirname "$0")/.." && pwd)
BASELINE=/tmp/p1_baseline
LOGS_DIR="$BENCH/logs"
GRADER="$BENCH/graders/phase1_grade.py"

# Extract baseline once
rm -rf "$BASELINE"
mkdir -p "$BASELINE"
cp -r "$BENCH/inputs/code-task-starter/"* "$BASELINE/"

for run_dir in "$LOGS_DIR"/p1_*/; do
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

  # Determine task from run name
  case "$run" in
    p1_bugfix_*) task=bugfix ;;
    p1_testwrite_*) task=testwrite ;;
    p1_refactor_*) task=refactor ;;
    *) echo "UNKNOWN run pattern: $run"; continue ;;
  esac

  # Extract workspace
  workspace_dir="/tmp/grade_$run"
  rm -rf "$workspace_dir"
  mkdir -p "$workspace_dir"
  tar -xzf "$tarball" -C "$workspace_dir"

  # The agent's repo is typically at /workspace/repo, /workspace/, or
  # /workspace/<some-name>. Find the dir that contains pyproject.toml or logalyzer/
  agent_repo=""
  for candidate in "$workspace_dir/repo" "$workspace_dir" "$workspace_dir"/*/; do
    candidate="${candidate%/}"
    if [ -d "$candidate/logalyzer" ] || [ -f "$candidate/pyproject.toml" ]; then
      agent_repo="$candidate"
      break
    fi
  done
  if [ -z "$agent_repo" ]; then
    echo "FAIL $run (no agent repo found in tarball)"
    continue
  fi

  echo "GRADE $run  (task=$task, repo=$agent_repo)"
  python3 "$GRADER" "$task" "$agent_repo" "$BASELINE" --out "$run_dir/grade.json" 2>&1 | tail -3 || \
    echo "  (grader failed)"
done
