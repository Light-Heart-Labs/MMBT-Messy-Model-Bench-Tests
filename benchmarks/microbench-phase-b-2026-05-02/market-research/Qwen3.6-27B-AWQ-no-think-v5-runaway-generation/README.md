# p3_market 27B-no-think v5 — `runaway-generation` (NEW pathology)

> Single-run failure-mode entry. The new `runaway-generation` primary label was added to [`tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md) because of this exact run — it's the canonical example.

## What happened

Started 2026-05-02 19:00 UTC. Made real research progress across all five vendors over 67 iterations, then went silent at iter 67 — no new tool calls, no new transcript entries — for **12+ minutes** while the harness was alive and vLLM was healthy on port 8002.

The mechanism: the model emitted **a single response of 137,855 output tokens** without ever calling another tool. The harness's max-output-tokens budget for this run was 137,855; vLLM returned the response cleanly when the budget was exhausted, and the harness wrote `finish_reason=model_exceeded_max_tokens_137855` and shipped the run.

This is **not** an `identical-call-loop` (no tool repetition — the model never emitted another tool call after iter 67). It is **not** a `timeout` (the harness's HTTP timeout is 3,600 s and was not reached). It is **not** an `api-error` (vLLM returned a successful response). It's a fourth thing — a runaway generation that exhausts the output-token budget — that wasn't in the taxonomy until this run.

## Why this matters

`runaway-generation` is operationally distinct from `identical-call-loop`:
- `identical-call-loop` shows up as repeated tool calls in the transcript — easy to catch via tool-call hashing.
- `runaway-generation` shows up as a single very long *model response* with no follow-up tool call — invisible to tool-call-based detectors.

The detection signal is: transcript stale > 5 minutes while the harness is alive and vLLM is healthy. This is now the documented monitoring criterion for this pathology.

## How long the operator should wait before SIGTERM

Looking at this run: the model spent ~17 minutes generating 138K tokens at ~135 tok/s (consistent with vLLM's no-think decode rate on Qwen3.6-27B-AWQ at 500 W). If a transcript stays silent for 10+ minutes with the harness alive, there are three possibilities:
1. Runaway generation in progress — wait for it to finish (will exhaust budget naturally).
2. vLLM API stall — won't recover; the harness's 3,600 s HTTP timeout will eventually kill it.
3. A genuinely huge-but-legitimate response — rare on these tasks.

For ship-rate optimization, **let it run**. The harness will produce a `summary.json` either way, and the `model_exceeded_max_tokens_*` finish_reason cleanly tags the failure. SIGTERM only saves time vs the HTTP timeout (3,600 s), not vs natural completion.

## Workspace artifact

The model wrote real research notes (1.38 MB workspace tarball — preserved in source bench's submit branch) before the runaway response began. A reader looking at the partial deliverable would find structured pricing/security notes for 1Password / Bitwarden / Dashlane / Keeper, but no `recommendation.md` or `verdict` because the model never finalized.

## What's published here

- `cost.json` — 1078 s wall, $0.039 upper-bound
- `label.json` — primary `partial-no-spec-output`, sub-label `model-exceeded-max-tokens`, with detailed narrative
- `receipt.json` — task SHA, harness SHA, model + flags
- `summary.json` — finish_reason `model_exceeded_max_tokens_137855`, full token / iter counts

Full transcript + 1.38 MB workspace tarball in source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_27b-nothink_v5/`.

## Cross-references

- [`../Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/`](../Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/), [`../Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/`](../Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/) — the other two `p3_market` 27B-no-think pathologies
- [`../../findings.md`](../../findings.md) § "Two new pathologies surfaced"
- [`../../../../tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md) § `runaway-generation` primary label — the formal taxonomy entry this run defined
