#!/usr/bin/env python3
"""
Cluster open PRs by subsystem (path-based) and identify file-level overlaps
between PRs. Output:

  analysis/cluster_summary.json   PR -> subsystem classification + file list
  analysis/file_overlaps.json     File path -> list of PRs touching it
  analysis/contributor_summary.json  Contributor -> PR list with stats
"""
import json, io, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRS_DIR = ROOT / "prs"
ANALYSIS = ROOT / "analysis"

# Subsystem heuristics — first match wins, in priority order.
# Tuned to DreamServer's tree layout (per ARCHITECTURE.md / CLAUDE.md).
SUBSYSTEM_RULES = [
    ("ci",                  re.compile(r"^\.github/")),
    ("installer-windows",   re.compile(r"dream-server/installers/windows/|installer/windows/|\.ps1$|install\.ps1")),
    ("installer-macos",     re.compile(r"dream-server/installers/macos/|installer/macos/|installers/macos\.sh")),
    ("installer-core",      re.compile(r"dream-server/installers/(lib|phases)/|install-core\.sh|^install\.sh$")),
    ("dream-cli",           re.compile(r"dream-server/dream-cli|^dream-cli")),
    ("dashboard-ui",        re.compile(r"dream-server/extensions/services/dashboard/")),
    ("dashboard-api",       re.compile(r"dream-server/extensions/services/dashboard-api/")),
    ("host-agent",          re.compile(r"host-agent|host_agent")),
    ("openclaw",            re.compile(r"openclaw")),
    ("langfuse",            re.compile(r"langfuse")),
    ("perplexica",          re.compile(r"perplexica")),
    ("searxng",             re.compile(r"searxng")),
    ("whisper-stt",         re.compile(r"whisper|stt")),
    ("tts",                 re.compile(r"\btts\b|kokoro")),
    ("comfyui",             re.compile(r"comfyui")),
    ("librechat",           re.compile(r"librechat")),
    ("anythingllm",         re.compile(r"anythingllm")),
    ("localai",             re.compile(r"localai")),
    ("continue",            re.compile(r"\bcontinue\b")),
    ("token-spy",           re.compile(r"token-spy|token_spy")),
    ("privacy-shield",      re.compile(r"privacy-shield|privacy_shield")),
    ("piper-audio",         re.compile(r"piper-audio|piper_audio")),
    ("milvus",              re.compile(r"milvus")),
    ("jupyter",             re.compile(r"jupyter")),
    ("compose-resolver",    re.compile(r"resolve-compose|scripts/resolve")),
    ("compose-base",        re.compile(r"docker-compose\.(base|nvidia|amd|apple|cpu)\.ya?ml")),
    ("manifests-extensions", re.compile(r"dream-server/extensions/services/[^/]+/manifest\.ya?ml")),
    ("compose-extensions",  re.compile(r"dream-server/extensions/services/[^/]+/compose")),
    ("scripts-shell",       re.compile(r"dream-server/scripts/")),
    ("env-schema",          re.compile(r"\.env\.schema|\.env\.example")),
    ("config-backends",     re.compile(r"dream-server/config/backends/")),
    ("config-other",        re.compile(r"dream-server/config/")),
    ("docs",                re.compile(r"\.md$|^docs/|/docs/|README")),
    ("tests",               re.compile(r"^tests?/|/tests?/|\.bats$")),
    ("resources",           re.compile(r"^resources/")),
    ("dependabot-actions",  re.compile(r"\.github/workflows/.*\.yml$")),
    ("other",               re.compile(r".*")),
]

def classify(path: str) -> str:
    for name, pat in SUBSYSTEM_RULES:
        if pat.search(path):
            return name
    return "other"

def main():
    cluster = {}
    file_to_prs = collections.defaultdict(list)
    contributors = collections.defaultdict(list)

    for prdir in sorted(PRS_DIR.glob("pr-*")):
        n = int(prdir.name.split("-")[1])
        meta_p = prdir / "raw" / "meta.json"
        files_p = prdir / "raw" / "files.json"
        if not meta_p.exists() or not files_p.exists():
            continue

        with io.open(meta_p, encoding="utf-8") as f:
            meta = json.load(f)
        with io.open(files_p, encoding="utf-8") as f:
            fdata = json.load(f)

        files = fdata.get("files") or []
        paths = [f["path"] for f in files]
        per_file_subsys = collections.Counter(classify(p) for p in paths)
        primary_sub = per_file_subsys.most_common(1)[0][0] if per_file_subsys else "other"
        all_subs = sorted(per_file_subsys.keys())

        author = (meta.get("author") or {}).get("login", "?")
        contributors[author].append({
            "n": n,
            "title": meta.get("title", ""),
            "additions": meta.get("additions", 0),
            "deletions": meta.get("deletions", 0),
            "changedFiles": meta.get("changedFiles", 0),
            "isDraft": meta.get("isDraft", False),
            "primary_sub": primary_sub,
        })

        cluster[n] = {
            "title": meta.get("title", ""),
            "author": author,
            "isDraft": meta.get("isDraft", False),
            "additions": meta.get("additions", 0),
            "deletions": meta.get("deletions", 0),
            "changedFiles": meta.get("changedFiles", 0),
            "createdAt": meta.get("createdAt"),
            "primary_sub": primary_sub,
            "all_subs": all_subs,
            "paths": paths,
            "review_decision": fdata.get("reviewDecision"),
            "ci": _ci_summary(fdata.get("statusCheckRollup")),
            "mergeable": meta.get("mergeable"),
            "url": meta.get("url"),
        }
        for p in paths:
            file_to_prs[p].append(n)

    # Filter file_to_prs to only files touched by 2+ PRs (the interesting ones)
    overlaps = {p: prs for p, prs in file_to_prs.items() if len(prs) >= 2}

    with io.open(ANALYSIS / "cluster_summary.json", "w", encoding="utf-8") as f:
        json.dump(cluster, f, indent=2)
    with io.open(ANALYSIS / "file_overlaps.json", "w", encoding="utf-8") as f:
        json.dump(overlaps, f, indent=2)
    with io.open(ANALYSIS / "contributor_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: sorted(v, key=lambda x: -x["n"]) for k, v in contributors.items()}, f, indent=2)

    # Print headline stats
    print(f"PRs classified: {len(cluster)}")
    sub_counter = collections.Counter(c["primary_sub"] for c in cluster.values())
    print("\nTop subsystems by PR count:")
    for s, c in sub_counter.most_common(20):
        print(f"  {c:3d}  {s}")
    print(f"\nFiles touched by 2+ PRs: {len(overlaps)}")
    print(f"Most-overlapping files (top 10):")
    for p, prs in sorted(overlaps.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {len(prs):3d}  {p}")
    print(f"\nContributors: {len(contributors)}")
    for author, prs in sorted(contributors.items(), key=lambda x: -len(x[1])):
        print(f"  {len(prs):3d}  {author}")


def _ci_summary(rollup):
    if not rollup:
        return None
    states = collections.Counter()
    for c in rollup:
        s = c.get("conclusion") or c.get("status") or c.get("state") or "?"
        states[s] += 1
    return dict(states)


if __name__ == "__main__":
    main()
