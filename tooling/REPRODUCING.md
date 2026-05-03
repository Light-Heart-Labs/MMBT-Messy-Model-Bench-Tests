# Reproducing a run

This walks an external reader from "fresh checkout" through running one of the benchmark tasks end-to-end. The agent harness is unfussy but has several moving parts (vLLM endpoint per model, sandbox container, mounted GPUs) that need to line up. Most pain happens at the seams.

## What you need

**Hardware**: a Linux box with at least one CUDA-capable GPU. Most of the runs in `logs/` were on Tower2 (2× RTX PRO 6000 Blackwell, 96 GB each, 252 GB RAM, TR PRO 7965WX). Smaller GPUs work but you'll need to drop `--max-model-len` and `--gpu-memory-utilization` accordingly. The harness itself is GPU-agnostic; only the vLLM containers care.

**Software**:
- Docker (with NVIDIA Container Toolkit if you're running models on GPU — `docker run --gpus all` needs to work)
- Python 3.10+ on the host (the harness is `python3 harness.py`; only depends on the standard library)
- ~50 GB free disk for vLLM image + at least one model

**Models**: The benchmark uses Qwen3-family models hosted locally. Download whatever you want to test to a directory you'll mount read-only into the vLLM container. Path convention here is `~/models/<org>-<model-name>/`. Three are tracked in `launch-commands.md`:

- `cyankiwi-Qwen3.6-27B-AWQ-INT4` (dense thinking, ~16 GB)
- `cyankiwi-Qwen3-Coder-Next-AWQ-4bit` (MoE 80B/3B, ~45 GB)
- `cyankiwi-Qwen3.6-35B-A3B-AWQ-4bit` (MoE thinking, ~25 GB)

Cloud LLM endpoints work too — point `--model` and `--port` at any OpenAI-compatible endpoint.

## Setup (one-time)

### 1. Build the sandbox image

The agent runs every tool call inside a per-run container based on `bench-sandbox:latest`:

```bash
docker build -t bench-sandbox:latest tooling/
```

Image is ~1.5 GB. Includes Python 3.11, common analysis libs (pandas, numpy, openpyxl, yfinance, sec-edgar-downloader, reportlab, python-pptx, matplotlib), `gh` CLI, `docker` CLI (static binary, talks to the host daemon when `--docker-socket` is passed), git, curl, etc. See `Dockerfile` for the exact contents.

### 2. Pull the vLLM image

```bash
docker pull vllm/vllm-openai:latest
```

(Around 12 GB.)

### 3. Decide which model to test

Pick from `launch-commands.md`. The launch commands document the exact `docker run` form for each model — flags for tool-call parsing and reasoning-mode parsing are model-specific and getting them wrong silently breaks the run (e.g., adding `--reasoning-parser qwen3` to a non-thinking model causes all output to be misclassified as "reasoning" with empty `content`).

### 4. (Optional) Authenticate gh on the host

For tasks that hit GitHub. `gh auth login` once on the host; the harness can then pull the token via `--gh-token @gh`. Public-repo read-only tasks don't need this.

## Running a task

### 1. Start the vLLM endpoint

Copy the canonical command from `launch-commands.md` for your model. Example (Coder-Next on GPU 0, port 8001):

```bash
docker run -d \
  --name vllm-coder-next \
  --gpus '"device=0"' \
  --shm-size 8g \
  -v ~/models:/models:ro \
  -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit \
  --served-model-name qwen3-coder-next-awq \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

Wait for the endpoint to come up (loading is 30-90 s for AWQ-4bit models, longer for FP8):

```bash
until curl -sf http://127.0.0.1:8001/v1/models >/dev/null; do sleep 5; done
echo "ready"
```

### 2. Run the harness

```bash
python3 harness.py <run_name> <task_file> [flags]
```

Concrete example — N=1 PR-audit on Coder-Next:

```bash
python3 harness.py \
  my_first_run \
  tasks/task_pr_audit_n1.md \
  --model qwen3-coder-next-awq \
  --port 8001 \
  --temperature 0.3 \
  --stuck-threshold 500 \
  --docker-socket \
  --gpus all
```

### Flag reference

| flag | default | when to set |
|---|---|---|
| `<run_name>` | — | unique per run; used for sandbox container name + log dir name. Reusing a name nukes the prior workspace via the harness's `rm -rf` step. |
| `<task_file>` | — | path to one of the `tasks/task_*.md` prompts. |
| `--model` | `qwen3-coder-next-awq` | the `--served-model-name` your vLLM endpoint advertises. |
| `--port` | 8001 | the host port your vLLM endpoint is bound to. |
| `--temperature` | 0.0 | **set to 0.3-0.5 for agentic tasks**. At temp=0 with seed=42, models can fall into deterministic fixed-point loops on long-horizon work (same context → same response → same tool result → same response). 0.3 breaks the trap without much off-task drift. See HARNESS-CHANGELOG. |
| `--stuck-threshold` | 30 | iterations of unchanged workspace state hash before the harness aborts. **Bump to 80-500 for long-horizon tasks** (memo/board tasks fit in ~100 iters; PR audits need more recon-without-writes headroom). |
| `--max-iters` | 10000 | hard upper bound on iterations. Effectively unlimited; never been approached in practice. |
| `--docker-socket` | off | bind-mount `/var/run/docker.sock` so the agent can run sibling containers (e.g. installer-in-clean-container tests). Sandbox gets root-equivalent access to the host docker daemon. |
| `--gpus` | none | pass-through to `docker run --gpus`. Required for tasks that need real GPU testing. The sandbox shares GPUs with the vLLM container, so heavy in-sandbox CUDA work contends with inference. |
| `--gh-token` | none | GitHub token for the sandbox. Pass a literal token, `@env` to read `$GH_TOKEN`/`$GITHUB_TOKEN`, or `@gh` to call `gh auth token` on the host. Token value is **never written to receipt.json** — only `gh_token_set: bool`. |
| `--input-mount` | none | host path mounted read-only at `/input/repo` inside the sandbox. Used for tasks that consume a prior agent's output (board task built on an earlier memo run). |
| `--system` | none | path to a system prompt file to prepend. Not used in the canonical task runs. |

### What you'll see

The harness prints one line per iteration to stdout. Format:

```
[iter 17] 1 tool call(s)  wall=1.0s  ctok=130  ptok=7869  total_ctok=2342  no-progress=6/30  max_tok_req=180000
```

- `iter` — turn number
- `tool call(s)` — number of tool calls in the model's response (>1 if the model used parallel calls)
- `wall` — seconds spent on the model API call (not the tool execution)
- `ctok` / `ptok` — completion tokens emitted / prompt tokens consumed
- `total_ctok` — running total
- `no-progress=N/THRESHOLD` — workspace-state-hash unchanged for N iterations; harness aborts when it hits THRESHOLD
- `max_tok_req` — the dynamic max_tokens the harness requested for that turn (shrinks as the prompt grows toward `max-model-len`)

Run ends when one of: the model calls `done()`, the model emits a "stop" finish without a tool call (`model_stopped`), the no-progress counter hits the threshold, the per-call timeout (3600 s) fires, or `--max-iters` is hit.

## Where the artifacts land

```
logs/<run_name>/
  receipt.json           reproducibility metadata, written before the loop starts
  transcript.jsonl       every model turn + tool call (one line each)
  summary.json           final state (only present if the harness exited cleanly — wall-killed runs lack this)
  workspace_final.tar.gz the agent's complete workspace at end-of-run (also only on clean exit)
```

The workspace tarball is the deliverable. Most are 1-50 MB depending on what the agent fetched (cloned repos, downloaded diffs, etc.).

## Reading a receipt

```bash
cat logs/<run>/receipt.json | jq '.vllm.containers[].args'      # exact vLLM launch flags
cat logs/<run>/receipt.json | jq '.harness'                      # harness git SHA + dirty flag + sha256
cat logs/<run>/receipt.json | jq '.task'                         # task file SHA
cat logs/<run>/receipt.json | jq '.hardware.nvidia_smi'          # GPU state at start
cat logs/<run>/receipt.json | jq '.sandbox.runtime'              # the per-run flags
cat logs/<run>/receipt.json | jq '.inference_request_defaults'   # temperature, max_tokens strategy, etc.
```

## Reproducing a specific past run identically

```bash
# 1. Read the receipt
cat logs/<run>/receipt.json | jq '.harness.git_sha, .harness.git_dirty, .vllm.containers[0].args'

# 2. Checkout that harness SHA
git checkout <git_sha>

# 3. Rebuild the sandbox image from that SHA's Dockerfile
docker build -t bench-sandbox:latest tooling/

# 4. Launch vLLM with the captured args (paste the args from step 1)
docker run -d --name vllm-replay --gpus '"device=0"' [...] <captured args>

# 5. Run the harness with the same task file SHA + same flags
python3 harness.py replay_<run> <task_file> [<original flags>]
```

If `git_dirty: true` in the receipt, the run had uncommitted local changes; the SHA alone won't reproduce it. Receipts emit a warning when this happens. If you're publishing benchmark results, work from clean trees only.

## Variance is expected

Two runs of the same model on the same prompt with the same temperature **will** diverge — vLLM's bf16 paths aren't bitwise deterministic, and at any non-zero temperature the sampling diverges further. Plan for N≥3 per (model × task) when moving from pilot to formal eval. The N=1 vs N=3 distinction is documented in the findings docs.

## Troubleshooting

**"Container not found" or "endpoint not reachable"**: the vLLM container takes 30-90 s to load weights and another 20-60 s to compile CUDA graphs before the API responds. Poll `curl -sf http://127.0.0.1:<port>/v1/models` until it returns 200, don't assume readiness.

**"Empty `content` field, output ended up in `reasoning`"**: you added `--reasoning-parser qwen3` to a non-thinking model (Coder-Next is not thinking-mode). Drop the flag.

**Tool calls aren't being parsed**: the `--tool-call-parser` flag is model-specific. `qwen3_xml` for thinking-mode Qwen3.6 dense / 35B-A3B; `qwen3_coder` for Coder-Next. Wrong parser silently produces empty `tool_calls` arrays.

**Stuck-detector firing immediately on a fresh run**: probably means the model isn't calling tools at all (responses are all content, no tool_calls). Check the transcript first — if you see `tcs=0` consistently, your `--tool-call-parser` flag is wrong.

**Sandbox sees no GPUs**: pass `--gpus all` to the harness. Without it the sandbox runs CPU-only.

**Sandbox can't reach `docker`**: pass `--docker-socket`. The sandbox image ships the docker CLI binary, but it needs the host socket to do anything.

**`gh` rate-limited at 60 req/hr**: that's the unauth ceiling. Either `gh auth login` on the host and use `--gh-token @gh`, or restructure the agent's behavior to clone the repo locally and use `git fetch refs/pull/*/head` instead of per-PR API calls.

## What's not covered here

- **Power capping the GPUs**: per-GPU `nvidia-smi -i <idx> -pl <watts>`. Tower2 runs uncapped at 600 W per GPU; some prior runs were at 535 W. The receipts capture the actual `power.limit` at run start.
- **Model swapping**: `docker rm -f vllm-<old>` then `docker run` the new one. Takes 60-90 s end-to-end.
- **Cloud-LLM endpoints**: any OpenAI-compatible URL works. Skip steps 1-2 of "Setup" and just point `--port` at the proxy / local litellm / wherever.

---

## Reproducing the microbench (`benchmarks/microbench-2026-04-28/`)

The microbench has 12 task families. Each task family has its own task prompt, starter input directory, and grader script. All three live in this `tooling/` folder.

### Layout

```
tooling/
  tasks/
    task_extraction.md          # Phase 2: structured extraction
    task_ci_failure.md          # Phase 2: CI failure debugging
    task_hallucination.md       # Phase 2: adversarial hallucination
    task_triage.md              # Phase 2: customer support triage
    task_doc_synthesis.md       # Phase 3: document synthesis
    task_business_memo.md       # Phase 3: business memo
    task_market_research.md     # Phase 3: market research
    task_writing_editing.md     # Phase 3: 3-audience writing/editing
    task_project_mgmt.md        # Phase 3: project management synthesis
    task_test_writing.md        # Phase 1: test writing
    task_refactoring.md         # Phase 1: refactoring
    task_code_adoption.md       # Phase 1: bug fixing (reused)

  inputs/
    phase2_extraction/          # press release for the agent to extract
    phase2_ci_failure/          # discountkit project + ci_failure.log
    phase2_hallucination/       # 15-issue report + logalyzer source
    phase2_triage/              # 30 hand-written tickets
    phase3_business_memo/       # Borealis Analytics deal pack
    phase3_doc_synthesis/       # 5 docs about Nimbus Logistics
    phase3_writing_editing/     # outage post-mortem + audience briefs
    phase3_project_mgmt/        # 6 weeks of Project Aurora notes
    # phase3_market_research has no input — agent gets a free internet sandbox

  graders/
    phase1_grade.py             # bug-fix / test-write / refactor scoring
    phase2_extraction_grade.py
    phase2_ci_failure_grade.py
    phase2_hallucination_grade.py
    phase2_triage_grade.py
    phase3_doc_synthesis_grade.py
    phase3_business_memo_grade.py
    phase3_market_research_grade.py
    phase3_writing_editing_grade.py
    phase3_project_mgmt_grade.py
    ground_truth/               # planted-answer files — kept SEPARATE from inputs/
      phase2_extraction.json    # so agents can't see the answers when grading
      phase2_hallucination.json
      phase2_triage.json
      phase3_doc_synthesis.json
      phase3_business_memo.json
      phase3_market_research_rubric.json
      phase3_project_mgmt.json
```

### Concrete reproduction example — adversarial hallucination on 27B

```bash
# 1. Start vLLM serving 27B on port 8001 (see launch-commands.md for the exact docker run)

# 2. Run the harness against the task prompt + input dir
python3 harness.py \
  my_hallucination_v1 \
  tooling/tasks/task_hallucination.md \
  --model qwen3.6-27b-awq \
  --port 8001 \
  --temperature 0.3 \
  --stuck-threshold 500 \
  --input-mount tooling/inputs/phase2_hallucination \
  --docker-socket --gpus all

# 3. Extract the workspace and grade
mkdir -p /tmp/grade_my_hallucination_v1
tar -xzf logs/my_hallucination_v1/workspace_final.tar.gz -C /tmp/grade_my_hallucination_v1
python3 tooling/graders/phase2_hallucination_grade.py \
  /tmp/grade_my_hallucination_v1 \
  tooling/graders/ground_truth/phase2_hallucination.json \
  --out logs/my_hallucination_v1/grade.json

# 4. Read the verdict
jq '{verdict, scores}' logs/my_hallucination_v1/grade.json
```

### Task-family → flags mapping

Most microbench tasks need `--input-mount <path-to-input-dir>`. Three exceptions:

| Task | Input | Other flags |
|---|---|---|
| `task_market_research.md` | none — agent gets unrestricted internet bash | `--stuck-threshold 500` |
| `task_code_adoption.md` (bug-fix) | `inputs/logalyzer/` if running locally; the prompt fetches the starter from a path you specify | check task prompt |
| `task_test_writing.md`, `task_refactoring.md` | same logalyzer starter as bug-fix | check task prompt |

For the rest: `--input-mount tooling/inputs/<phase_taskname>/`.

### Grader invocation pattern

All graders take the same form:

```bash
python3 tooling/graders/<task>_grade.py <workspace_dir> <ground_truth_json> [--out grade.json]
```

The `<workspace_dir>` is wherever you extracted the agent's `workspace_final.tar.gz`. The `<ground_truth_json>` is the planted-answer file from `tooling/graders/ground_truth/`.

Graders for the open-ended Phase 3 tasks (doc-synthesis, business-memo, market-research, writing-editing, project-mgmt) emit programmatic verdicts plus `hand_rating_placeholders` for subjective dimensions you'd hand-grade. The published microbench entries have those placeholders filled (graded by Claude Opus 4.7 — see `KNOWN-LIMITATIONS.md` § "claude-grading-claude" for the meta-issue).

### Batch-running the full microbench

The `scripts/` folder doesn't include the batch chain runners (those are bench-side conveniences and would need adapting per-host), but the pattern is:

```bash
for task_family in extraction ci_failure hallucination triage doc_synthesis business_memo writing_editing project_mgmt market_research; do
  for v in v1 v2 v3; do
    python3 harness.py "p_${task_family}_${MODEL}_${v}" \
      "tooling/tasks/task_${task_family}.md" \
      --model "$MODEL" --port 8001 \
      --temperature 0.3 --stuck-threshold 500 \
      ${INPUT_DIR:+--input-mount "tooling/inputs/${INPUT_DIR}"} \
      --docker-socket --gpus all
  done
done
```

The microbench runs in this repo took 3-7 hours per model (15 runs × 5-30 minutes each, including 2 manually-advanced 27B doc-synthesis stuck-loops). Budget overnight if you're running both Coder-Next and 27B end-to-end.

### Caveats specific to microbench reproduction

- **Live data drift**: `task_market_research.md` requires the live web. Pricing, certifications, security incidents change over time. The published 27B entry's `sources.md` documents a 2026-04-28 snapshot; running the same task now will see updated data.
- **Hand-grading subjectivity**: The Phase 3 graders' `hand_rating_placeholders` need a human (or a different model) to fill. The published entries used Claude Opus 4.7 as the grader; that's a meta-issue (claude-grading-claude). For a research-grade reproduction, plan a hand-grading pass.
- **Two manually-advanced 27B doc-synthesis runs in the published data**: see `KNOWN-LIMITATIONS.md`. If you reproduce, the same `identical-call-loop` on `brief.md` will likely happen — either let `--stuck-threshold` fire (~5 hours wall) or SIGTERM the harness manually after ~50+ same-content writes.
- **For long bench chains, run [`scripts/check_substance.py`](scripts/check_substance.py) every 5 min on every active transcript.** It catches `scroll-loop` and `runaway-generation` pathologies hours before the harness's own `--stuck-threshold` fires. Exit code 1 = SIGTERM the harness PID per the documented `>30 same-content writes` methodology rule. See [`scripts/SUBSTANCE-MONITORING-WORKFLOW.md`](scripts/SUBSTANCE-MONITORING-WORKFLOW.md) for the full workflow + quantified GPU-hours saved on the `microbench-phase-b-2026-05-02` chain (~10-14 GPU-hours).
