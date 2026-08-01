# Gemma 4 31B QAT Q4_0 MMBT preregistration

Status: frozen before the first Gemma inference on Tower2

Campaign branch: `gemma4-31b-q4-mmbt`

MMBT base: `dcd9431d82168a17f039de084dce1a46ce3cc01a`

## Question

What quality, reliability, long-context behavior, latency, and concurrent
throughput does the official Gemma 4 31B instruction-tuned QAT Q4_0 checkpoint
deliver on Tower2 when it is configured for the best capability-preserving
operation this hardware can sustain? How does that evidence compare with the
published Qwen3.6-27B, Qwen3.6-35B-A3B, Qwen3-Coder-Next, Qwen3.5-397B, and
DeepSeek V4 Flash entries?

The campaign must separate bounded-task benchmark strength from complex
artifact quality, long-horizon agent control, and serving performance. No one
aggregate is allowed to stand in for those distinct questions.

## Immutable model and operating point

- Source: `google/gemma-4-31B-it-qat-q4_0-gguf`
- Revision: `59dde24573e7e61570dba08b18a2e1fe246955ed`
- Text GGUF SHA-256: `179cfb99212709597eae5929112cfca677e1bbf566178b479ae1da0c4772874b`
- Multimodal projector SHA-256: `6bd60bdb958548b4093196d38744b0f2290c12503a3fddd7486bffa9c5eb07a4`
- Native context: 262,144 tokens per sequence
- Sampling: temperature 1.0, top-p 0.95, top-k 64
- Hardware: two RTX PRO 6000 Blackwell Workstation Edition GPUs
- Persistent power limit: 500 W per GPU

The text benchmark uses the text GGUF. The projector is pinned and receives a
separate image smoke test, but multimodal tokens are not injected into the
historical text-only MMBT cells.

The request output cap is 262,144 for every canonical and extended suite. The
harness subtracts actual prompt tokens and a 14,000-token safety reserve, so a
request can never exceed the native total context. A length termination at the
remaining safe ceiling is a valid model-control outcome, not infrastructure
invalidity.

## Serving bakeoff before model benchmarking

The model is only about 17.65 GB, so using both GPUs for each token is not
assumed to be optimal. The four preregistered candidates are:

1. One fully offloaded instance on GPU 0.
2. One instance split 1:1 across both GPUs in llama.cpp layer mode.
3. One instance split 1:1 across both GPUs in llama.cpp row mode.
4. Two independent fully offloaded instances, one per GPU, behind a
   health-aware local router.

The exact machine-readable matrix and selection rule are in
`topology-matrix.json`. Every candidate must use the same model hash, chat
template, sampling, context, and benchmark prompts. Runtime builds are pinned by
commit or image digest. Current llama.cpp source is evaluated because the
already-cached b9641 image predates the validated QAT upload; the cached image is
a fallback candidate, not an assumed winner.

Mandatory gates precede speed ranking: valid chat formatting, native tool-call
round trip, 250K prompt acceptance, start/middle/end recall near 256K, no OOM,
stable restart, and repeatability. A candidate failing any gate is ineligible.
Among passing candidates, concurrency-8 aggregate decode wins; candidates within
10% are broken by single-request end-to-end latency and uncached 128K prefill,
then power, operational simplicity, and failover behavior.

For independent replicas, `-np` and the total context pool are capacity search
variables. A configuration may expose multiple slots only when each advertised
slot can still receive a full 262,144-token sequence. Queueing is preferable to
silently reducing per-request context.

## Production safety gate

DeepSeek remains the production model while non-conflicting preparation occurs.
Before releasing its GPU allocation, Sanctuary and Pixel must each pass a real
request and a fallback route must be proven. During the controlled cutover,
availability and route state are recorded. Both agents must pass again after
Gemma load, after a deliberate Gemma restart, and after the benchmark campaign.
Failure restores the prior known-good route before optimization continues.

## Canonical cohort

The immutable first cohort is the standard 12 task families at N=3: 36 model
runs. It is scored and reported independently for direct comparison with the
historical N=3 local entries and DeepSeek.

