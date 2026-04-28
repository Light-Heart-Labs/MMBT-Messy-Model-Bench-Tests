#!/usr/bin/env python3
"""One-time hand-labeling of all PR-audit-family runs.

Run once. Writes label.json sibling to each run's receipt/transcript/summary.
Labels reflect the human labeler's call as of 2026-04-27 against the vocabulary
in agent-pilot/FAILURE-TAXONOMY.md. Future runs can have label.json written
either by re-running this script (if updated) or by hand directly.

If a run dir already has label.json with `labeler: human` and a notes field,
this script will not overwrite it — pass --force to override.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

LABELED_AT = "2026-04-28T00:00:00Z"

# Hand labels for the PR-audit-family runs. Format:
#   run_name: (primary_label, sub_labels_list, notes_string)
LABELS = {
    # 75-PR task — Coder-Next smokes (wall-time-capped, surfaced harness gaps)
    "coder_pr_audit_smoke_v1": (
        "identical-call-loop",
        ["harness-mid-fix"],
        "30 consecutive identical curl .../pull/1057/files calls (iters 12-41). Surfaced the temp=0+seed=42 deterministic loop trap. Led to --temperature flag.",
    ),
    "coder_pr_audit_smoke_v2": (
        "stuck-in-research",
        ["harness-mid-fix"],
        "30 ls -la calls of different DreamServer subdirs without writes. Surfaced the workspace-state-hash gap on read-only ops. Led to --stuck-threshold flag.",
    ),
    "coder_pr_audit_smoke_v3": (
        "identical-call-loop",
        ["harness-mid-fix", "wall-killed"],
        "50+ consecutive identical `git log --oneline -1000 --all | grep \"Merge pull request\" | sed | awk | grep | uniq` commands. Wall-clock killed before stuck-detector fired.",
    ),

    # 75-PR task — Coder-Next canonical attempts (with harness fixes applied)
    "coder_pr_audit_canonical_v1": (
        "cyclic-name-slop",
        ["aborted-mid-run"],
        "60 decisions/0XX-final-{report,merge,verification,approval,strategy}.md ADRs across 5 byte-identical templates cycled by filename. Killed manually after content-hash dedupe confirmed the pattern.",
    ),
    "coder_pr_audit_canonical_v2": (
        "stuck-in-research",
        ["aborted-mid-run"],
        "157 iters of legitimate `git diff origin/main..pr-XXXX` across dozens of distinct PRs. 0 write_file calls, 0 git commits. Killed on pivot to escalation experiment, but trajectory had been read-only-forever for the whole run.",
    ),

    # 75-PR task — 27B canonical runs
    "27b_pr_audit_canonical_v1": (
        "scaffold-and-stop",
        [],
        "75/75 verdict.md files, but only 3 are real reviews (PR-1057, PR-988, PR-750). Other 72 average 15 lines, single-sentence reasons pulled from PR titles. Tagged v1.0. Zero tests run, zero bug reproductions despite spec requiring both. Best of the three 27B canonical runs — published as the MMBT entry.",
    ),
    "27b_pr_audit_canonical_v2": (
        "scaffold-and-stop",
        [],
        "75/75 verdict.md files, 0 hand-written reviews. Verdict distribution shifted toward MERGE (64/9/2 vs v1's 59/10/6). Did not tag a release. Model literally named the second commit 'Batch review scaffolding' — admitting the scaffolds are stubs.",
    ),
    "27b_pr_audit_canonical_v3": (
        "scaffold-and-stop",
        [],
        "Most files of any 27B canonical (761) but zero git commits ever made (spec violation). Most lenient verdict distribution: 70 MERGE / 4 REVISE / 1 REJECT. Created 175 PR directories vs 75 expected.",
    ),

    # 75-PR task — 27B smoke (wall-time-capped to 5 min for harness validation)
    "27b_pr_audit_smoke_v1": (
        "wall-killed",
        [],
        "First 27B smoke on the 75-PR task. Bulk-downloaded all 75 PR diffs to /tmp/pr_diffs/. Wrote initial README + pr_analyzer.py + ran the analyzer. Made one substantive first commit. Wall-clock killed at iter 26 mid-`cat pr-750.diff`. Demonstrated 27B can do real work on this task class — distinct from Coder-Next smokes that surfaced loops.",
    ),

    # N=1 task — Coder-Next variance batch
    "n1_coder_v1": (
        "success-shipped-wrong",
        ["wrong-on-1-claims"],
        "REJECT for correctness. Conflated _handle_model_list comment with _handle_model_download behavior. Verdict shipped clean (13/13 files, 20 commits, tag, done()) but wrong on the catalog-handling architectural distinction.",
    ),
    "n1_coder_v2": (
        "success-shipped",
        ["cherry-picked"],
        "MERGE after minor doc improvements. Correctly identified the catalog asymmetry as intentional. Matches ground truth. Cherry-picked correct run of three; other two (v1, v3) gave REJECT (wrong).",
    ),
    "n1_coder_v3": (
        "success-shipped-wrong",
        ["wrong-on-4-claims"],
        "REJECT for correctness AND quality, citing four issues: stderr-direction (BACKWARDS — claimed errors at start when PR's whole point is they're at end), catalog 500 (same conflation as v1), pull edge case (speculation, not tested), llama-server RuntimeError (claimed inconsistent with codebase when it's the explicit fix). Authored fake `tests/test_stderr_truncation.py` to 'demonstrate' the non-existent issue. Worst run of the three.",
    ),

    # N=1 task — 27B variance batch
    "n1_27b_v1": (
        "partial-no-spec-output",
        [],
        "Best 27B-on-PR-1057 by content quality at the time. 4 of 13 required files. 1 commit. No verdict.md, no tag, no done(). Caught the rollback-path silent-failure concern (real). Self-corrected on a false logger.info indentation claim. Ran pytest on baseline + PR branch.",
    ),
    "n1_27b_v2": (
        "partial-no-spec-output",
        [],
        "2 of 13 required files (tool-log.md + research/notes.md). 0 commits. Rollback-bug claim flipped from v1's 'is a bug' to v2's 'is fine' — 27B's analysis varies between runs.",
    ),
    "n1_27b_v3": (
        "partial-no-spec-output",
        [],
        "Best analytical content of any local-model run on this PR. 7 of 13 files. 0 commits. Implicit MERGE in review.md's Summary of Findings table. questions.md Q2 walks through the catalog asymmetry more cleanly than the canonical hand-written ground truth.",
    ),

    # N=1 task — 35B-A3B
    "n1_35ba3b_v1": (
        "floor-failure",
        [],
        "28 iters of legitimate investigation (cloned repo, ran pytest on both branches, grep'd for AMD), then a 25-second thinking turn (4,368 reasoning tokens) emitted no tool calls and stopped. Zero artifacts written, zero commits.",
    ),

    # Wallstreet investment-memo task — successful runs (cherry-picked best-of-three)
    "27b_invest_memo_v2": (
        "success-shipped",
        ["cherry-picked"],
        "GitLab Inc. (GTLB) BUY recommendation. 27 min, 56 iters, done_signal. 17 KB three-statement model, full audit trail, tagged release. Cherry-picked best-of-three: v3 was parser-fault-truncated, v4 hit a 1-hour single-call timeout. Score 85 in the consolidated 2x3x3 grid (best of any model on the memo task).",
    ),
    "coder_invest_memo_v5": (
        "success-shipped",
        ["cherry-picked"],
        "DocuSign (DOCU) BUY recommendation. 11 min, 95 iters, done_signal. 10.6 KB three-statement model, full audit trail, tagged release. Cherry-picked best-of-three: v6 and v7 stalled in scaffold-and-stop pattern within 1-2 minutes. Score 80 in the consolidated 2x3x3 grid. Verdict-reliability caveat from the PR-audit benchmark (single-shot Coder-Next can be confidently wrong) extends to this BUY call.",
    ),
    "27b_invest_memo_v3": (
        "partial-no-spec-output",
        [],
        "27B memo v3: model_stopped at iter 40 due to a parser fault mid-emission (XML parser hit malformed tool-call argument). 11 min wall. Substantive work in progress when the parser failed.",
    ),
    "27b_invest_memo_v4": (
        "timeout",
        [],
        "27B memo v4: api_error: timed out. The model spent 60+ minutes on a single thinking-mode inference call before the harness's 3600s urlopen timeout fired. 68 min total wall before the harness exited.",
    ),
    "coder_invest_memo_v6": (
        "scaffold-and-stop",
        [],
        "Coder-Next memo v6: 2 min, 37 iters, stuck-detector fired. Did initial scaffolding (mkdir, README, etc.) then locked into the documented Coder-Next failure pattern. Failed to transition to actual research/extraction work.",
    ),
    "coder_invest_memo_v7": (
        "scaffold-and-stop",
        [],
        "Coder-Next memo v7: 1 min, 63 iters, stuck-detector fired. Same pattern as v6 but faster — the model emitted scaffolding tool calls quickly without making progress on the actual memo work.",
    ),
    "35ba3b_invest_memo_v1": (
        "stuck-in-research",
        [],
        "35B-A3B memo v1: 6 min, 51 iters, stuck-detector fired. Did legitimate research (cloned ticker data, fetched filings) but never transitioned to memo composition.",
    ),
    "35ba3b_invest_memo_v2": (
        "floor-failure",
        [],
        "35B-A3B memo v2: 14 seconds, 14 iters, model_stopped. Floor failure at the smallest scale — emitted a few tool calls and stopped without producing anything substantive.",
    ),
    "35ba3b_invest_memo_v3": (
        "api-error",
        [],
        "35B-A3B memo v3: 7 min, 38 iters, model_exceeded_max_tokens cap. Model hit a per-response token ceiling mid-emission while attempting a memo. Only tool-log.md and a git scaffold made it into the workspace. Best of the three 35B-A3B memo runs but still not usable.",
    ),

    # N=1 task — 27B strict-done ablation (Fix 1 from the MMBT feedback round)
    "n1_27b_strict_v1": (
        "partial-no-spec-output",
        [],
        "Strict-done ablation v1: --require-files verdict.md,summary.md,README.md --require-git-tag. Outcome: 0 DONE_REJECTED events fired during the run — model never even attempted to call done(). Result is identical-shape failure to baseline n1_27b_v{1,2,3}: model_stopped at iter 65, 4 files written (research/notes.md + research/questions.md + tests/results.md + test_pr_1057_changes.py), 0 commits, no verdict.md. Strict-done validation never got to do its job because the failure isn't 'calls done() too early' — it's 'never calls done() at all.'",
    ),
    "n1_27b_strict_v2": (
        "partial-no-spec-output",
        [],
        "Strict-done ablation v2: same flags as v1. Outcome: 0 DONE_REJECTED events fired. model_stopped at iter 54 (7 min), 2 files written (summary.md + tool-log.md), 0 commits. Confirms v1's pattern — strict-done validation never gets exercised.",
    ),
    "n1_27b_strict_v3": (
        "api-error",
        [],
        "Strict-done ablation v3: same flags as v1. Outcome: 0 DONE_REJECTED events fired (consistent with v1, v2). But the failure mode shifted — instead of model_stopped, the run hit the per-response max_tokens cap (180K) at iter 53 after 63 min wall and 194K total completion tokens. A single inference call generated 180K tokens, almost certainly a runaway thinking trace before any output. Net for the strict-done question: still 0 DONE_REJECTED, still no verdict.md, still no path to scaffold-fixes-it.",
    ),

    # ============================================================================
    # PHASE 1: coding microbench (logalyzer codebase)
    # bug-fix, test-writing, refactoring × 27B + Coder-Next × N=3
    # ============================================================================

    "p1_bugfix_27b_v1": ("success-shipped", [], "Pytest 0→17, ruff clean. PASS."),
    "p1_bugfix_27b_v2": ("success-shipped", [], "Pytest 0→63, ruff clean. PASS."),
    "p1_bugfix_27b_v3": ("success-shipped", [], "Pytest 0→55, ruff clean. PASS."),
    "p1_bugfix_coder_v1": ("success-shipped", [], "Pytest 0→49/50, ruff clean. PASS."),
    "p1_bugfix_coder_v2": ("success-shipped", [], "Pytest 0→66, ruff clean. PASS."),
    "p1_bugfix_coder_v3": ("aborted-mid-run", ["post-completion-drift"], "110-min runaway: model tagged v0.3.0 at iter 540, then started running pointless `rm -rf repo && cp -r /workspace/repo .` operations destroying its own work. Killed at iter 545. New failure mode worth flagging: post-completion drift — model finishes, doesn't call done(), then makes things worse."),
    "p1_testwrite_27b_v1": ("success-shipped-wrong", [], "FAIL grade because logalyzer_unchanged=False — agent modified production code. Caveat: starter has a `from collections import Iterable` bug that prevents test collection; fixing it is required to make tests work. Task design has a chicken-and-egg conflict with the rule."),
    "p1_testwrite_27b_v2": ("success-shipped-wrong", [], "Same task-design issue as v1 — modified production code to make tests collect."),
    "p1_testwrite_27b_v3": ("success-shipped-wrong", [], "Same task-design issue."),
    "p1_testwrite_coder_v1": ("api-error", [], "Hit per-response max_tokens cap (180K) at iter 42, 23 min wall. Single thinking turn ran away."),
    "p1_testwrite_coder_v2": ("success-shipped-wrong", [], "Same task-design issue as 27B testwrite — modified production code."),
    "p1_testwrite_coder_v3": ("success-shipped-wrong", [], "Same task-design issue."),
    "p1_refactor_27b_v1": ("partial-no-spec-output", [], "Did not produce required logalyzer/output/ subpackage."),
    "p1_refactor_27b_v2": ("partial-no-spec-output", [], "Same as v1."),
    "p1_refactor_27b_v3": ("partial-no-spec-output", [], "Same as v1, but did call done()."),
    "p1_refactor_coder_v1": ("success-shipped-wrong", [], "Did create the output/ subpackage with backward-compat imports — spirit achieved. But also modified non-output files, violating the strict 'unchanged' rule. Same chicken-and-egg as testwrite — to make code work, agent had to fix the broken import."),
    "p1_refactor_coder_v2": ("success-shipped-wrong", [], "Same as v1."),
    "p1_refactor_coder_v3": ("success-shipped-wrong", [], "Same as v1."),

    # ============================================================================
    # PHASE 2: programmatic-graded tasks
    # extraction, CI failure, hallucination, triage × 27B + Coder-Next × N=3
    # ============================================================================

    "p2_extract_27b_v1": ("success-shipped", [], "100% accuracy on 20 fields."),
    "p2_extract_27b_v2": ("success-shipped", [], "100% accuracy."),
    "p2_extract_27b_v3": ("success-shipped", [], "100% accuracy."),
    "p2_extract_coder_v1": ("success-shipped", [], "95% accuracy (19/20)."),
    "p2_extract_coder_v2": ("success-shipped", [], "90% accuracy (18/20)."),
    "p2_extract_coder_v3": ("success-shipped", [], "90% accuracy (18/20)."),
    "p2_ci_27b_v1": ("success-shipped", [], "Made CI green: ruff clean, pytest passes, no shortcut markers."),
    "p2_ci_27b_v2": ("success-shipped", [], "Same."),
    "p2_ci_27b_v3": ("success-shipped", [], "Same."),
    "p2_ci_coder_v1": ("success-shipped", [], "Made CI green."),
    "p2_ci_coder_v2": ("success-shipped", [], "Made CI green."),
    "p2_ci_coder_v3": ("success-shipped", [], "Made CI green."),
    "p2_hallucination_27b_v1": ("success-shipped", [], "100% accuracy on 15 issues, 0 dangerous errors. Caught all 6 real, dismissed all 9 fabrications cleanly."),
    "p2_hallucination_27b_v2": ("success-shipped", [], "Same as v1."),
    "p2_hallucination_27b_v3": ("success-shipped", [], "Same as v1."),
    "p2_hallucination_coder_v1": ("stuck-in-research", [], "Hit stuck-detector at 500 iters / 25 min. No triage.json output."),
    "p2_hallucination_coder_v2": ("stuck-in-research", [], "Hit stuck-detector at 500 iters / 27 min. No output."),
    "p2_hallucination_coder_v3": ("success-shipped", ["wrong-on-2-claims"], "PASS but at the safety threshold: confirmed 2 fabrications as real. Squeaked over the dangerous-error ≤2 threshold."),
    "p2_triage_27b_v1": ("success-shipped", [], "Category 87%, urgency 73%, duplicate-cluster recall 100%."),
    "p2_triage_27b_v2": ("success-shipped", [], "Same."),
    "p2_triage_27b_v3": ("success-shipped", [], "Same."),
    "p2_triage_coder_v1": ("success-shipped", [], "Re-ran after chain crashed first attempt; clean PASS."),
    "p2_triage_coder_v2": ("success-shipped", [], "Category 97%, urgency 73%, duplicate recall 100%. Better category accuracy than 27B."),
    "p2_triage_coder_v3": ("success-shipped", [], "Same as v2."),

    # ============================================================================
    # PHASE 3: subjective-task family — Coder-Next runs (27B runs in progress)
    # ============================================================================

    "p3_doc_coder_v1": ("success-shipped", [], "All 8 planted facts captured. PASS."),
    "p3_doc_coder_v2": ("success-shipped-wrong", [], "7/8 facts captured, but went over 700-word limit (1005 words). FAIL."),
    "p3_doc_coder_v3": ("success-shipped", [], "7/8 facts captured, within word limit. PASS."),
    "p3_business_coder_v1": ("success-shipped", [], "Caught 7/8 planted bias signals, pushed back against deal pack. PASS at 409 words."),
    "p3_business_coder_v2": ("success-shipped", [], "7/8 bias signals, pushback. 636 words. PASS."),
    "p3_business_coder_v3": ("success-shipped", [], "6/8 bias signals, pushback. 580 words. PASS."),
    "p3_market_coder_v1": ("stuck-in-research", [], "Did not produce recommendation.md / comparison.md / sources.md. STRUCTURAL_FAIL. Probably stuck on internet-research workflow."),
    "p3_market_coder_v2": ("stuck-in-research", [], "Same."),
    "p3_market_coder_v3": ("api-error", [], "vLLM api_error: HTTP 400 (probably context overflow). 6 min, 65 iters. STRUCTURAL_FAIL."),
    "p3_writing_coder_v1": ("success-shipped", [], "All three audience rewrites PASS — within word limits, hit required content, avoided prohibited content."),
    "p3_writing_coder_v2": ("success-shipped", [], "Same."),
    "p3_writing_coder_v3": ("success-shipped-wrong", [], "v3 failed legal_summary subdimension — probably included content on the prohibited list."),
    "p3_pm_coder_v1": ("success-shipped-wrong", [], "All 6 workstreams identified, all 5 milestones, 3/4 decisions. But only 2/6 risks recalled — missed several. FAIL."),
    "p3_pm_coder_v2": ("success-shipped", [], "Workstreams 6/6, decisions 4/4, milestones 4/5, risks 3/6. PASS at the threshold."),
    "p3_pm_coder_v3": ("success-shipped-wrong", [], "Workstreams 6/6, decisions 4/4, milestones 4/5, but risks only 2/6. FAIL."),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing label.json files")
    ap.add_argument("--logs-dir", default=None)
    args = ap.parse_args()

    logs_dir = Path(args.logs_dir) if args.logs_dir else Path(__file__).resolve().parent.parent / "logs"

    written = skipped = missing = 0
    for run_name, (primary, sub, notes) in LABELS.items():
        run_dir = logs_dir / run_name
        if not run_dir.is_dir():
            print(f"MISSING  {run_name}  (no dir)")
            missing += 1
            continue
        out = run_dir / "label.json"
        if out.exists() and not args.force:
            existing = json.loads(out.read_text())
            if existing.get("labeler") == "human":
                print(f"SKIP     {run_name}  (already labeled, use --force to overwrite)")
                skipped += 1
                continue
        label_doc = {
            "primary": primary,
            "sub_labels": sub,
            "notes": notes,
            "labeler": "human",
            "labeled_at": LABELED_AT,
        }
        out.write_text(json.dumps(label_doc, indent=2))
        print(f"WROTE    {run_name:35s}  {primary}  {sub}")
        written += 1

    # Per-label tally
    from collections import Counter
    tally = Counter(p[0] for p in LABELS.values())
    print()
    print("=== LABEL DISTRIBUTION ===")
    for label, n in tally.most_common():
        print(f"  {n}  {label}")
    print(f"\ntotal: written={written}  skipped={skipped}  missing={missing}")


if __name__ == "__main__":
    main()
