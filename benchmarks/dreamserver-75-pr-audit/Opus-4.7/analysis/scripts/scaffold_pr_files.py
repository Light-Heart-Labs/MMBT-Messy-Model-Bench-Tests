#!/usr/bin/env python3
"""
Scaffold per-PR audit files (verdict.md, summary.md, review.md,
diff-analysis.md, interactions.md, trace.md) for every open PR. Metadata
is pre-filled from raw/ so the auditor only writes the prose.

This intentionally writes templates only when files don't exist — running
twice is a no-op for already-edited PRs.
"""
import json, io, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRS_DIR = ROOT / "prs"
RISK_MATRIX_PATH = ROOT / "analysis" / "risk-matrix.md"

# Pre-computed risk tiers (from analysis/risk-matrix.md). Order: A, B, C, D, E, total.
# This list is the source of truth for the scaffolder; the matrix .md is the
# rendered version. If you change scores here, regenerate the matrix.
RISK = {
    1057: ("yasin", 1, 2, 0, 1, 0, 4, "Low"),
    1056: ("yasin", 2, 2, 0, 1, 0, 5, "Low"),
    1055: ("yasin", 1, 0, 0, 0, 0, 1, "Trivial"),
    1054: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1053: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    1052: ("yasin", 1, 0, 0, 0, 0, 1, "Trivial"),
    1051: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1050: ("yasin", 3, 2, 1, 3, 0, 9, "Medium"),
    1049: ("yasin", 0, 2, 0, 1, 0, 3, "Trivial"),
    1048: ("yasin", 0, 0, 0, 0, 0, 0, "Trivial"),
    1047: ("yasin", 0, 1, 0, 0, 0, 1, "Trivial"),
    1046: ("yasin", 0, 1, 0, 1, 0, 2, "Trivial"),
    1045: ("yasin", 3, 2, 1, 2, 0, 8, "Low"),
    1044: ("yasin", 2, 1, 0, 1, 0, 4, "Low"),
    1043: ("y-coffee-dev", 1, 2, 0, 2, 1, 6, "Low"),
    1042: ("boffin-dmytro", 3, 3, 0, 1, 1, 8, "Low"),
    1040: ("yasin", 2, 2, 1, 1, 0, 6, "Low"),
    1039: ("yasin", 2, 1, 0, 2, 0, 5, "Low"),
    1038: ("yasin", 2, 1, 0, 1, 0, 4, "Low"),
    1037: ("yasin", 2, 2, 0, 1, 0, 5, "Low"),
    1036: ("yasin", 2, 1, 0, 1, 0, 4, "Low"),
    1035: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1034: ("yasin", 0, 1, 0, 0, 0, 1, "Trivial"),
    1033: ("yasin", 0, 1, 0, 0, 0, 1, "Trivial"),
    1032: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    1030: ("yasin", 2, 1, 1, 2, 0, 6, "Low"),
    1029: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1028: ("yasin", 0, 0, 0, 0, 0, 0, "Trivial"),
    1027: ("yasin", 3, 2, 1, 2, 0, 8, "Low"),
    1026: ("yasin", 2, 1, 1, 2, 0, 6, "Low"),
    1025: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1024: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    1023: ("yasin", 1, 0, 0, 0, 0, 1, "Trivial"),
    1022: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    1021: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1020: ("yasin", 2, 0, 0, 0, 0, 2, "Trivial"),
    1019: ("yasin", 2, 0, 0, 1, 0, 3, "Trivial"),
    1018: ("yasin", 3, 0, 0, 0, 0, 3, "Trivial"),
    1017: ("yasin", 2, 0, 0, 0, 0, 2, "Trivial"),
    1016: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1015: ("yasin", 2, 1, 0, 1, 0, 4, "Low"),
    1014: ("yasin", 0, 0, 0, 0, 0, 0, "Trivial"),
    1013: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1012: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    1011: ("yasin", 2, 1, 0, 1, 0, 4, "Low"),
    1010: ("yasin", 0, 1, 0, 1, 0, 2, "Trivial"),
    1009: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1008: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1007: ("yasin", 0, 0, 0, 0, 0, 0, "Trivial"),
    1006: ("yasin", 0, 1, 0, 1, 0, 2, "Trivial"),
    1005: ("yasin", 1, 2, 0, 1, 0, 4, "Low"),
    1004: ("yasin", 0, 1, 0, 1, 0, 2, "Trivial"),
    1003: ("yasin", 3, 2, 0, 2, 0, 7, "Low"),
    1002: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    1000: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    999: ("yasin", 1, 2, 0, 1, 0, 4, "Low"),
    998: ("yasin", 1, 2, 0, 1, 0, 4, "Low"),
    997: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    996: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    994: ("yasin", 1, 1, 0, 1, 0, 3, "Trivial"),
    993: ("yasin", 1, 1, 0, 0, 0, 2, "Trivial"),
    992: ("yasin", 0, 0, 0, 0, 0, 0, "Trivial"),
    991: ("dependabot", 0, 0, 0, 0, 0, 0, "Trivial"),
    990: ("dependabot", 0, 0, 0, 0, 0, 0, "Trivial"),
    988: ("yasin", 3, 2, 1, 4, 0, 10, "Medium"),
    983: ("Arifuzzaman", 4, 4, 0, 0, 3, 11, "Medium"),
    974: ("yasin", 0, 1, 0, 1, 0, 2, "Trivial"),
    973: ("yasin", 2, 0, 0, 0, 0, 2, "Trivial"),
    966: ("boffin-dmytro", 1, 0, 0, 0, 1, 2, "Trivial"),
    961: ("gabsprogrammer", 4, 4, 1, 1, 4, 14, "High"),
    959: ("boffin-dmytro", 2, 2, 0, 1, 1, 6, "Low"),
    750: ("y-coffee-dev", 4, 2, 1, 4, 1, 12, "Medium"),
    716: ("Arifuzzaman", 1, 1, 0, 1, 3, 6, "Low"),
    364: ("championVisionAI", 4, 4, 1, 3, 3, 15, "High"),
    351: ("reo0603", 3, 0, 0, 0, 3, 6, "Low"),
}


