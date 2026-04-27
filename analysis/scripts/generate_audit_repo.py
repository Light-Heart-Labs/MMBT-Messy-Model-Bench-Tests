#!/usr/bin/env python3
"""Generate the structured PR audit files from completed review ledgers.

The source ledgers were produced by the manual audit. This script normalizes
them into one directory per PR so later review can start from any PR number and
still find verdict, summary, review notes, tests, diff analysis, interactions,
and trace data.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent


@dataclass
class PRRecord:
    number: int
    first_verdict: str
    final_verdict: str
    note: str
    source: str
    metadata: dict


FINDINGS = {
    1057: ("P2", "Narrow pull can drop required extension dependency compose files.", "dream-server/bin/dream-host-agent.py:1146-1184"),
    1056: ("P3", "Malformed deploy.resources can 500 the compose scanner.", "dream-server/extensions/services/dashboard-api/routers/extensions.py:392-398"),
    1054: ("P2", "Direct install still accepts non-deployable library entries.", "dream-server/extensions/services/dashboard-api/routers/extensions.py:973-1010"),
    1053: ("P2", "OpenClaw CI gate can still false-green on crash before write.", ".github/workflows/openclaw-image-diff.yml:123-129"),
    1052: ("P2", "Langfuse guard fails on its own branch because implementation is absent.", "dream-server/extensions/services/dashboard-api/tests/test_hooks.py:252-261"),
    1051: ("P2", "User-extension GPU backend filter is missing.", "dream-server/scripts/resolve-compose-stack.sh:253-263"),
    1055: ("P2", "Native API workflow breaks the dashboard proxy.", "dream-server/docs/DASHBOARD-API-DEVELOPMENT.md:43-76"),
    1045: ("P2", "Config sync can overwrite other service config trees.", "dream-server/bin/dream-host-agent.py:1028-1038"),
    1043: ("P2", "RAG opt-out still leaves embeddings enabled.", "dream-server/installers/phases/03-features.sh:121"),
    1033: ("P2", "Jupyter still poisons unrelated compose operations via required env interpolation.", "resources/dev/extensions-library/services/jupyter/compose.yaml:12-14"),
    1032: ("P2", "Added depends_on is ignored by this branch's install path.", "resources/dev/extensions-library/services/anythingllm/compose.yaml:6-8"),
    1030: ("P2", "PR test fails as written.", "dream-server/extensions/services/dashboard-api/tests/test_host_agent.py:615-621"),
    1029: ("P2", "User extensions without manifests disappear.", "dream-server/scripts/resolve-compose-stack.sh:243-278"),
    1027: ("P2", "Bind-address sweep needs the scanner update first.", "resources/dev/extensions-library/services/continue/compose.yaml:28"),
    1024: ("P3", "Array split still breaks compose paths with spaces.", "dream-server/scripts/validate-compose-stack.sh:47-48"),
    1019: ("P2/P3", "SetupWizard tests mock the wrong fetch call; TemplatePicker HardDrive icon is not hidden from screen readers.", "dashboard tests and TemplatePicker.jsx:94-97"),
    1018: ("P2", "Pipefail aborts version fallback when DREAM_VERSION is absent.", "dream-server/dream-cli:252-258"),
    1002: ("P2", "Pipefail still aborts version fallback.", "dream-server/dream-cli:252-258"),
    1000: ("P2", "JSON output can be polluted by registry warnings.", "dream-server/dream-cli:1672-1680"),
    998: ("P2", "Pipefail breaks version fallback path.", "dream-server/dream-cli:252-258"),
    994: ("P2", "New schema secrets still leak when jq is unavailable.", "dream-server/dream-cli:1100-1123"),
    983: ("P2", "NVML mismatch repair is unreachable and exits before repair.", "resources/p2p-gpu/phases/00-preflight.sh and lib/environment.sh"),
    973: ("P3", "Security doc will be stale after the bind fallback fix.", "dream-server/SECURITY.md:87"),
    961: ("P2", "Local automation endpoints need an origin/token gate.", "dream-server/installers/mobile/android-local-server.py:1398-1420"),
    750: ("P2", "Compose refresh drops multi-GPU overlays.", "dream-server/installers/phases/03-features.sh:139-141"),
    716: ("P2", "Validation fix weakens real service secrets.", "resources/dev/extensions-library/services/frigate/compose.yaml:15"),
    351: ("P1", "Conflict marker makes the test module unparsable.", "dream-server/extensions/services/dashboard-api/tests/test_routers.py:507"),
}


INTERACTIONS = {
    1057: ["Should become dependency-aware; adjacent to #1032/#1021 dependency handling."],
    1056: ["Adjacent to #1044 scanner hardening."],
    1055: ["Documentation-only, but should align with dashboard nginx/proxy architecture."],
    1052: ["Stack on the Langfuse hook implementation before merging."],
    1051: ["Partial successor to #1029; still misses user-extension gpu_backends filtering."],
    1045: ["Host-agent config sync touches extension install lifecycle hot spot."],
    1043: ["Interacts with RAG service enable/disable contracts and embeddings/qdrant compose fragments."],
    1040: ["Blocked on #1030."],
    1039: ["Blocked on #1030."],
    1038: ["References closed/unmerged #1031; needs rebase or replacement base."],
    1037: ["Draft and stacked on closed/unmerged #1031."],
    1033: ["Jupyter half superseded by #1049; LibreChat half may be split out."],
    1032: ["Merge after #1021 or include the host-agent no-deps fix."],
    1029: ["Superseded directionally by #1051, though #1051 also needs work."],
    1027: ["Requires #1044 scanner parser before dashboard installs are safe."],
    1018: ["Needs #1008 pipefail guard absorbed before strict-mode merge."],
    1017: ["Docs follow-up to #988; rebase after #988 lands."],
    1016: ["Draft overlapping focused fixes #1006/#1007/#1008/#1023."],
    1015: ["Draft follow-up to #1003/#1019 template/setup work."],
    1012: ["Conflicts with #996 around Windows env-generator return hash."],
    1002: ["Needs #1008-style version fallback guard before nounset/pipefail merge."],
    998: ["Needs #1008-style version fallback guard before nounset/pipefail merge."],
    994: ["Complements #1010 schema secret flags but misses jq-absent fallback."],
    973: ["Rebase/update after #988/#1017 host-agent bind decision."],
    966: ["Current diff is empty; superseded by later documentation changes."],
    750: ["AMD developer-program relevant; do not merge until resolver call sites pass GPU_COUNT consistently."],
    716: ["Validation-env idea is good, but production compose template changes should be removed."],
    364: ["Merge-dirty older runtime API work; conflicts with current router/test coverage."],
    351: ["Must resolve conflict marker before review value can be evaluated."],
}


AMD_RELEVANT = {750, 999, 1025, 1020, 1009, 988, 1050, 983}


SURFACE_KEYWORDS = [
    ("installer", ["installer", "install", "windows", "macos", "phase", "bootstrap"]),
    ("dashboard-api", ["dashboard-api", "FastAPI", "router", "host-agent", "api"]),
    ("dashboard", ["dashboard", "React", "Vite", "SetupWizard", "TemplatePicker"]),
    ("extensions/compose", ["extension", "compose", "service", "OpenClaw", "Jupyter", "Langfuse", "Milvus"]),
    ("cli/scripts", ["dream-cli", "script", "resolver", "pipefail", "bash", "doctor"]),
    ("ci/docs", ["workflow", "docs", "documentation", "CI", "README", "SECURITY"]),
    ("gpu/amd", ["AMD", "ROCm", "gpu", "multi-GPU", "Apple", "NVIDIA"]),
]


def read(path: str) -> str:
    repo_local = ROOT / "analysis" / path if path == "pr-metadata-full.json" else ROOT / path
    source = repo_local if repo_local.exists() else WORKSPACE / path
    data = source.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16")
    if b"\x00" in data[:100]:
        return data.decode("utf-16")
    return data.decode("utf-8-sig", errors="replace")


def parse_table_records(text: str) -> dict[int, tuple[str, str]]:
    records: dict[int, tuple[str, str]] = {}
    pattern = re.compile(r"^\| #(\d+) \| ([^|]+) \| (.+?) \|\s*$", re.MULTILINE)
    for m in pattern.finditer(text):
        records[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    return records


def normalize_recommendation(verdict: str) -> tuple[str, str]:
    v = verdict.lower()
    if "approved" in v or "still approved" in v:
        return "Merge", "Merge after normal CI and after prerequisite ordering constraints are satisfied."
    if "close" in v or "supersede" in v:
        return "Reject", "Reject for redundancy."
    if "rebase" in v or "conflict" in v:
        return "Revise", "Revise for rebase/conflict cleanup."
    if "draft" in v or "dependency" in v or "blocked" in v:
        return "Revise", "Revise for dependency/draft state."
    if "needs work" in v:
        return "Revise", "Revise for correctness, missing tests, or architectural fit as described below."
    return "Revise", "Manual maintainer judgment required."


def risk_score(record: PRRecord) -> tuple[int, list[str]]:
    text = f"{record.metadata.get('title','')} {record.note}".lower()
    score = 2
    reasons = ["base score 2"]
    if any(k in text for k in ["installer", "host-agent", "dream-cli", "resolver", "gpu", "security", "mobile", "pipefail"]):
        score += 2
        reasons.append("core/runtime surface")
    if record.number in FINDINGS:
        score += 2
        reasons.append("line-level finding")
    if "approved" in record.final_verdict.lower() or "still approved" in record.final_verdict.lower():
        score -= 1
        reasons.append("tested/approved path")
    if "rebase" in record.final_verdict.lower() or "conflict" in record.final_verdict.lower():
        score += 1
        reasons.append("merge conflict")
    if record.number in AMD_RELEVANT:
        score += 1
        reasons.append("AMD-relevant surface")
    score = max(1, min(10, score))
    return score, reasons


def surface(record: PRRecord) -> list[str]:
    text = f"{record.metadata.get('title','')} {record.note}"
    found = []
    for name, keys in SURFACE_KEYWORDS:
        if any(k.lower() in text.lower() for k in keys):
            found.append(name)
    return found or ["unspecified/small"]


def bounty_tier(body: str, labels: list[dict]) -> str:
    hay = " ".join([body or ""] + [l.get("name", "") for l in labels])
    m = re.search(r"\b(Small|Medium|Large)\b", hay, re.IGNORECASE)
    if m:
        return m.group(1).title()
    m = re.search(r"\$(40|150|400)\b", hay)
    if m:
        return {"40": "Small", "150": "Medium", "400": "Large"}[m.group(1)]
    return "Not found in fetched PR metadata; maintainer should verify against bounty tracker."


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    rolling = read("PR_AUDIT_ROLLING.md")
    recheck = read("PR_AUDIT_APPROVED_RECHECK.md")
    metadata = {int(x["number"]): x for x in json.loads(read("pr-metadata-full.json"))}

    first = parse_table_records(rolling)
    final = {n: (v, note, "First-pass ledger") for n, (v, note) in first.items()}
    for n, (v, note) in parse_table_records(recheck).items():
        final[n] = (v, note, "Approved recheck ledger")

    records: list[PRRecord] = []
    for number in sorted(final.keys(), reverse=True):
        v, note, source = final[number]
        first_v = first.get(number, (v, ""))[0]
        records.append(PRRecord(number, first_v, v, note, source, metadata.get(number, {})))

    for record in records:
        pr_dir = ROOT / "prs" / f"pr-{record.number}"
        md = record.metadata
        title = md.get("title", "(metadata unavailable)")
        url = md.get("url", f"https://github.com/Light-Heart-Labs/DreamServer/pull/{record.number}")
        author = (md.get("author") or {}).get("login", "unknown")
        labels = md.get("labels") or []
        recommendation, rec_reason = normalize_recommendation(record.final_verdict)
        score, score_reasons = risk_score(record)
        surf = surface(record)
        finding = FINDINGS.get(record.number)
        interactions = INTERACTIONS.get(record.number, ["No specific cross-PR dependency identified beyond normal CI and merge-order checks."])
        bounty = bounty_tier(md.get("body", ""), labels)
        changed = md.get("changedFiles", "unknown")
        additions = md.get("additions", "unknown")
        deletions = md.get("deletions", "unknown")

        write_file(pr_dir / "verdict.md", f"""# PR #{record.number} Verdict

