# Gemma 4 31B QAT Q4_0 on Tower2

This directory is the reproducibility package for the Gemma 4 31B Q4 campaign.
It is created before serving optimization so runtime choices cannot be selected
after seeing benchmark quality.

Read in this order:

1. `PREREGISTRATION.md` — immutable questions, cohorts, validity policy, and
   topology selection rule.
2. `model-manifest.json` — exact local artifacts, hashes, upstream revision,
   hardware, and runtime candidates.
3. `topology-matrix.json` — serving candidates, workloads, and winner rule.
4. `final-validation.json` — populated only after a serving candidate passes.
5. `campaign/` — launchers, units, telemetry, and benchmark supervision added as
   the preregistered phases execute.

The source is Google's [official QAT Q4_0 GGUF](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-gguf).
Google documents [llama.cpp as an OpenAI-compatible Gemma serving route](https://ai.google.dev/gemma/docs/integrations/llamacpp),
and the model repository pins the 256K context and temperature 1.0 / top-p 0.95 /
top-k 64 operating point.

This package deliberately tests one model per GPU as well as cross-GPU splitting.
The 17 GB text model fits on either 98 GB GPU; using both GPUs for every request
would add communication without necessarily improving latency or aggregate
throughput.

The campaign runtime is temporary. `production-restore.json` fingerprints the
proven DeepSeek launcher, image, OpenClaw routing, and a permission-restricted
pre-campaign config backup. Campaign completion requires stopping Gemma,
restoring that DeepSeek state byte-for-byte, and passing fresh Sanctuary and
Pixel end-to-end checks.

Serving files
-------------

- `run-gemma4-server.sh` is the foreground server launcher. It refuses any
  context pool that would leave a parallel slot with less than 262,144 tokens,
  and refuses a server read/write timeout below 14,400 seconds. The four-hour
  floor is long enough to reach the native output boundary at the slowest
  long-generation decode rate observed during canonical N=3.
- `mmbt-gemma4@.service` and `topologies/*.env` define the preregistered serving
  candidates.
- `gemma4-topology-control.sh` enforces mutually exclusive topology candidates
  and refuses to start while the DeepSeek container still owns the GPUs.
- Split-GPU builds use the privately pinned NCCL runtime recorded in
  `model-manifest.json`; no system CUDA or NCCL package is modified.

Validated benchmark serving
---------------------------

The winning quality-preserving topology is two independent Q8-KV, four-slot
replicas: GPU 0 on port 8000 and GPU 1 on port 8001. Each request stays on one
GPU and retains a hard 262,144-token context; using both replicas concurrently
increases campaign throughput without introducing a cross-GPU dependency.

- `benchmark-serving-manifest.json` is the compact immutable receipt anchor for
  the artifact, runtime, topology, sampling point, context, output ceiling, and
  500 W power caps.
- `ensure-gemma4-winner.sh` starts and health-checks both systemd services; the
  benchmark supervisor uses it for recovery rather than assuming a container.
- `tooling/gemma4-31b-q4-mmbt.json` sends temperature 1.0, top-p 0.95, top-k 64,
  and the 262,144-token output ceiling to the harness. Work is assigned by
  stable run ordinal modulo two, so the lanes are disjoint and reproducible.
- Every run receipt captures the deployment manifest, live `/v1/models`
  identity, and the exact host `llama-server` path, arguments, and SHA-256.
- The supervisor watches each port independently and treats advancing
  llama.cpp `/slots` prompt/decode counters as live progress. This matters at
  the native 262K output envelope: a non-streamed HTTP call can decode for more
  than the historical transcript-staleness timeout without appending a JSONL
  row, and must not be misclassified as a hung run. The five-minute substance
  monitor is likewise keyed to every live lane and exact harness PID, so work
  on one replica cannot mask an identical-call loop on the other.
- `gemma4_gpu_telemetry.py` samples both GPUs and the CPU package every five
  seconds. It attributes port 8000's active harness to GPU 0 and port 8001's to
  GPU 1, so simultaneous cells are not mislabeled as one dual-GPU request.
- `analyze_replica_telemetry.py` clips samples to authoritative evidence
  windows and records their exact source. Normally that is `summary.json`; an
  explicit terminal outcome instead uses the preserved receipt/transcript
  start and label/transcript end. It writes per-run power, utilization, memory,
  temperature, clock, energy, CPU-package context, coverage, and concurrent-lane
  evidence for both completed workspaces and terminal outcomes. AC wall draw is
  explicitly unavailable to software and is not fabricated from component data.
- The telemetry sidecar derives `cost.json` and `gpu_telemetry.json` for an
  explicit terminal label as well as a normal summary. A model-control failure
  therefore cannot evade resource accounting merely because it never produced
  a final workspace archive.
- `snapshot_gemma4_telemetry.sh` fail-closes cohort-boundary snapshots. It
  refuses an active benchmark or overwrite, briefly stops the telemetry writer
  and sidecar, validates that the copied CSV ends on a complete row with the
  pinned schema, prints its SHA-256, and restores exactly the services that
  were active. N=3 and N=10 audits point at immutable snapshots rather than
  hashing a live CSV that later cohorts will append to.

The two-lane optimization changes scheduling only. It does not change the
canonical run names, cohort membership, prompts, grading, or attempt-preservation
rules, and v1-v3 remain the immutable first cohort before expansion through v10.

Canonical refactor v3 exposed that the initial llama.cpp default
`--timeout 3600` was shorter than the model's native envelope: the final API
call was cancelled at exactly one hour after 133,606 decoded tokens, while the
slot remained untruncated at 151,966 total tokens. The attempt is preserved in
`logs/_invalid/` and externally, and is excluded as infrastructure-invalid
independently of its score. Its prolonged post-work generation remains valid
operational reliability evidence. The exact cell is replaced under the same
prompt, model, sampling, context, and output controls after raising only the
server transport timeout to 14,400 seconds. See
`canonical-refactor-timeout-incident-20260802.json`.

Canonical bug-fix v1/v2 completed before the telemetry sidecar was introduced.
After N=3 stops, `tooling/run_gemma4_supplemental_telemetry.sh` produces exactly
two separately labeled, one-per-GPU observations with identical operating
controls. They never replace or enter the quality cohort. The fail-closed audit
requires explicit canonical-to-supplement mappings and validates each
supplement's complete receipt, archive, cost, and telemetry evidence. The
supplement launcher also requires both replica slot pools to be idle at launch,
so an already-running Sanctuary or Pixel request cannot silently contaminate
the matched observation.

At the clean N=3 boundary, the committed tools run in this order:

```bash
bash tooling/run_gemma4_supplemental_telemetry.sh
bash tooling/snapshot_gemma4_telemetry.sh \
  /home/michael/gemma4-campaign-state/telemetry/snapshots/canonical-n3-plus-supplement.csv

python3 tooling/audit_gemma4_campaign.py \
  --target-n 3 --require-grades \
  --allow-pretelemetry-run p1_bugfix_gemma4-31b-q4_v1 \
  --allow-pretelemetry-run p1_bugfix_gemma4-31b-q4_v2 \
  --pretelemetry-supplement \
    p1_bugfix_gemma4-31b-q4_v1=p1_bugfix_gemma4-31b-q4-telemetry-supplement_v1 \
  --pretelemetry-supplement \
    p1_bugfix_gemma4-31b-q4_v2=p1_bugfix_gemma4-31b-q4-telemetry-supplement_v2 \
  --raw-telemetry \
    /home/michael/gemma4-campaign-state/telemetry/snapshots/canonical-n3-plus-supplement.csv \
  --output logs/_campaign_audit/gemma4-canonical-n3-evidence-audit.json

python3 tooling/capture_gemma4_grader_manifest.py \
  --target-n 3 \
  --output logs/_campaign_audit/gemma4-canonical-n3-grader-manifest.json
python3 tooling/summarize_gemma4_campaign.py \
  --target-n 3 \
  --allow-pretelemetry-run p1_bugfix_gemma4-31b-q4_v1 \
  --allow-pretelemetry-run p1_bugfix_gemma4-31b-q4_v2 \
  --output-json logs/_campaign_audit/gemma4-canonical-n3-scorecard.json \
  --output-markdown logs/_campaign_audit/gemma4-canonical-n3-scorecard.md

python3 tooling/correct_gemma4_project_mgmt_grades.py \
  --target-n 3 \
  --output logs/_campaign_audit/gemma4-canonical-n3-project-mgmt-correction.json
```

N=10 repeats the snapshot, audit, grader-manifest, and scorecard commands with
`--target-n 10` and a distinct immutable telemetry snapshot. Extended suites
start only after that second boundary passes.

`tooling/summarize_gemma4_campaign.py` generates the raw N=3 and N=10 JSON and
Markdown scorecards only when every expected completed workspace or explicit
terminal label has its required grade/label, cost, and telemetry evidence. It
keeps `done_signal`, raw PASS/STRUCTURAL_PASS, explicit terminal non-pass
outcomes, model-call throughput, total wall time, and per-replica telemetry as
separate axes; it never invents a normal grade for a terminal outcome, and
reproducible grader corrections remain separate hash-tied overlays.
`tooling/capture_gemma4_grader_manifest.py` fingerprints the grading driver,
all task graders and ground-truth inputs, the sandbox image, runtime versions,
repository commit, and every raw grade/terminal-label file before any overlay
is considered.

The raw project-management grader searches for a few contiguous phrases and
misses semantically exact wording such as “Maevia … push back,” “Legal has not
yet responded,” hyphenated “web-responsive,” and “private beta (3-5
customers).” `tooling/correct_gemma4_project_mgmt_grades.py` is a narrow,
non-destructive overlay fixed after N=3 and before N=10. It records the raw
grade, report, archive, raw-grader, and correction-script hashes; changes only
those four lexical false negatives; and never overwrites `grade.json`. Raw
scores remain primary and the corrected total is reported separately. No other
failure is reinterpreted without an independently reproducible grader defect.

`invalid-attempt-classifications.json` is the exclusion ledger. The canonical
auditor requires every `logs/_invalid/` directory to have a matching
score-independent infrastructure classification, affirmative evidence,
hash-pinned preserved files, an incident document, and a completed exact
canonical replacement. An unknown, altered, or merely pending exclusion makes
the cohort audit fail.

`tooling/gemma4-comparison-sources.json` freezes the pre-result evidence for
Qwen3.6-27B, Qwen3.6-35B-A3B, Qwen3-Coder-Next, Qwen3.5-397B-A17B, and
DeepSeek V4 Flash. `tooling/validate_gemma4_comparison_sources.py` verifies
every source hash and checks the extracted DeepSeek/Qwen397 raw and corrected
totals plus the historical serving controls. Qwen3.6-35B-A3B is deliberately
recorded as lacking a comparable canonical cohort rather than being assigned a
made-up rank. This pin happens before Gemma grades are known.

`tooling/analyze_gemma4_queueing.py` derives the accepted four-slot queueing
result from the preserved simultaneous-eight-request probe. It separates the
four shortest first-wave requests from the four queued requests, subtracts
llama.cpp-reported prompt-plus-decode work from client wall time, fingerprints
the raw source, and labels the resulting queue-wait delta as an estimate rather
than a direct server timestamp.

The committed `queueing-analysis.json` reports 112.6166 aggregate decode
tokens/s at eight simultaneous requests. With four slots, the second wave's
median client wall was 9.0752 seconds longer and the derived queue-wait delta
was 9.0921 seconds. The source is the hash-pinned uncached topology probe; the
queue delta remains explicitly an estimate because llama.cpp did not expose a
direct per-request queue-start timestamp.

Extended-suite scheduling
-------------------------

`tooling/run_gemma4_extended_suites.py` applies the same two-lane design to the
four DeepSeek-comparable extended suites. `mmbt-gemma4-extended@.service` pins
lane 0 to port 8000 and lane 1 to port 8001. Jobs are assigned by immutable
suite/replicate ordinal, and board-presentation jobs wait for their matching
investment-memo workspace even when the dependency is running on the other
lane. Any Python traceback stops that lane for operator review; endpoint outages
are the only automatically replaceable attempts.

`tooling/audit_gemma4_extended.py` then fail-closes the 12-run matrix over
model/runtime identity, pinned task hashes, deterministic lane assignment,
sampling/context/output controls, 500 W receipts, telemetry, dependency
lineage, frozen-fixture mounting, archive hashes, and preserved invalid
attempts. The one-PR arm additionally requires every artifact to identify the
base, head, squash contribution, and original commits pinned in
`gemma4-single-pr-subject-pin.json`, matching the three DeepSeek comparator
archives despite the prompt's stale “open PR” wording. Its result is
deliberately an evidence audit, not a quality verdict:
the one-PR and 75-PR repositories, investment workbooks, and rendered board
decks still receive their separate substantive code, finance, and visual
overlays before publication. Those overlay rules are fixed before launch in
`tooling/GEMMA4-EXTENDED-SUBSTANTIVE-AUDIT-PROTOCOL.md`; its SHA-256 is pinned
by the extended matrix so completed artifacts cannot change the rubric.
