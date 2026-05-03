# Failure-mode taxonomy

A fixed vocabulary for labeling agent runs. Each run gets one primary label committed in a `label.json` sibling to the receipt + transcript + summary.

The labels exist because reading 38 runs' commit messages to extract "what mode was this?" is slow. Structured labels make cross-run comparison and per-mode counting trivial. Per-run labels are *hand-assigned* — auto-detection is feasible for some labels (see "Auto-detectable" column) but introduces its own noise; for now we trust the human pass.

## Vocabulary

| label | meaning | observable signals | auto-detectable? |
|---|---|---|---|
| `success-shipped` | Full deliverable produced. Required artifacts present. Verdict (or equivalent task output) is correct. Model called `done()` and tag was applied where the spec required. | finish_reason=`done_signal`, all required files exist in workspace, verdict matches ground truth | partial (file existence yes; correctness no) |
| `success-shipped-wrong` | Full deliverable produced and complete. Required artifacts present. But the verdict / answer is wrong (factually incorrect, fabricated evidence, contradicts ground truth). | finish_reason=`done_signal`, all required files exist, verdict disagrees with ground truth | partial (need ground truth) |
| `partial-no-spec-output` | Substantial work done. Some artifacts produced, but the spec-required output (verdict.md / final report / etc.) is missing. Model didn't call `done()` or did but never reached the spec output. | finish_reason in {`model_stopped`, `stuck_no_workspace_change_*`}; some files exist; verdict.md or equivalent absent | yes |
| `scaffold-and-stop` | Spec-shaped output exists (every required file path filled), but most of the per-item content is template stub or auto-generated placeholder. The shape is right; the substance is hollow. | required files present; verdict.md count = N; but content per item averages <X lines or shows duplicate templates across items | yes (with a content-similarity check) |
| `identical-call-loop` | Stuck on N+ consecutive identical bash commands. The model keeps issuing the same call and getting the same result. | tool_call hash of last K iters has duplicate ratio > 0.7 (raw OR digit-stripped — see `scroll-loop` sub-label); finish_reason commonly `stuck_no_workspace_change_*` or `wall_killed_identical_call_loop` | yes |
| `runaway-generation` | Single model response exceeds the harness's max-output-tokens budget without stopping. No tool-call repetition (model never emits another tool call after the runaway response begins). Distinct from `timeout` (HTTP didn't fire), `api-error` (vLLM returned successfully), and `identical-call-loop` (no repetition). | finish_reason=`model_exceeded_max_tokens_*`; transcript stops with a model entry but no follow-up tool entry; transcript stale > 5 min while harness alive and vLLM healthy | yes |
| `cyclic-name-slop` | Writing many byte-identical files with cycling names (filename incremented, content unchanged). Workspace state hash *does* update because the filename is new — defeats the stuck-detector. | content-hash dedupe of files in any one dir shows few unique hashes spread across many filenames | yes (sha1sum + uniq -c) |
| `stuck-in-research` | Many iters of legitimate-looking read-only operations with zero file writes / git commits / artifact production. The model investigates indefinitely without ever transitioning to writing. | iters > N AND write_file count = 0 AND git_commit count = 0 AND read-shaped tool calls (cat, git diff, git log, sed -n, find) > 80% of total | yes |
| `floor-failure` | Few iters before the model stops emitting tool calls entirely. Zero artifacts produced. Distinct from `partial-no-spec-output` in that nothing was produced at all. | finish_reason=`model_stopped` AND iters < 30 AND write_file count = 0 AND git_commit count = 0 | yes |
| `timeout` | The harness's per-call HTTP timeout (3600 s) fired. Model was either hung or thinking for over an hour on a single call. | finish_reason=`api_error: timed out` | yes |
| `api-error` | vLLM returned a non-200 mid-loop and the harness gave up. Common causes: 400 (context overflow), parser fault, OOM. | finish_reason starts with `api_error:` and isn't a timeout | yes |
| `harness-fault` | Run failed because of a bug in the harness, not the model. Example: argv-too-long before the stdin fix, parser bug. | requires inspection of the failure cause | no — needs human |
| `wall-killed` | Run was terminated externally by wall-clock timeout (smoke runs in this batch). Distinct from internal stuck-detector. | no summary.json present (kill bypassed cleanup) AND a wall-clock cap was applied via `timeout` wrapper | yes |
| `aborted-mid-run` | Run was killed manually (kill -9 / docker rm -f) for reasons unrelated to a fair eval — e.g., pivot to a different experiment design, harness bug discovered, GPU resource needed elsewhere. | summary.json absent; receipt present; transcript truncated at non-natural endpoint | no — needs human |