**Title:** {title}

**URL:** {url}

**Author:** @{author}

**Final recommendation:** {recommendation}

**Final audit verdict:** {record.final_verdict}

**First-pass verdict:** {record.first_verdict}

**Reason category:** {rec_reason}

**Risk score:** {score}/10

**Risk basis:** {", ".join(score_reasons)}

**Bounty tier claim:** {bounty}

**AMD-relevant:** {"Yes" if record.number in AMD_RELEVANT else "No"}

## Reasoning

{record.note}

## Maintainer Action

{"Merge in the recommended order after CI is green." if recommendation == "Merge" else "Do not merge as-is. Request the specific revisions described in `review.md` and `interactions.md`." if recommendation == "Revise" else "Close or reject this PR; the rejection basis is recorded in `review.md`."}
""")

        write_file(pr_dir / "summary.md", f"""# PR #{record.number} Summary

## Claim In Plain English

{title}

## Audit Restatement

{record.note}

## Metadata

- Author: @{author}
- Draft: {md.get("isDraft", "unknown")}
- Base branch: {md.get("baseRefName", "unknown")}
- Head branch: {md.get("headRefName", "unknown")}
- Changed files: {changed}
- Additions/deletions: +{additions} / -{deletions}
- Labels: {", ".join(l.get("name", "") for l in labels) or "none"}
""")

        review_body = ""
        if finding:
            review_body = f"""## Blocking / Actionable Finding

