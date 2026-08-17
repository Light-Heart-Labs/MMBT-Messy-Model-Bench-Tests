# DEVIATIONS — Qwen3.6 vs Qwen3.8 corrective study

Preregistration rule (binding): quarantine + same-seed rerun is reserved for
mechanically identified INFRASTRUCTURE failures; every deviation from the
preregistered protocol is recorded here with timestamp + rationale BEFORE any
affected analysis. Machine-written artifacts for the corrections below are
committed under `deviations/` (the operational ledgers under `/logs/` are
gitignored by design; the committed copies are byte-identical to the appended
ledger lines).

Both deviations were recorded 2026-08-17 (file written 2026-08-17T13:55Z),
during phase_a of the exploratory diag-t03 arm, while phase_b / quant /
analysis remain blocked. No affected analysis had run.

---

## Deviation 1 — 2026-08-17T13:55Z: `exceed_context_size` api_error is a MODEL outcome ("context-exhausted"), not infra

**Incident.** Cell `p3_market_q38-diag-t03-nothink-s101_v1` (exploratory
diag-t03 arm, phase_a, tower1:18101): attempt 1 ran 479 model turns in 1787 s
until the model's own prompt reached 262,339 tokens against the serving
window of 262,144, and llama-server rejected the request with HTTP 400
`{"type":"exceed_context_size_error","n_prompt_tokens":262339,"n_ctx":262144}`
(final transcript event, 2026-08-17T13:33:21Z). The delivery validator
bucketed ALL `api_error` finishes as `infra`, so the cell was quarantined and
same-seed rerun; attempts 2–4 died in ~2 s each with zero model turns (see
deviation 2), the quarantine budget exhausted, and the phase_a launcher
aborted by design.

**Clarification (this deviation).** The protocol restricts quarantine to
infrastructure failures. Context exhaustion via the model's own prompt growth
is model behaviour, not infrastructure: the serving endpoint was healthy and
answered 479 requests correctly, and the 480th request was rejected because
of what the model had accumulated. `tooling/corrective/delivery_validator.py`
now splits `api_error` handling mechanically:

* HTTP 400 `exceed_context_size` (matched on the recorded error-event body:
  the `exceed_context_size` type string and/or the
  `request (N tokens) exceeds the … context size (M tokens)` message), with
  at least one model turn in the transcript, classifies as
  **`context-exhausted`**: a terminal MODEL outcome like a loop-label cell —
  `delivery: false`, never quarantined, never rerun.
* A zero-model-turn context overflow (first request already over the window)
  stays `infra` — that can only be a task/config/serving problem.
* All other `api_error` finishes (connection refused/reset, 5xx, timeouts,
  empty response) stay `infra` → quarantine + same-seed rerun, unchanged.

Unit tests cover both directions
(`tooling/corrective/test_delivery_validator.py`; suite now 69 tests,
CI floor ≥ 64).

**Direction note.** The ORIGINAL misclassification FAVOURED q38: it removed a
real q38 delivery failure (`delivery: false`) from the diag arm's outcome
ledger by quarantining it as infra and attempting to replace it with
same-seed reruns, which would have both suppressed a genuine q38 failure and
inflated the infra-rerun count.

**Restoration.** Attempt 1 is the cell's true, terminal result. Its artifacts
were COPIED (quarantine forensics preserved at
`logs/corrective/quarantine/p3_market_q38-diag-t03-nothink-s101_v1.attempt1.20260817T133322Z/`)
back to the canonical cell dir, re-validated with the fixed validator
(`classification: context-exhausted`, `delivery: false`, 479 model turns),
the outcome record appended to `logs/corrective/cell_outcomes.jsonl`, and a
machine-written correction line appended to
`logs/corrective/rerun_ledger.jsonl` marking attempts 2–4
**void-infra-misfire**. Committed byte-copies:
`deviations/p3_market_q38-diag-t03-nothink-s101_v1.restored-outcome.jsonl`,
`deviations/rerun-ledger-correction.jsonl`.

**Blast radius: zero confirmatory-arm cells.** This occurred in the
exploratory diag-t03 arm only. Mechanically verified over all outcome
records (`logs/corrective/cell_outcomes.jsonl`, 2026-08-17): 144
official-nothink / official-think rows, of which **zero** contain
`api_error`; the only `api_error` row in the file is the restored diag cell
above; `rerun_ledger.jsonl` and `logs/corrective/quarantine/` contain only
this one cell's attempts. No official-nothink or official-think cell ever
hit an `api_error`.

---

## Deviation 2 — 2026-08-17T13:55Z: rerun path could never launch a harness (root-owned workspace residue); fixed

**Mechanical cause (attempts 2–4, ~2 s deaths, zero model turns).** The
sandbox container runs as root and writes root-owned files into the
bind-mounted per-run workspace `tooling/workspace/<run_name>/` (for this
cell: `.git/`, `mirror/`, `research/` — 118 root-owned entries). Quarantine
moves only `logs/<run_name>`; the workspace stays behind. On each rerun,
`tooling/harness.py` (pre-fix lines 1136–1138) executed an unprivileged
`rm -rf` of that workspace with `check=True`; `rm` failed with
`Permission denied` (exit 1) on the root-owned entries, raising
`CalledProcessError` before the harness ever created the sandbox or made a
model request. Attempt logs
(`logs/corrective/cell-logs/p3_market_q38-diag-t03-nothink-s101_v1.attempt{2,3,4}.log`)
show exactly this traceback; the attempt 2–4 quarantine dirs are empty
because each rerun died before writing anything.

**Fix.** `tooling/harness.py` now scrubs an existing per-run workspace
INSIDE a container mounting only the workspace parent
(`docker run --rm -v <parent>:/w alpine rm -rf /w/<run_name>` — the audit
A4b cleanup pattern; never sudo), falling back to plain `rm -rf` only for
hosts without docker/alpine.

**Verification (2026-08-17, throwaway detached worktree — campaign ledgers
untouched).**

* Negative control: root-owned residue created via the sandbox-equivalent
  container; unprivileged `rm -rf` fails (`Permission denied`, rc=1 — the
  pre-fix crash), the containerized scrub removes it (rc=0).
* End-to-end supervisor loop against a mock endpoint whose first completion
  request returns HTTP 503: attempt 1 classified `infra` and quarantined
  with full artifacts + ledger line; the same-seed rerun (attempt 2)
  **actually launched a harness** — scrubbing the root-owned residue left by
  attempt 1's sandbox — recorded a model turn, and ended terminal
  (`completed-no-delivery`, supervisor rc=0). This is the exact incident
  mechanism, now surviving a genuine infra rerun.

**Void attempts.** Attempts 2–4 of
`p3_market_q38-diag-t03-nothink-s101_v1` are marked
**void-infra-misfire** in the ledger correction (deviations 1+2 artifacts
above): they are evidence about the rerun tooling, not about the endpoint or
the model.

---

Both tooling changes (`tooling/corrective/delivery_validator.py`,
`tooling/corrective/test_delivery_validator.py`, `tooling/harness.py`) and
this file are committed byte-identically on the live campaign branch
(`methodology/qwen-corrective-2026-08`) and the clean methodology branch
(`methodology-clean/qwen-corrective-2026-08`), per the audit's byte-identity
gate.
