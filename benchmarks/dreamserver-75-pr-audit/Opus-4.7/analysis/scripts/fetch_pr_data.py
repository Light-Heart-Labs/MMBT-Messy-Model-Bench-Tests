#!/usr/bin/env python3
"""
Fetch per-PR metadata and write to prs/pr-{N}/raw/ directories.

For each open PR:
  - raw/meta.json    (title, author, body, base, head, additions/deletions, etc.)
  - raw/files.json   (files changed with +/-)
  - raw/checks.json  (status check rollup)
  - raw/diff.patch   (full diff against the PR's base ref)

Reads prs-full.json (already-fetched list from `gh pr list`) and uses the
local DreamServer clone (../dreamserver-src) for diffs to avoid extra API
calls. The PR refs were fetched into refs/remotes/origin/pr/<N>.
"""
import json, os, subprocess, sys, io, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT.parent / "dreamserver-src"
PRS_JSON = ROOT / "prs-full.json"
PRS_DIR = ROOT / "prs"

def sh(cmd, cwd=None, check=True, capture=True):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                       capture_output=capture, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.stderr.write(f"FAIL {cmd}\n{r.stderr}\n")
        return None
    return r

def main():
    with io.open(PRS_JSON, encoding="utf-8") as f:
        prs = json.load(f)

    print(f"Fetching per-PR data for {len(prs)} PRs...")
    for i, pr in enumerate(prs, 1):
        n = pr["number"]
        d = PRS_DIR / f"pr-{n}" / "raw"
        d.mkdir(parents=True, exist_ok=True)

        # 1. meta.json — drop the body keys we don't need to keep small
        with io.open(d / "meta.json", "w", encoding="utf-8") as f:
            json.dump(pr, f, indent=2)

        # 2. files.json via gh
        if not (d / "files.json").exists():
            r = sh(["gh", "pr", "view", str(n), "--repo", "Light-Heart-Labs/DreamServer",
                    "--json", "files,reviewDecision,statusCheckRollup,reviewRequests,reviews,closingIssuesReferences"])
            if r:
                with io.open(d / "files.json", "w", encoding="utf-8") as f:
                    f.write(r.stdout)

        # 3. diff.patch from local clone
        if not (d / "diff.patch").exists():
            base_sha = sh(["git", "merge-base", "main", f"origin/pr/{n}"], cwd=SRC, check=False)
            if base_sha and base_sha.returncode == 0:
                bs = base_sha.stdout.strip()
                r = sh(["git", "diff", f"{bs}...origin/pr/{n}"], cwd=SRC, capture=True, check=False)
                if r and r.returncode == 0:
                    with io.open(d / "diff.patch", "w", encoding="utf-8", newline='\n') as f:
                        f.write(r.stdout)
                    with io.open(d / "diff.base.sha", "w", encoding="utf-8") as f:
                        f.write(bs + "\n")

        # 4. diff stat summary
        if not (d / "diff.stat").exists() and (d / "diff.base.sha").exists():
            with io.open(d / "diff.base.sha", encoding="utf-8") as f:
                bs = f.read().strip()
            r = sh(["git", "diff", "--stat", f"{bs}...origin/pr/{n}"], cwd=SRC, capture=True, check=False)
            if r and r.returncode == 0:
                with io.open(d / "diff.stat", "w", encoding="utf-8") as f:
                    f.write(r.stdout)

        if i % 10 == 0:
            print(f"  {i}/{len(prs)} done")

    print("Done.")

if __name__ == "__main__":
    main()