## Sub-labels (orthogonal qualifiers)

These can be added alongside a primary label for finer description. Optional.

- `harness-mid-fix` — run happened with a flag set that was patched mid-experiment; comparable only against runs with the same harness git SHA. (Most relevant to the early Coder-Next smokes that surfaced the determinism + stuck-threshold issues.)
- `cherry-picked` — this is the best of N runs of the same model on the same task; the other (N-1) had different / worse outcomes. Important for the MMBT publishing convention.
- `wrong-on-N-claims` — for `success-shipped-wrong`: N is the count of fabricated technical claims in the verdict (line citations to non-existent issues, fake evidence, misread architecture).
- `scroll-loop` — for `identical-call-loop`: subclass where the model emits the same tool-call template under digit-stripping but with different numeric offsets per iter (e.g., `print(content[N:N+20000])` walking with N += 20000 each iter). Raw command hashes are unique, so the harness's content-hash same-content guard does NOT fire — only the workspace-hash stuck-threshold (500 iters) catches it. Operator detection: digit-strip the last 30+ tool_call commands and check uniqueness; tail_streak ≥ 30 of the same digit-stripped template triggers SIGTERM per the documented methodology rule. (Caught in p3_market_27b-nothink_v1, _v8, and likely the wall_killed_identical_call_loop runs in p3_business and p3_doc.)
- `model-exceeded-max-tokens` — for `runaway-generation` or `partial-no-spec-output`: tags the specific token-budget bucket if it varies across runs (e.g., `model-exceeded-max-tokens-137855`, `model-exceeded-max-tokens-180000`).

## When to use which label

The labels are **mutually exclusive at the primary level** — each run has exactly one. If a run could plausibly fit two labels, prefer the one closer to the *cause*:

- A run that's `identical-call-loop` AND ended with `stuck_no_workspace_change_*` finish_reason → label `identical-call-loop`. The stuck-detector firing is the symptom, the loop is the cause.
- A run that did a ton of read-only ops AND eventually wrote one stub file → label `stuck-in-research`. The single stub doesn't redeem the trajectory.
- A run that wrote scaffolding for 75 PRs and stopped → label `scaffold-and-stop`. Distinct from `partial-no-spec-output` because the spec output *exists*, it's just hollow.

## What the labels are NOT

- **Not a quality score.** `success-shipped-wrong` and `success-shipped` both indicate the model did the work it was supposed to do; the difference is whether the work was *correct*. A stub-filled `success-shipped` that happens to land on the right verdict could be `success-shipped` even though it's bad work. (We'd want a separate quality field for that.)
- **Not blame.** `floor-failure` doesn't mean the model is bad in general — just that it failed this task at this difficulty.
- **Not deterministic.** Same model + same flags + same task can produce different labels across runs (see Coder-Next N=1 v1/v2/v3: `success-shipped-wrong` × 2 + `success-shipped` × 1).

## Updating the taxonomy

Add a label only when an observed run doesn't fit any existing one. Don't add labels speculatively. If the existing labels look ill-fitting in retrospect, prefer adding a sub-label or annotating notes rather than splitting an existing label — backwards compatibility on the labeling matters.

## Labeling format

`label.json` per run, sibling to receipt:

```json
{
  "primary": "success-shipped-wrong",
  "sub_labels": ["wrong-on-4-claims"],
  "notes": "Hallucinated stderr-direction is wrong; fabricated test_stderr_truncation.py supports the wrong claim.",
  "labeler": "human",
  "labeled_at": "2026-04-27T20:30:00Z"
}
```
