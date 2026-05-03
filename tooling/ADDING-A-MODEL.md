# Adding a new local model to the microbench

End-to-end walkthrough: from "I have a HuggingFace model name" to "PR submitted with my model's results in MMBT." Built so that a new contributor can rerun the same 12-task-family microbench against any vLLM-supported model and produce comparable, reproducible results.

> **TL;DR**: Pull weights, add a launch command, smoke-test (5 min), full chain (3-7 hr), grade, summarize, write up. Half-day to one-day total operator time.

## Two contribution shapes

This walkthrough covers both:

1. **New model entry** — a model that isn't currently in the comparison (any vLLM-supported local model with a working tool-call parser).
2. **Same model, different quant** — re-running an existing comparison-arm model at a different precision (e.g. official Qwen FP8, Unsloth UD4 GGUF, BF16) of the same base model. This is currently the **highest-priority external contribution path** — see [`ROADMAP.md`](../ROADMAP.md) item 1, motivated by field reports that the published Cyankiwi 4-bit AWQ quants underperform other precisions of the same models.

The mechanics are the same in both cases: only the HuggingFace model path and the vLLM launch flags change. Use a tag like `qwen3.6-27b-fp8` or `qwen3-coder-next-unsloth-ud4` so the result is comparable and clearly differentiated from the published Cyankiwi 4-bit AWQ entries.

## What you need