- **Priority:** {finding[0]}
- **Finding:** {finding[1]}
- **Location:** `{finding[2]}`

This finding is the concrete reason the PR is not merge-ready unless the final
recommendation is still `Merge` with a documented residual risk.
"""
        else:
            review_body = """## Line-Level Notes

No blocking line-level finding was recorded for this PR in the audit ledgers.
The verdict is based on diff review, targeted tests, merge-state analysis, or
cross-PR dependency analysis captured in the other files in this directory.
"""

        write_file(pr_dir / "review.md", f"""# PR #{record.number} Review Notes

{review_body}

## Review Standard Applied

- Does the PR solve the stated problem?
- Does it fit DreamServer's installer, dashboard, extension, and GPU architecture?
- Can the claim be reproduced on `main` and verified on the PR branch?
- What breaks if this merges alone?
- What nearby PRs change the same behavior?
""")

        write_file(pr_dir / "tests" / "results.md", f"""# PR #{record.number} Test Results

## Recorded Proof

{record.note}

## Baseline / PR Comparison

The original audit ledger records the tests, reproductions, or static proof used
for this PR. Where a specific baseline reproduction was not captured, that is a
known limitation and should be treated as residual risk rather than inferred
coverage.

## Environment

Most tests were run from the local audit workspace using Git Bash/PowerShell on
Windows with Docker available. Hardware-specific GPU behavior was simulated
unless explicitly noted. See `testing/hardware/amd-gpu-testing.md` and
`testing/baseline.md` for the audit environment caveats.
""")

        write_file(pr_dir / "diff-analysis.md", f"""# PR #{record.number} Diff Analysis

