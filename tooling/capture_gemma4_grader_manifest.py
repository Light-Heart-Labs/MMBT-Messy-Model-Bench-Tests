#!/usr/bin/env python3
"""Fingerprint the exact grader stack and raw Gemma grades for publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from summarize_gemma4_campaign import TASKS


GRADER_FILES = [
    "tooling/scripts/grade_microbench.sh",
    "tooling/graders/phase1_grade.py",
    "tooling/graders/code_task_grader.py",
    "tooling/graders/phase2_extraction_grade.py",
    "tooling/graders/phase2_ci_failure_grade.py",
    "tooling/graders/phase2_hallucination_grade.py",
    "tooling/graders/phase2_triage_grade.py",
    "tooling/graders/phase3_doc_synthesis_grade.py",
    "tooling/graders/phase3_business_memo_grade.py",
    "tooling/graders/phase3_market_research_grade.py",
    "tooling/graders/phase3_writing_editing_grade.py",
    "tooling/graders/phase3_project_mgmt_grade.py",
    "tooling/graders/ground_truth/phase2_extraction.json",
    "tooling/graders/ground_truth/phase2_hallucination.json",
    "tooling/graders/ground_truth/phase2_triage.json",
    "tooling/graders/ground_truth/phase3_doc_synthesis.json",
    "tooling/graders/ground_truth/phase3_business_memo.json",
    "tooling/graders/ground_truth/phase3_market_research_rubric.json",
    "tooling/graders/ground_truth/phase3_project_mgmt.json",
    "tooling/inputs/phase3_writing_editing/audience_briefs.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint_files(root: Path, relative_paths: list[str]) -> tuple[dict, list[str]]:
    files = {}
    errors = []
    for relative in relative_paths:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing grader input: {relative}")
            continue
        files[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return files, errors


def command_output(command: list[str]) -> str | None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--label", default="gemma4-31b-q4")
    parser.add_argument("--target-n", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    files, errors = fingerprint_files(root, GRADER_FILES)
    grades = []
    for task in TASKS:
        for rep in range(1, args.target_n + 1):
            name = f"{task}_{args.label}_v{rep}"
            run = root / "logs" / name
            grade = run / "grade.json"
            label = run / "label.json"
            if grade.is_file():
                payload = json.loads(grade.read_text())
                grades.append({
                    "run_name": name, "verdict": payload.get("verdict"),
                    "grade_json": {"bytes": grade.stat().st_size, "sha256": sha256(grade)},
                })
            elif label.is_file():
                payload = json.loads(label.read_text())
                grades.append({
                    "run_name": name, "terminal_label": payload.get("primary"),
                    "label_json": {"bytes": label.stat().st_size, "sha256": sha256(label)},
                })
            else:
                errors.append(f"{name}: neither raw grade nor terminal label exists")
    git_status = command_output(["git", "-C", str(root), "status", "--porcelain"])
    if git_status:
        errors.append("grader manifest captured from dirty worktree")
    document = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "label": args.label,
        "target_n": args.target_n,
        "passed": not errors,
        "errors": errors,
        "repository_commit": command_output(["git", "-C", str(root), "rev-parse", "HEAD"]),
        "python": sys.version,
        "docker_version": command_output(["docker", "version", "--format", "{{.Server.Version}}"]),
        "bench_sandbox_image_id": command_output([
            "docker", "image", "inspect", "bench-sandbox:latest", "--format", "{{.Id}}",
        ]),
        "grader_files": files,
        "raw_grades": grades,
        "correction_policy": (
            "grade.json and label.json hashes are immutable raw evidence. Any correction "
            "must be a separate overlay naming the original hash, corrected grader hash, "
            "unchanged workspace archive hash, and reproducible defect."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({
        "passed": document["passed"], "grader_files": len(files),
        "raw_grades": len(grades), "errors": len(errors),
    }, sort_keys=True))
    raise SystemExit(0 if document["passed"] else 1)


if __name__ == "__main__":
    main()