**Hardware**: a Linux box with a CUDA-capable GPU. Tower2 (the published runs' hardware) has 2× RTX PRO 6000 Blackwell (96 GB each); the canonical flags assume that. **For smaller GPUs** (24-48 GB), drop `--max-model-len` to 32k-65k and `--gpu-memory-utilization` as needed. The tasks themselves rarely exceed 30k tokens of context — long context isn't needed.

**Software**: Docker with NVIDIA Container Toolkit, Python 3.10+ on the host. ~50 GB free disk for the vLLM image plus your model.

**Model**: any HuggingFace model that vLLM supports AND that has a working tool-call parser. See [`launch-commands.md`](launch-commands.md) § "Tool-call-parser quick reference" for a parser ↔ model-family table covering Qwen, Llama, Mistral, DeepSeek, Gemma, GLM, Phi, Hermes.

**API access (optional)**: nothing required for the local-model path. The market-research task fetches public web pages from the sandbox; if you're behind a strict firewall, that one task will fail, the other 11 will work.

## The friendly path (4 commands once setup is done)

```bash
# 1. Build the sandbox image (one-time, ~5 min)
docker build -t bench-sandbox:latest tooling/

# 2. Pull the vLLM image (one-time, ~12 GB)
docker pull vllm/vllm-openai:latest

# 3. Start vLLM serving your model (see "Step-by-step" below for the docker run)
docker run -d ... --served-model-name my-new-model --port 8001 ...

# 4. The friendly path
bash tooling/scripts/smoke_test.sh my-new-model 8001          # ~3 min
bash tooling/scripts/run_microbench.sh my-new-model 8001 my-label   # 3-7 hr
bash tooling/scripts/grade_microbench.sh my-label             # ~5 min
bash tooling/scripts/summarize.sh my-label                    # instant
```

That last command prints a per-task PASS/FAIL table next to the published Coder-Next + 27B reference numbers, so you can see at-a-glance where your model is stronger or weaker.

## Step-by-step

### Step 1: Pick a model and verify vLLM supports it

Check vLLM's [supported models list](https://docs.vllm.ai/en/latest/models/supported_models.html). Most modern instruction-tuned models are supported. Specifically check that:
- The base model architecture is supported (e.g. `LlamaForCausalLM`, `Qwen3ForCausalLM`)
- A tool-call parser exists for the model family (see the table in `launch-commands.md`)
- If the model has a thinking/reasoning mode, a reasoning parser exists or is omittable

If your model is a fresh release, check the vLLM GitHub issues for "tool calling" + the model name. Sometimes parsers land weeks after the model.

### Step 2: Pull the weights

```bash
# Option A: huggingface-cli (recommended for most users)
huggingface-cli download <org>/<model> --local-dir ~/models/<org>-<model>

# Option B: curl + manifest (for slow/buffer-bloated connections — see Tower2 memory note)
# Faster than hf_transfer on links with bufferbloat; see https://huggingface.co/docs/hub/datasets-downloading
```

Path convention: `~/models/<org>-<model>/`. The vLLM container will mount this directory read-only.

### Step 3: Write a launch command

Open [`launch-commands.md`](launch-commands.md) and add a new section for your model, copying the closest existing entry as a template. The two flags that matter most:

- `--tool-call-parser <parser>` — see the quick-reference table. Wrong parser = empty `tool_calls` arrays = agent never executes any tool. **This is the single most common failure mode for a new model.**
- `--reasoning-parser <parser>` — only if the model has a thinking mode. Adding it to a non-thinking model causes all output to land in the `reasoning` field with empty `content`.

Example template for an unfamiliar model:

```bash
docker run -d \
  --name vllm-my-new-model \
  --gpus '"device=0"' \
  --shm-size 8g \
  -v ~/models:/models:ro \
  -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/<org>-<model> \
  --served-model-name my-new-model \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 65536 \
  --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice \
  --tool-call-parser <parser-from-table>
```

For thinking models, add `--reasoning-parser <parser>`. For Qwen3 it's `qwen3`; for DeepSeek-R1 it's `deepseek_r1`; for GLM-4.5 thinking it's `glm45`.

Wait for it to come up:

```bash
until curl -sf http://127.0.0.1:8001/v1/models >/dev/null; do sleep 5; done
echo "ready"
curl -s http://127.0.0.1:8001/v1/models | jq '.data[].id'
```

### Step 4: Smoke test (CRITICAL)

```bash
bash tooling/scripts/smoke_test.sh my-new-model 8001
```

This runs the structured-extraction task at N=1 (~2-5 min wall) and grades the output. Expected:

```
==> Smoke test result
    verdict:  PASS
    accuracy: 0.95-1.0
    log dir:  logs/smoke_extract_...
✓ Smoke test PASS — your setup works.
```

**If smoke test fails**, do NOT proceed to the 3-7 hour full chain. Common failures:

| Symptom | Cause | Fix |
|---|---|---|
| `tcs=0` on every iter in transcript.jsonl | Wrong `--tool-call-parser` | Try a different parser from the quick-ref table |
| Output in `reasoning_content`, `content` empty | `--reasoning-parser` set on non-thinking model | Drop the flag |
| 4xx/5xx from vLLM endpoint | Container loading or model name mismatch | `docker logs vllm-...`; check `/v1/models` shows your model |
| Stuck-detector fires immediately | Agent isn't calling tools (parser issue) OR model is too small for the task | Verify smoke test passes on a known-good model first |
| OOM on container start | `--max-model-len` too high for your GPU memory | Drop to 32768 or 16384 |

Once smoke passes, the rest is mechanical.

### Step 5: Full microbench chain

```bash
bash tooling/scripts/run_microbench.sh my-new-model 8001 my-label 3
```

Args: `<served-model-name> <port> <run-name-tag> <N>`. The chain runs all 12 task families × N replicates.

Wall time:
- Tower2-class hardware (2× 96 GB Blackwell, 4-bit AWQ models): **3-7 hours** for N=3
- Smaller GPUs / FP8 / BF16: probably 6-15 hours for N=3
- N=1 instead of N=3 cuts wall by ~3× but loses variance signal

The chain is **idempotent**: if you Ctrl-C and rerun, it skips runs that already have `summary.json` and `workspace_final.tar.gz`. Safe to run overnight, check, resume.

You can monitor progress with:

```bash
ls logs/p[1-3]_*_${LABEL}_v*/ | wc -l    # how many runs started
ls logs/p[1-3]_*_${LABEL}_v*/summary.json | wc -l    # how many runs finished cleanly
```

### Step 6: Grade

```bash
bash tooling/scripts/grade_microbench.sh my-label
```

This iterates `logs/p[1-3]_*_<label>_v*/`, picks the right grader per task family, and writes `grade.json` next to each run's other artifacts. Idempotent. Takes ~5 min.

For the **5 Phase 3 tasks**, the graders emit programmatic verdicts AND `hand_rating_placeholders` for subjective dimensions (prose quality, source skepticism, citation validity, audience tone fit, etc). Filling those is a separate step:

- **Quick path**: leave them as `null` and report only the programmatic PASS/FAIL. This is honest and matches what the published microbench did originally.
- **Honest path**: hand-grade them (yourself or with a second model — record the grader provenance per the existing convention; see [`KNOWN-LIMITATIONS.md`](../KNOWN-LIMITATIONS.md) § "claude-grading-claude" for the meta-issue).
- **Rigorous path**: hand-grade with explicit rubric, sample-validate citations on the market-research entry. Documented in [`SCORECARD.md`](../SCORECARD.md) "What would change this picture" #1.

### Step 7: Summarize

```bash
bash tooling/scripts/summarize.sh my-label
```

Prints a per-task table comparing your model against the published Coder-Next + 27B reference cells:

```
Microbench results for: llama3-70b

task                   pass     cost_med   wall_med   | 27B (ref)  Coder (ref)
-----------------------------------------------------------------------------------
p1_bugfix              3/3      $0.0184    14.2m      | 3/3        2/3
p1_testwrite           0/3      $0.0098    8.1m       | 0/3 †      0/3 †
...
Total: 22/36 PASS
```

The reference column is hard-coded to the published microbench-2026-04-28 numbers, so you can see directly where your model differs.

### Step 8: Cost extraction

```bash
for d in logs/p[1-3]_*_my-label_v*/; do
  python3 tooling/scripts/extract_cost.py "$d"
done
```

Writes `cost.json` next to each run. Recorded fields: wall, completion + prompt tokens, throughput, GPU power+memory snapshot, energy upper-bound USD cost. Takes ~10s.

### Step 9: Write up

A new MMBT contribution needs at minimum:

1. **A row in `SCORECARD.md`** — under the microbench-2026-04-28 section, add a new row format showing your model. Or, if your model is dramatically different from the existing two, propose a separate section.
2. **A short findings note** — what does your model do well vs poorly relative to Coder-Next + 27B? Particularly note any task families where it inverts the existing pattern (e.g. wins where Coder-Next wins, loses where 27B wins, etc.). 1-2 pages of markdown.
3. **At least one full per-model entry** for the highest-signal task family — copy the structure from `benchmarks/microbench-2026-04-28/adversarial-hallucination/Qwen3.6-27B-AWQ/` as a template.

A more thorough contribution adds:

4. Lean per-model entries for all 12 task families (mirror the existing 9 lean entries' structure)
5. A failure-mode label.json per run, classified per [`FAILURE-TAXONOMY.md`](FAILURE-TAXONOMY.md). The published `tooling/scripts/apply_labels.py` is hand-coded per run name; you'd add a `LABELS` dict entry per run.
6. Hand-graded subjective dimensions on Phase 3 with explicit `_GRADER_` provenance.
7. Sample-validated citations on the market-research entry (the published 27B entry samples 18/33 URLs; you'd do the same on yours).

### Step 10: Submit a PR

```bash
git checkout -b add-<model-label>-microbench-results
git add SCORECARD.md benchmarks/microbench-2026-04-28/<your-additions>
git commit -m "Add <model> microbench results"
git push -u origin add-<model-label>-microbench-results
gh pr create --title "Add <model> microbench results" --body "..."
```

PR template suggestions:
- Headline pass-rate (e.g. "23/36 PASS, comparable to 27B's 17/30 excluding test-design rows")
- 2-3 specific cells where your model differs interestingly from the published baselines
- Cost-per-attempt comparison
- Anything you noticed about failure modes that isn't captured in the taxonomy

## Common pitfalls

- **Skipping the smoke test.** Wastes hours on a 3-7 hour chain that was always going to fail at iter 1. The smoke test exists for this exact reason.
- **Running before vLLM is fully ready.** vLLM takes 30-90s to load weights and another 20-60s to compile CUDA graphs. Poll `/v1/models` until 200, don't assume readiness.
- **Reading `cost.json` as actual energy cost.** It's `cost_usd_upper_bound` — assumes the GPU drew at `power.limit` for the entire wall time. Real draw is significantly lower. Useful for ranking, not for absolute economics.
- **Drawing strong conclusions from a single N=3 run.** Confidence intervals on N=3 are wide. Treat point estimates as point estimates.
- **Cherry-picking-best-of-N without saying so.** The MMBT convention for the older benchmarks is "publish best of N with explicit variance discussion." For the microbench, the convention shifted to "publish N=3 PASS rate so variance is visible." Pick one and be clear.
- **Not pinning the harness git SHA.** Receipts capture this automatically, but if you modified `harness.py` for a new tool-call parser or schema, commit those changes BEFORE running the chain. Receipts with `git_dirty: true` aren't reproducible.

## What if I'm not on Tower2-class hardware?

The published flags assume 96 GB GPUs. Smaller setups need adjustments:

| Hardware | Likely changes |
|---|---|
| 1× RTX 4090 (24 GB) | `--max-model-len 16384`, `--gpu-memory-utilization 0.85`. Models >7B at 4-bit might OOM. |
| 1× RTX 5090 (32 GB) | `--max-model-len 32768`. Most 7B-13B-class works fine. |
| 1× RTX 6000 Ada (48 GB) | `--max-model-len 65536`. 27B-class at 4-bit fits. |
| 1× H100 (80 GB) | Default flags work for most models up to ~32B AWQ-4bit |
| 2× 24-48 GB | Use `--tensor-parallel-size 2` for larger models |

If `--max-model-len` is too low for a task's prompt, the harness will hit "completion_token_cap" and the run will FAIL with a non-substantive cause. The microbench tasks rarely exceed 30k tokens of context, so 32-65k should be comfortable.

## Cost / time budget cheatsheet

For one new model, full microbench at N=3:

| Item | Tower2-class | Smaller GPU |
|---|---|---|
| Smoke test | 3 min | 5 min |
| Full chain (12 tasks × N=3) | 3-7 hr | 6-15 hr |
| Grading | 5 min | 5 min |
| Cost extraction | 10 sec | 10 sec |
| Hand-grading Phase 3 | 30-60 min (claude) / 2-4 hr (human) | same |
| Citation validation on market-research | 30-60 min | same |
| Write-up + PR | 1-3 hr | same |
| **Total** | **~6-12 hr** | **~10-20 hr** |

Operator time is roughly 4-6 hours of focused work spread over a day or two. Compute time is mostly unattended.

## What this benchmark won't tell you

- How your model performs at higher N (N=10+ on the highest-signal cells)
- How your model performs on a different hardware profile (cost numbers don't normalize)
- How your model performs vs cloud LLMs on these tasks (no cloud entries here yet)
- How your model performs on tasks not in this suite (this is 12 task families, not the universe of agentic work)
- Per-claim factual accuracy on long-form outputs (graders cover keyword presence + structure; deep fact-by-fact is hand-grading)

These are listed in [`KNOWN-LIMITATIONS.md`](../KNOWN-LIMITATIONS.md) and [`SCORECARD.md`](../SCORECARD.md) "What would change this picture." If your contribution moves the needle on any of them, that's a high-value add.

## Questions / issues

Open a GitHub issue on [Light-Heart-Labs/MMBT-Messy-Model-Bench-Tests](https://github.com/Light-Heart-Labs/MMBT-Messy-Model-Bench-Tests/issues) with:
- Your model + quantization
- Your hardware profile
- The smoke-test output if it failed (`logs/smoke_*/transcript.jsonl` first 50 lines is usually enough to diagnose tool-call-parser issues)