After v1-v3 are complete, every family is extended through v10: 120 total model
runs. The first three are not replaced or reselected. Full N=10 is chosen rather
than expanding only favorable or differential cells; it gives Gemma a direct
variance-aware comparison with the Qwen3.5-397B N=10 campaign while retaining
the historical Qwen3.6-27B N=3 and differential-cell comparisons.

All generated grades are preserved. The raw score is always published.

## Extended suites

Each suite runs at N=3 with the full safe 256K request envelope:

- DreamServer single-PR audit
- Wall Street investment memo
- Wall Street board presentation, using the corresponding memo replicate
- Frozen historical DreamServer 75-PR audit at baseline `d5154c3`

The frozen PR-number set SHA-256 is
`569b95b3384af0c4ae4b54a2c8c8f7c908b396124777927a37b5c8fa0211ecd1`.
Current and historical task hashes are recorded in
`tooling/gemma4-31b-q4-extended-matrix.json`.

## Attempt preservation and validity

Every attempt receives a unique run name and remains in the campaign ledger.
No completed or unfavorable run is overwritten.

An attempt may be marked infrastructure-invalid only with affirmative evidence
that the intended model was never evaluated, such as wrong model identity,
fixture/hash mismatch caught before inference, endpoint unavailable for more
than 90 seconds with no model response, or a harness launch failure before the
first request. A server-visible API error is not automatically excluded. OOM,
length termination, looping, malformed tool calls, missing deliverables, bad
formatting, and failure to call tools are valid outcomes unless a separate
reproduction proves an infrastructure defect.

Infrastructure-invalid attempts are preserved, classified, and replaced until
the preregistered valid N is reached. Replacement policy never depends on score.

## Grading and artifact audit

- Original `grade.json` outputs are immutable.
- Corrections require a reproducible grader defect against an unchanged archive.
- Raw grades are copied to `grade.raw.json`; corrected grades and a cell-by-cell
  overlay record archive hash, old/new verdict, reason, and grader commit.
- Corrections may remove generated caches, host-runtime dependence, or a
  contradictory rubric rule. They may not reinterpret a merely weak answer.
- Workbooks are inspected for formulas, hard-coded calculations, consistency,
  missing claimed sheets, and material finance defects.
- Presentations are rendered and visually inspected for overflow, clipping,
  unreadable text, charts, citations, and unsupported claims.
- Agent-audit repositories are checked for required structure, traceability,
  executable evidence, git history/tag, and substantive completion.

## Telemetry and reporting

Record exact model/runtime revisions and commands; prompt and template controls;
sampling; context and output caps; seeds; request IDs; prompt, cached-prompt,
reasoning, and completion tokens; finish reasons; TTFT/prefill/decode where the
server exposes them; wall time; queue time; concurrency; GPU memory, utilization,
power, temperature, and clocks; host power where available; restart/OOM state;
artifact hashes; and grader commits.

Performance probes use uncached prompts or explicitly label prefix-cache hits.
Power telemetry is sampled at five-second cadence and clipped to request/run
windows. Performance comparisons do not mix cached and uncached measurements.

## Comparison and publication rules

Matched claims use common task cells, cohort sizes, and raw scoring where
available. Context, engine, sampling, quantization, and date differences are
shown beside every cross-model aggregate. Gemma may be described as the highest
observed result only if the matched evidence supports it; no global-SOTA claim
is inferred from MMBT.

Compact audits, manifests, hashes, validators, deployment files, scorecards, and
limitations are committed. Oversized raw archives remain external under
`REPO-SPACE.md`, with hashes and inventory in git. Publication requires syntax,
unit, link, evidence, secret, size, and synthetic-merge audits; the draft PR is
merged only after those pass and production agents are healthy.

## Stop conditions

The campaign is complete only when the selected serving topology is stable, all
valid N=3 and N=10 canonical cells and every extended N=3 suite are audited,
the results and deployment rationale are merged into MMBT, and Sanctuary and
Pixel pass the final production checks. Time or a favorable early score is not a
stop condition.
