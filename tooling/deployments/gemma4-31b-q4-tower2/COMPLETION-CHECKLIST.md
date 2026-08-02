# Gemma 4 31B Q4 campaign completion checklist

This checklist maps each required campaign outcome to authoritative evidence.
It is an operational completion gate, not a substitute for the evidence and
does not relax `PREREGISTRATION.md`.

## 1. Artifact and cohort pin

- [x] Official QAT Q4_0 model, matching mmproj, Hugging Face revision, byte
  sizes, and local SHA-256 values are recorded in `model-manifest.json`.
- [x] MMBT base, task fixtures, model-card sampling, native context, topology
  candidates, validity policy, canonical N=3, N=10 expansion, and extended N=3
  suites were pinned before their applicable runs.
- [ ] Final validator output proves the pinned files and local model artifacts
  still match at publication time.

## 2. Tower2 serving choice

- [x] One-GPU full offload, dual-layer split, dual-row split, and independent
  replicas were measured under the 500 W limits.
- [x] Independent full-offload replicas won the preregistered quality-preserving
  rule and passed chat, tool, concurrency, restart, and near-256K recall
  gates; the decision and rejected candidates are documented in `README.md`,
  `topology-matrix.json`, `MICROBENCH-INDEX.md`, and `final-validation.json`.
- [ ] Publication explicitly reports queued-request latency or queue wait at the
  accepted four-slot operating point rather than inferring it from aggregate
  concurrency alone.
- [ ] Publication artifacts include the exact accepted runtime/model hashes and
  uncached-versus-cached labels for every quoted performance result.

## 3. Sanctuary and Pixel

- [x] Pre-campaign fallback and pre-canonical Gemma route checks are preserved.
- [x] Sanctuary and Pixel were placed on separate replica endpoints.
- [ ] Fresh post-campaign checks prove both agents can complete a real tool turn
  before publication.
- [ ] After publication, the byte-for-byte pre-Gemma OpenClaw configuration is
  restored, DeepSeek-V4-Flash-0731 is restarted, both agents use it without
  fallback, and fresh end-to-end markers and tool turns pass.

## 4. Instrumentation and validity

- [x] Receipts capture model/runtime identity, live endpoint, sampling/context,
  power caps, task hash, repository state, and archive provenance.
- [x] Per-replica GPU plus shared CPU-package telemetry, cost extraction,
  deterministic two-lane scheduling, endpoint recovery, exact-PID substance
  monitoring, and server-slot progress watchdogs have isolated tests.
- [x] Explicit terminal outcomes retain receipt, transcript, cost, telemetry,
  label, and evidence-window provenance without fabricating normal grades.
- [x] The one-hour transport-timeout refactor attempt remains preserved as
  infrastructure-invalid, and its exact replacement reaches a model-native
  stop condition under the corrected 14,400-second server timeout.
- [ ] The committed boundary bundle passes syntax, unit, ShellCheck,
  preregistration, and comparison-source validation from a clean worktree.

## 5. Canonical matrix

- [ ] All 36 immutable N=3 cells are completed or explicitly terminal, graded
  or labeled, telemetry-audited, and summarized without cherry-picking.
- [ ] The two pre-telemetry bug-fix attempts retain their original quality
  outcomes and map to separately labeled, idle-start supplemental observations.
- [ ] Raw N=3 grader manifest, scorecard, evidence audit, invalid-attempt
  inventory, raw telemetry hash, and any reproducible correction overlay are
  complete.
- [ ] All 120 N=10 cells, including immutable v1-v3, meet the same gates and
  have a separate variance-aware scorecard and audit.

## 6. Extended suites

- [ ] Single-PR audit N=3 uses the exact pinned PR #1057 base/head/squash and
  original commits; evidence and substantive code-review audits pass.
- [ ] Investment memo N=3 archives receive formula, statement, unit,
  traceability, valuation, and material-finance review.
- [ ] Board presentation N=3 derives from the matching memo replicate; every
  deck is rendered and receives structural, visual, and claim-trace review.
- [ ] Frozen historical 75-PR N=3 uses the pinned baseline and PR-set hash and
  receives strict coverage, traceability, repository, test, and substance
  review.
- [ ] Every attempt and dependency failure is preserved; only affirmatively
  proven infrastructure-invalid attempts are excluded and replaced.

## 7. Cross-model interpretation

- [x] Comparator source documents and historical operating points were pinned
  before Gemma grades in `gemma4-comparison-sources.json`.
- [ ] Gemma N=3 and N=10 raw/corrected results are compared with Qwen3.6-27B,
  Qwen3.6-35B-A3B, Qwen3-Coder-Next, Qwen3.5-397B-A17B, and DeepSeek V4 Flash
  only on supported axes, with sample-size, engine, quantization, context,
  sampling, power, date, grader, and task-level caveats.
- [ ] The final report distinguishes bounded-task quality, performance,
  artifact-modality quality, and marathon-agent reliability; it makes no
  unsupported global-SOTA claim.

## 8. Publish, merge, and restore

- [ ] Compact reports, manifests, hashes, validators, deployment files,
  scorecards, correction overlays, and external-archive inventories comply with
  `REPO-SPACE.md`.
- [ ] Code, evidence, link, secret, size, synthetic-merge, and security audits
  pass; the worktree is clean.
- [ ] A draft PR is opened against current MMBT main, independently audited,
  updated if necessary, and merged only when clean.
- [ ] Gemma campaign and telemetry services are stopped after evidence capture;
  the proven DeepSeek launcher/config is restored byte-for-byte and Sanctuary
  and Pixel pass final DeepSeek health checks.
- [ ] Only after every box above has authoritative evidence is the persistent
  campaign goal marked complete.