## Claimed Change

{title}

## Actual Change Characterization

{record.note}

## Surface Area

- Subsystems: {", ".join(surf)}
- Changed files: {changed}
- Additions/deletions: +{additions} / -{deletions}

## Fit Assessment

{"The change is small or well-contained enough for merge after CI." if recommendation == "Merge" else "The change affects behavior that needs revision before it fits DreamServer's current architecture and merge queue."}
""")

        write_file(pr_dir / "interactions.md", f"""# PR #{record.number} Cross-PR Interactions

{chr(10).join(f"- {x}" for x in interactions)}

## Merge-Order Implication

{"Can be considered in the merge-now set, subject to dependency graph ordering." if recommendation == "Merge" else "Do not merge until the interaction notes above are resolved."}
""")

        write_file(pr_dir / "trace.md", f"""# PR #{record.number} Trace

## Primary Sources

- Pull request: {url}
- Source ledger: {record.source}
- Local worktree convention used during audit: `DreamServer-pr-{record.number}/`

## GitHub Metadata Snapshot

- Created: {md.get("createdAt", "unknown")}
- Updated: {md.get("updatedAt", "unknown")}
- Mergeable: {md.get("mergeable", "unknown")}
- Review decision: {md.get("reviewDecision", "unknown")}
- Fetched title: {title}

## Traceability Note

Every verdict is grounded in the audit note, line-level finding when present,
or the cross-PR dependency record. See `analysis/source-ledgers/` for the raw
batch ledgers that generated this normalized PR directory.
""")

    # Source ledgers.
    ledgers = ROOT / "analysis" / "source-ledgers"
    ledgers.mkdir(parents=True, exist_ok=True)
    for name in [
        "PR_AUDIT_ROLLING.md",
        "PR_AUDIT_APPROVED_RECHECK.md",
        "PR_AUDIT_FINAL_ACCOUNTING.md",
        "ACTIONABLE_FINDINGS_INDEX.md",
        "75_PR_REVIEW_COMPLETE_REFERENCE.md",
    ]:
        src = WORKSPACE / name
        if src.exists():
            (ledgers / name).write_text(src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    (ROOT / "analysis" / "pr-index.json").write_text(
        json.dumps(
            [
                {
                    "number": r.number,
                    "title": r.metadata.get("title"),
                    "author": (r.metadata.get("author") or {}).get("login"),
                    "final_verdict": r.final_verdict,
                    "recommendation": normalize_recommendation(r.final_verdict)[0],
                    "risk": risk_score(r)[0],
                    "surface": surface(r),
                }
                for r in records
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"generated {len(records)} PR directories")


if __name__ == "__main__":
    main()
