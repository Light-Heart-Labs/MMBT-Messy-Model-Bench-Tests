# Gemma 4 extended-suite substantive audit protocol

This protocol is fixed before any Gemma extended-suite output exists. It keeps
the historical artifact/finish gates, adds the same strict overlays applied to
DeepSeek V4 Flash, and never converts “files exist” into a quality pass.

## Common evidence gate

Every run first passes `tooling/audit_gemma4_extended.py`: exact model/runtime,
task and subject hashes, model-card sampling, native context/output policy,
deterministic replica lane, 500 W limits, telemetry, dependency lineage, clean
tagged archive, and attempt preservation. Raw archives and grades remain
immutable. Substantive corrections are separate overlays tied to archive and
grader hashes; no model rerun can replace an unfavorable valid attempt.

A missing deliverable, early stop, malformed tool use, length exhaustion at the
genuine dynamic context allowance, scroll loop, or wrong audited subject after
the pinned refs were available is a model outcome. Only affirmative endpoint,
fixture, network-before-subject-fetch, or harness evidence can make an attempt
infrastructure-invalid.

## Single DreamServer PR #1057

- Audit the immutable subject in `gemma4-single-pr-subject-pin.json`: base
  `309e9cd0`, head `e5ceb43e`, squash `1678f194`, and the original PR commits.
  The stale word “open” and current `main` cannot redefine the subject.
- Require the complete requested repository structure, meaningful commit
  history, final tag, explicit bounty/AMD/risk treatment, line-level traces,
  tool log, questions, dead ends, decisions, and rerunnable evidence.
- Reproduce applicable behavior on the historical state and run documented
  baseline/head/current tests. Claimed execution without command output is not
  test evidence; a skip must be explicit and scoped.
- Reconcile the important history: runtime code arrived independently through
  PR #1039, while #1057's surviving squash contribution is targeted tests.
- Independent expected disposition is **MERGE**. Report separately whether a
  different disposition is defensible, over-strict, unsupported, or unsafe;
  do not force binary agreement when the artifact contains materially useful
  reasoning.

## Investment memo

The historical `SHIPPED` gate requires a clean tagged repository, PDF and
source memo, workbook, raw primary sources, extraction/analysis code, decisions,
questions, dead ends, source hashes, and tool log. The substantive overlay also
requires:

- A US-listed $1B-$10B company at the recorded observation date.
- An eight-page-or-shorter readable memo leading with recommendation, 12-month
  target, probability-weighted bear/base/bull cases, risks, differentiated
  thesis or explicit efficient-pricing conclusion, confidence, and limits.
- A real three-statement workbook with formulas—not pasted outputs—whose
  historical periods reconcile to primary filings and whose statements,
  working capital, cash, debt, capex, interest, taxes, and valuation link
  consistently. Formula caches are recalculated before inspection.
- Unit, sign, share-count, enterprise/equity-value, FCFF/FCFE, WACC, terminal
  value, and scenario-probability checks. Five random memo numbers are traced
  end-to-end from source bytes through extraction/model cells to prose.
- Every management quote and external claim is traceable to preserved source
  content; citations or raw filenames without the claimed evidence are defects.

Classify each run as `SUBSTANTIVE_FINANCE_PASS`,
`SHIPPED_WITH_MATERIAL_FINANCE_DEFECTS`, `SCAFFOLD_AND_STOP`, or
`MODEL_TERMINAL_FAILURE`.

## Board presentation

The board run must derive from the matching memo replicate; a terminal memo
produces a preserved dependency failure rather than a substituted input.

- Require PPTX and PDF, 15-25 slides, source/build scripts, standalone chart
  data and regeneration scripts, claim/number/quote traces, five-number
  reconciliation, storyboard committed before the first deck, alternatives,
  audience analysis, decisions, questions, dead ends, sources, and tool log.
- Render every slide and every PDF page. Inspect at full size for clipping,
  overlap, tiny text, broken fonts, malformed axes, illegible contrast,
  inconsistent scenario colors, missing images, and PPTX/PDF divergence.
- Check all required content, probability-weighted scenario visualization,
  reasoning graph, rejected hypotheses, change-my-mind triggers, limitations,
  and the self-audit slide. Re-run a sample of chart scripts and compare output.
- Trace five random displayed numbers and every management quote to the exact
  matching memo-repository commit/file/line and preserved primary evidence.

Classify each run as `SUBSTANTIVE_DECK_PASS`,
`SHIPPED_WITH_MATERIAL_DECK_DEFECTS`, `SCAFFOLD_AND_STOP`,
`DEPENDENCY_FAILURE`, or `MODEL_TERMINAL_FAILURE`.

## Frozen 75-PR audit

Apply `tooling/MMBT-75PR-AUDIT-PROTOCOL.md` unchanged against fixture baseline
`d5154c3` and canonical PR-set SHA-256
`569b95b3384af0c4ae4b54a2c8c8f7c908b396124777927a37b5c8fa0211ecd1`.
Run the existing frozen-scope validator, then inspect individual review/test
substance, traceability, overlap/dependency reconciliation, bounty and AMD
coverage, risk matrix, executive reconciliation, boilerplate, and rerunnable
commands. Exactly three valid outcomes remain in the denominator; only proven
infrastructure-invalid attempts receive replacements.

## Publication

Publish the historical gate, evidence audit, and substantive classification as
separate axes. Compare Gemma to DeepSeek and historical Qwen artifacts only at
matching axes, with task, sampling, context, date, quantization, and N caveats.
All rendered images, workbook/deck audit JSON, compact hashes, grader versions,
and correction overlays are retained; oversized raw archives remain external
with paths and SHA-256 receipts.
