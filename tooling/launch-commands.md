# Canonical vLLM launch commands

Exact `docker run` commands for each model under test. Each run's `logs/<run>/receipt.json` records the actual container Args at run time, so this file documents the *intended* canonical form for new launches.

## Context

- Host: Tower2 (WRX90E, TR PRO 7965WX, 2× RTX PRO 6000 Blackwell, 96 GB each)
- vLLM image: `vllm/vllm-openai:latest` (resolves to vLLM 0.19.1 as of 2026-04-26 — check image digest in each run's receipt for the exact pin)
- Sandbox image: `bench-sandbox:latest` (built from `agent-pilot/Dockerfile`)
- Models live at: `~/models/<org-name>-<model>/`
- Mount convention: `-v ~/models:/models:ro`
- GPU power cap on Tower2: 535 W per GPU (set via `sudo nvidia-smi -i 0,1 -pl 535`; resets on reboot to default 600)

## Conventions

- Each model gets its own container; we don't share containers across models
- Container names: `vllm-<short-name>`
- Host port: 8000 for GPU1's primary model, 8001 for GPU0's primary model
- `--gpu-memory-utilization 0.92` is the default (vLLM allocates ~88 GB of the 96 GB)
- `--max-model-len 262144` matches the native context for the Qwen3.x family
- `--temperature 0.0` is set per-request in the harness (not at launch); receipts record it
- `--tensor-parallel-size 1` for now (each model on a single GPU); change if both GPUs are needed for one model

## Per-model launch

### Qwen3.6-27B AWQ (dense, thinking-mode)

```bash
docker run -d \
  --name vllm-qwen36-awq \
  --gpus '"device=1"' \
  --shm-size 8g \
  -v ~/models:/models:ro \
  -p 127.0.0.1:8000:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3.6-27B-AWQ-INT4 \
  --served-model-name qwen3.6-27b-awq \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.92 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml
```

Flags rationale:
- `--reasoning-parser qwen3` — model emits `<think>...</think>` sections; parser splits them into `reasoning_content` so `content` only contains the final answer. Without this, the answer ends up nested inside `content` mixed with thinking.
- `--tool-call-parser qwen3_xml` — Qwen3.6 dense models emit tool calls in XML form (`<function name="..."><parameter ...>`). The `qwen3_xml` parser extracts these into the standard OpenAI `tool_calls` array.

### Qwen3-Coder-Next AWQ (MoE 80B/3B, agentic)

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

Flags rationale:
- **No `--reasoning-parser`** — Coder-Next is not a thinking-mode model. Adding `--reasoning-parser qwen3` causes the entire output to be misclassified into the `reasoning` field, leaving `content` empty (we hit this exact bug in the first round of testing — see `findings/2026-04-26-coder-next-investment-memo-pilot.md`).
- `--tool-call-parser qwen3_coder` — Coder-Next was trained on the Qwen3-Coder tool format (different from `qwen3_xml`).

### Qwen3.6-35B-A3B AWQ (MoE 35B/3B, thinking-mode)

> Swap candidate for GPU0 (alternates with Coder-Next). Used in the 2026-04-26 grid (1/6 across memo+board) and the 2026-04-27 PR-audit family. Disqualified from the daily-driver comparison after a floor failure at N=1 PR audit (`n1_35ba3b_v1`: zero artifacts written in 28 iters before model_stopped) — kept here for replay.

```bash
docker rm -f vllm-coder-next   # free GPU0 first
docker run -d \
  --name vllm-qwen36-35ba3b \
  --gpus '"device=0"' \
  --shm-size 8g \
  -v ~/models:/models:ro \
  -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3.6-35B-A3B-AWQ-4bit \
  --served-model-name qwen3.6-35ba3b-awq \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.92 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml
```

Flags rationale: same pattern as the 27B since 35B-A3B is also a Qwen3.6-family thinking model.

### Qwen3.6-27B-FP8 (official, 8-bit, thinking-mode)

> Reference variant. 8-bit is bandwidth-heavier per token; useful for FP8-vs-AWQ comparison.

```bash
docker run -d \
  --name vllm-qwen36-fp8 \
  --gpus '"device=1"' \
  --shm-size 8g \
  -v ~/models:/models:ro \
  -p 127.0.0.1:8000:8000 \
  vllm/vllm-openai:latest \
  --model /models/Qwen-Qwen3.6-27B-FP8 \
  --served-model-name qwen3.6-27b-fp8 \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.92 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --speculative-config '{"method":"mtp","num_speculative_tokens":1}'
```

Flags rationale: only the FP8 build ships the MTP heads (`mtp.safetensors` in the repo); enabling `--speculative-config` here gets free decode speedup. AWQ builds don't include MTP, so the flag is omitted there.

## Inference-request defaults (set by harness, not at launch)

Recorded in every receipt under `inference_request_defaults`. Current values:

- `temperature`: configurable per-run via `--temperature` (default 0.0). Receipts reflect the actual value used. 0.3-0.5 is recommended for agentic tasks (see HARNESS-CHANGELOG `--temperature` entry for the determinism trap that motivated making it configurable).
- `max_tokens` per request: dynamically computed as `min(180000, max_model_len - last_prompt_tokens - 14000)` to leave headroom for prompt growth as conversation history accumulates. Floor is 2048.
- `max_model_len`: 262144 (the Qwen3.x family's native context)
- `seed`: 42 on every request (kept for replay reproducibility; harmless at non-zero temperature)
- `stream`: false (we capture full responses; streaming would help for live progress but complicates token accounting)
- `tool_choice`: "auto"
- `tools`: `bash`, `write_file`, `read_file`, `done`

## Sandbox image

`bench-sandbox:latest` rebuild:

```bash
docker build -t bench-sandbox:latest <this-tooling-dir>/
```

Contents (see `agent-pilot/Dockerfile`):
- python 3.11-slim base
- system tools: git, curl, jq, poppler-utils (PDF extraction), unzip, build-essential, graphviz, font packages, cairo/pango (for python-pptx + reportlab rendering)
- `gh` CLI (from cli.github.com's apt repo) — for tasks that read GitHub PRs/issues
- `docker` CLI (static binary from download.docker.com) — talks to the host daemon when `--docker-socket` is passed
- python libs: requests, beautifulsoup4, lxml, pandas, numpy, openpyxl, yfinance, sec-edgar-downloader, markdown, reportlab, python-pptx, matplotlib, plotly, kaleido, Pillow, graphviz, pytest, pytest-cov, ruff

The image digest at run time is in each receipt under `sandbox.image_id`. Per-run sandbox config (whether `--docker-socket`, `--gpus`, `--gh-token`, `--input-mount` were passed) lands in `sandbox.runtime`.

## Auditing a past run

```bash
cat agent-pilot/logs/<run>/receipt.json | jq '.vllm.containers[].args'      # see exact launch flags
cat agent-pilot/logs/<run>/receipt.json | jq '.harness'                      # harness git SHA + dirty flag + sha256
cat agent-pilot/logs/<run>/receipt.json | jq '.task'                         # task file SHA
cat agent-pilot/logs/<run>/receipt.json | jq '.hardware.nvidia_smi'          # GPU state at start
```

If any of those changed and you want to re-run identically: `git checkout <harness_git_sha>`, rebuild the sandbox image (use the Dockerfile from that SHA), launch vLLM with the captured args, then run the harness.
