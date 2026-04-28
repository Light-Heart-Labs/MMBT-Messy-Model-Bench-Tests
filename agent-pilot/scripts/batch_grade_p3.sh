#!/usr/bin/env bash
# Batch-grades Phase 3 runs. Most produce STRUCTURAL_PASS / STRUCTURAL_FAIL or
# verdicts derived from programmatic+keyword checks. The "real" grade for
# subjective tasks comes from hand-rating the placeholders later.
set -e

BENCH=$(cd "$(dirname "$0")/.." && pwd)
LOGS_DIR="$BENCH/logs"
GT_DIR="$BENCH/graders/ground_truth"

for run_dir in "$LOGS_DIR"/p3_*/; do
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
    p3_doc_*) task=doc_synthesis; gt="$GT_DIR/phase3_doc_synthesis.json" ;;
    p3_business_*) task=business_memo; gt="$GT_DIR/phase3_business_memo.json" ;;
    p3_market_*) task=market_research; gt="$GT_DIR/phase3_market_research_rubric.json" ;;
    p3_writing_*) task=writing_editing; gt="$BENCH/inputs/phase3_writing_editing/audience_briefs.json" ;;
    p3_pm_*) task=project_mgmt; gt="$GT_DIR/phase3_project_mgmt.json" ;;
    *) echo "UNKNOWN run pattern: $run"; continue ;;
  esac

  workspace_dir="/tmp/grade_$run"
  rm -rf "$workspace_dir"
  mkdir -p "$workspace_dir"
  tar -xzf "$tarball" -C "$workspace_dir"

  case "$task" in
    doc_synthesis)
      grader="$BENCH/graders/phase3_doc_synthesis_grade.py" ;;
    business_memo)
      grader="$BENCH/graders/phase3_business_memo_grade.py" ;;
    market_research)
      grader="$BENCH/graders/phase3_market_research_grade.py" ;;
    writing_editing)
      grader="$BENCH/graders/phase3_writing_editing_grade.py" ;;
    project_mgmt)
      grader="$BENCH/graders/phase3_project_mgmt_grade.py" ;;
  esac

  echo "GRADE $run  (task=$task)"
  python3 "$grader" "$workspace_dir" "$gt" --out "$run_dir/grade.json" 2>&1 | tail -3 || \
    echo "  (grader failed)"
done