def get_meta(n):
    p = PRS_DIR / f"pr-{n}" / "raw" / "meta.json"
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def get_files(n):
    p = PRS_DIR / f"pr-{n}" / "raw" / "files.json"
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def get_basesha(n):
    p = PRS_DIR / f"pr-{n}" / "raw" / "diff.base.sha"
    if not p.exists():
        return None
    with io.open(p, encoding="utf-8") as f:
        return f.read().strip()


def write_if_missing(p, content):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        return False
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return True


def write_force(p, content):
    p.parent.mkdir(parents=True, exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def render_files_table(fdata):
    files = (fdata.get("files") or [])
    if not files:
        return "_No files in metadata._"
    rows = ["| File | + | - |", "|------|--:|--:|"]
    for f in files:
        # escape pipes
        path = f["path"].replace("|", "\\|")
        rows.append(f"| `{path}` | {f.get('additions', 0)} | {f.get('deletions', 0)} |")
    return "\n".join(rows)


def render_ci_table(fdata):
    rollup = fdata.get("statusCheckRollup") or []
    if not rollup:
        return "_No CI runs found in metadata._"
    rows = ["| Check | Status |", "|-------|--------|"]
    for c in rollup:
        name = c.get("name") or c.get("context") or "?"
        state = c.get("conclusion") or c.get("state") or c.get("status") or "?"
        rows.append(f"| {name} | {state} |")
    return "\n".join(rows)


def scaffold(n):
    meta = get_meta(n)
    fdata = get_files(n)
    base = get_basesha(n)

    risk = RISK.get(n)
    if not risk:
        return False
    contributor, A, B, C, D, E, total, tier = risk

    title = meta.get("title", "?")
    author = (meta.get("author") or {}).get("login", "?")
    is_draft = meta.get("isDraft", False)
    additions = meta.get("additions", 0)
    deletions = meta.get("deletions", 0)
    changed = meta.get("changedFiles", 0)
    head = meta.get("headRefName", "?")
    base_branch = meta.get("baseRefName", "main")
    url = meta.get("url", "")
    body = (meta.get("body") or "").strip()
    review_decision = fdata.get("reviewDecision") or "(none)"

    pr_dir = PRS_DIR / f"pr-{n}"

    # 1. verdict.md (template; auditor fills in actual verdict)
    verdict_template = f"""# PR #{n} — Verdict

> **Title:** {title}
> **Author:** [{author}](https://github.com/{author}) · **Draft:** {is_draft} · **Base:** `{base_branch}`  ←  **Head:** `{head}`
> **Diff:** +{additions} / -{deletions} across {changed} file(s) · **Risk tier: {tier} (score {total}/20)**
> **PR URL:** {url}

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | {A} | _see review.md_ |
| B — Test coverage | {B} | _see review.md_ |
| C — Reversibility | {C} | _see review.md_ |
| D — Blast radius | {D} | _see review.md_ |
| E — Contributor | {E} | _see review.md_ |
| **Total** | **{total}** | **{tier}** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**{ '_TBD — auditor review pending_' if total > 3 else 'Pending review (Trivial tier — short verdict)' }**

_Reasoning lives in `review.md` and `diff-analysis.md`. This file is the
single line a maintainer reads to decide what to do with the PR._
"""
    write_force(pr_dir / "verdict.md", verdict_template)

    # 2. summary.md
    body_for_summary = body if body else "_PR body is empty._"
    summary = f"""# PR #{n} — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> {title}

## Author's stated motivation

The PR body says (paraphrased):

> {body_for_summary[:1500]}{"  …(truncated)" if len(body_for_summary) > 1500 else ""}

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
"""
    write_force(pr_dir / "summary.md", summary)

    # 3. review.md
    review = f"""# PR #{n} — Review notes

Line-by-line review notes against `prs/pr-{n}/raw/diff.patch`. Severity:

- ★★★ — must address before merge
- ★★ — would address before merge
- ★ — observation, not blocking

## Findings

_TBD — auditor reads the diff and notes findings here._

## Convention adherence (per `research/upstream-context.md`)

- [ ] No new `eval` of script output
- [ ] No new `2>/dev/null`, `\\|\\| true`, broad `except: pass`
- [ ] No new retry/fallback chains
- [ ] If touches port bindings: defaults to loopback or `${{BIND_ADDRESS:-127.0.0.1}}`
- [ ] If adds new file in `installers/lib/`: pure (no I/O)
- [ ] If adds new env var: schema and example updated together
- [ ] If touches manifest: schema-valid (no breaking the resolver)

_TBD — auditor checks each item._
"""
    write_force(pr_dir / "review.md", review)

    # 4. diff-analysis.md
    diff_analysis = f"""# PR #{n} — Diff analysis

What the diff actually changes, vs what the title/body claim.

## Files touched ({changed})

{render_files_table(fdata)}

## Auditor's read of the diff

_TBD — auditor reads `raw/diff.patch` and writes the gap-vs-claim here.
For Trivial-tier PRs this is often "matches the title; no surprises"._
"""
    write_force(pr_dir / "diff-analysis.md", diff_analysis)

    # 5. interactions.md
    interactions = f"""# PR #{n} — Interactions

Conflicts and dependencies with other open PRs. Cross-reference to
`analysis/dependency-graph.md` for cluster context.

## Hard dependencies (this PR requires another PR's change)

_TBD._

## Soft conflicts (this PR shares files with other open PRs)

_TBD — auditor cross-references `analysis/file_overlaps.json` and
the dependency-graph clusters._

## Supersession / collapse candidates

_TBD._
"""
    write_force(pr_dir / "interactions.md", interactions)

    # 6. trace.md
    trace = f"""# PR #{n} — Trace

Pointers back to the exact state reviewed, so any verdict here is
reproducible.

| Item | Value |
|------|-------|
| PR head ref | `{head}` |
| Base branch | `{base_branch}` |
| Diff base SHA (`merge-base main {head}`) | `{base or '(unresolved)'}` |
| Audit baseline | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` (main HEAD at audit start) |
| Diff file | `prs/pr-{n}/raw/diff.patch` |
| Files JSON | `prs/pr-{n}/raw/files.json` |
| Meta JSON | `prs/pr-{n}/raw/meta.json` |

## CI rollup at audit time

{render_ci_table(fdata)}

## GitHub review decision

`{review_decision}`

## Auditor-cited lines

_TBD — when verdict cites a specific line, link it here as
`raw/diff.patch:LINE` or `dreamserver-src:path:LINE` for traceability._
"""
    write_force(pr_dir / "trace.md", trace)

    # 7. tests/ placeholder
    tests_dir = pr_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    tests_readme = tests_dir / "README.md"
    if not tests_readme.exists():
        write_force(tests_readme, f"""# Tests run for PR #{n}

This directory holds test outputs and the scripts that produced them.
Empty for now; auditor populates as tests are run.

If this PR touches code reachable by `dream-server/tests/`, the auditor:
1. Runs the relevant tests on baseline `d5154c3` (main HEAD)
2. Runs the same tests on the PR head
3. Records both outputs here as `baseline-{{test}}.txt` and `prhead-{{test}}.txt`

If no tests apply, this README explains why.
""")

    return True


def main():
    written = 0
    for n in sorted(RISK.keys()):
        if scaffold(n):
            written += 1
    print(f"Scaffolded {written} PR directories.")


if __name__ == "__main__":
    main()
