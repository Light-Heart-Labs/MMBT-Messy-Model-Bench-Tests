#!/usr/bin/env python3
"""
Analyze all 75 open PRs: extract diffs, compute stats, identify subsystems,
and build the dependency/conflict graph.
"""
import json
import subprocess
import os
import re
from pathlib import Path
from collections import defaultdict

REPO_DIR = Path("/workspace/dreamserver-repo")
AUDIT_DIR = Path("/workspace/dreamserver-audit")

# Subsystem classification based on file paths
SUBSYSTEM_MAP = {
    "dream-server/bin/": "host-agent",
    "dream-server/bin/dream-host-agent.py": "host-agent",
    "dream-server/dashboard-api/": "dashboard-api",
    "dream-server/dashboard/": "dashboard-frontend",
    "dream-server/extensions/": "extensions",
    "dream-server/extensions-library/": "extensions-library",
    "dream-server/compose/": "compose",
    "dream-server/compose.yaml": "compose",
    "dream-server/compose.local.yaml": "compose",
    "dream-server/compose.override.yaml": "compose",
    "dream-server/compose.gpu-nvidia.yaml": "compose-gpu",
    "dream-server/compose.gpu-amd.yaml": "compose-gpu",
    "dream-server/compose.gpu-apple.yaml": "compose-gpu",
    "dream-server/compose.gpu-intel.yaml": "compose-gpu",
    "dream-server/scripts/": "scripts",
    "dream-server/dream-cli": "dream-cli",
    "dream-server/bin/dream-cli": "dream-cli",
    "dream-server/bin/dream": "dream-cli",
    "dream-server/tests/": "tests",
    "dream-server/test/": "tests",
    "installer/": "installer",
    "install.sh": "installer",
    "install.ps1": "installer-windows",
    "dream-server/install.sh": "installer",
    "dream-server/install-core.sh": "installer",
    "dream-server/get-dream-server.sh": "installer",
    "dream-server/dream-preflight.sh": "installer",
    "dream-server/dream-update.sh": "installer",
    "dream-server/dream-restore.sh": "installer",
    "dream-server/dream-uninstall.sh": "installer",
    "dream-server/dream-backup.sh": "installer",
    "dream-server/test-install.sh": "installer-tests",
    "dream-server/test-stack.sh": "installer-tests",
    "resources/": "resources",
    ".github/": "ci",
    "docs/": "docs",
    "README.md": "docs",
    "ARCHITECTURE.md": "docs",
    "SECURITY_AUDIT.md": "docs",
    "CONTRIBUTING.md": "docs",
    "CLAUDE.md": "docs",
}

def classify_file(filepath):
    """Classify a file path into a subsystem."""
    for prefix, subsystem in SUBSYSTEM_MAP.items():
        if filepath.startswith(prefix):
            return subsystem
    # Fallback heuristics
    if "gpu" in filepath.lower() or "rocm" in filepath.lower() or "amd" in filepath.lower():
        return "gpu"
    if "macos" in filepath.lower() or "apple" in filepath.lower() or "darwin" in filepath.lower():
        return "macos"
    if "windows" in filepath.lower() or "win" in filepath.lower() or ".ps1" in filepath:
        return "windows"
    if "test" in filepath.lower():
        return "tests"
    if "docker" in filepath.lower() or "compose" in filepath.lower():
        return "compose"
    return "other"

def get_pr_diff(pr_num, base="main"):
    """Get the diff for a PR against main."""
    try:
        result = subprocess.run(
            ["git", "diff", f"{base}..refs/remotes/pull/{pr_num}"],
            cwd=REPO_DIR,
            capture_output=True, text=True, timeout=30
        )
        return result.stdout
    except Exception as e:
        return None

def get_pr_stats(diff):
    """Extract stats from a diff."""
    if not diff:
        return {"files": [], "insertions": 0, "deletions": 0, "lines": 0}
    
    files = []
    insertions = 0
    deletions = 0
    
    for line in diff.split("\n"):
        m = re.match(r'^diff --git a/(.+?) b/(.+?)(?:$|\t)', line)
        if m:
            files.append(m.group(1))
        elif line.startswith("+++") or line.startswith("---"):
            pass
        elif line.startswith("@@"):
            m2 = re.search(r'\+(\d+)(?:,\d+)? \-(\d+)(?:,\d+)?', line)
            if m2:
                pass  # hunk info
        elif line.startswith("+") and not line.startswith("+++"):
            insertions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    
    return {
        "files": files,
        "insertions": insertions,
        "deletions": deletions,
        "lines": insertions + deletions,
        "subsystems": list(set(classify_file(f) for f in files))
    }

def main():
    # Load PR data
    with open("/tmp/prs_page1.json") as f:
        prs = json.load(f)
    
    all_stats = {}
    file_to_prs = defaultdict(list)
    
    for pr in prs:
        num = pr["number"]
        diff = get_pr_diff(num)
        stats = get_pr_stats(diff)
        
        all_stats[num] = {
            "title": pr["title"],
            "author": pr["user"]["login"],
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "body": pr.get("body", "")[:500],
            "files": stats["files"],
            "insertions": stats["insertions"],
            "deletions": stats["deletions"],
            "lines": stats["lines"],
            "subsystems": stats["subsystems"],
            "labels": [l["name"] for l in pr.get("labels", [])],
        }
        
        for f in stats["files"]:
            file_to_prs[f].append(num)
    
    # Save stats
    with open(AUDIT_DIR / "analysis/pr_stats.json", "w") as f:
        json.dump(all_stats, f, indent=2)
    
    # Save file-to-PRs mapping
    with open(AUDIT_DIR / "analysis/file_to_prs.json", "w") as f:
        # Only files touched by multiple PRs (conflicts)
        conflicts = {k: v for k, v in file_to_prs.items() if len(v) > 1}
        json.dump(conflicts, f, indent=2)
    
    # Print summary
    print(f"Analyzed {len(all_stats)} PRs")
    print(f"Files touched by multiple PRs: {len(conflicts)}")
    
    # Print subsystem distribution
    subsystem_counts = defaultdict(int)
    for num, stats in all_stats.items():
        for s in stats["subsystems"]:
            subsystem_counts[s] += 1
    
    print("\nPRs by subsystem:")
    for s, c in sorted(subsystem_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")
    
    # Print conflict details
    if conflicts:
        print("\nConflicting files (touched by multiple PRs):")
        for f, nums in sorted(conflicts.items()):
            print(f"  {f}: PRs {nums}")

if __name__ == "__main__":
    main()
