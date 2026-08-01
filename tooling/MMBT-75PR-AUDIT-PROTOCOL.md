# MMBT DreamServer frozen-75-PR audit protocol

This protocol preserves the historical deliverable gate while adding a
reproducible substantive overlay. It grades the audit produced by the model;
it does not grade whether the underlying PR author ultimately deserves a
bounty or whether a maintainer later chooses a different disposition.

## Authoritative subject

- Frozen capture date: 2026-04-27.
- Baseline: `Light-Heart-Labs/DreamServer` commit `d5154c3`.
- Canonical set: the 75 PR numbers in `canonical-prs.txt`, SHA-256
  `569b95b3384af0c4ae4b54a2c8c8f7c908b396124777927a37b5c8fa0211ecd1`.
- The exact same 75-number set is present in the historical Qwen3.6-27B-AWQ,
  GPT-5.5, and Opus-4.7 artifacts.
- Frozen per-PR diffs and file lists are source evidence. Current live PR
  state is optional context and may not replace the frozen subject.

## Historical/legacy shipped gate

- Harness ends with `done_signal`.
- A clean final Git commit has the required release tag.
- Exactly the canonical 75 `/prs/pr-{number}/` directories exist.
- All required top-level report, analysis, testing, research, decision,
  source, tool-log, and README artifacts exist.
- Every PR directory has non-empty verdict, summary, review, diff-analysis,
  interactions, trace, and test-evidence artifacts.
- Receipt, transcript, summary, cost, telemetry, and a valid final workspace
  archive are preserved.

## Substantive checks

- Every PR has exactly one merge/revise/reject disposition. Revise and reject
  reasons use the prompt taxonomy and give actionable guidance.
- Verdict totals reconcile to 75 everywhere they are reported.
- Trace and review files cite frozen-diff paths/hunks, test evidence, or
  pinned-baseline architecture—not merely the PR title/body.
- Every test-reachable code PR records baseline and patched results. A skip is
  acceptable only when explicit, scoped, and justified. Claimed bug fixes have
  a baseline reproduction or a recorded failed reproduction that affects the
  verdict.
- The frozen `files.txt` files are baseline-to-capture-tree lists, not always
  PR-owned file lists. For stale branches they contain reverse-drift: files
  changed on main after the PR branched. The audit must reconcile each list to
  metadata `changedFiles`, document the mismatch, and must not mislabel drift
  as a PR conflict. The independent overlay reports raw overlap coverage for
  corpus traceability, hard-checks overlap pairs among high-confidence lists
  whose file counts reconcile to metadata, and separately assesses recovered
  clean-diff/semantic dependencies.
- The risk matrix documents all requested axes and contains all 75 PRs.
- Surface-area analysis covers all 75 PRs. Contributor notes cover every
  contributor and cite representative PRs/patterns; they need not repeat every
  PR number. Bounty tier/absence and AMD relevance are explicit rather than
  inferred silently.
- The executive summary is at most three pages in substance and reconciles
  counts, top priorities, high-risk situations, dependency hot spots, and AMD
  implications to the detailed artifacts.
- Reproduction/test commands are actually present and rerunnable; prose that
  merely repeats an author's testing claim is not execution evidence.
- A verdict's link to `/tests/` is not evidence when that directory is empty.
  Every PR needs a non-empty executed-test record or a scoped, justified skip.
- Generic trace pointers to the baseline or a scripts directory are not
  line-level traceability. Review/trace artifacts must name a source file,
  frozen diff, hunk, or equivalent inspectable location.
- Each verdict declares one actual bounty tier (or explicitly none/unknown);
  a pointer to a general Small/Medium/Large mapping is not a declaration.
- Boilerplate or programmatically cloned prose is not mistaken for 75 real
  reviews. Depth may be risk-tiered, but each disposition must be grounded in
  the individual frozen diff.

## Classification

- `SUBSTANTIVE_PASS`: legacy-shipped, exact frozen scope, structurally
  complete, internally reconciled, and sufficiently evidenced to act on.
- `SHIPPED_WITH_MATERIAL_AUDIT_DEFECTS`: ships the requested shape but has a
  material evidence, test, trace, dependency, or reconciliation defect.
- `SCAFFOLD_AND_STOP`: creates nominal coverage but most PRs lack individual
  review/test substance.
- `MODEL_TERMINAL_FAILURE`: malformed tool call, unparsed tool syntax,
  scroll loop, context/API termination, or other model-attributable stop.
- `INFRASTRUCTURE_INVALID`: moving upstream, missing fixture, endpoint outage,
  sandbox/harness failure, or another non-model condition invalidates the run.

Historical Qwen3.6's published `scaffold-and-stop` label remains unchanged:
75 verdict files existed, but only three were real reviews and no required
tests or reproductions were run. The stricter overlay is a separate axis for
all models until historical artifacts are uniformly regraded.
