# Tower2 evals

Working repo for benchmarks, capability tests, and research conducted on Tower2
(WRX90E, TR PRO 7965WX, 2× RTX PRO 6000 Blackwell). Commits are the audit trail.

## Layout

```
agent-pilot/         Agent-task harness (vLLM tool-calling loop, Docker sandbox)
  harness.py         Runs (model × task) → records transcript + workspace
  Dockerfile         The sandbox image (python + git + curl + financial libs)
  task_*.md          Task prompts, one per evaluation
  logs/<run>/        Per-run artifacts (transcript.jsonl, summary.json, workspace tarball)
  workspace/         Live sandboxes for in-flight runs (gitignored)

qwen3.5-397b/        Earlier Qwen3.5-397B-A17B llama.cpp benchmarking
suite/               General benchmark scratch
findings/            Narrative writeups, dated, one per session/topic
results/             Aggregated cross-run summaries (when we have multiple)
```

External (not tracked here, but part of the same research):

```
~/thermal-tests/     Burn-in / thermal harness (dual-GPU + CPU stress, CSV logger)
~/models/            Persistent model library (FP8, AWQ, BF16, GGUFs)
```

## How to read this repo

1. Start with the latest entry in `findings/` for what was learned most recently.
2. For any specific run referenced in a finding, the artifacts are at
   `agent-pilot/logs/<run-name>/` — `summary.json` for the metrics,
   `transcript.jsonl` for the full model+tool trace, and
   `workspace_final.tar.gz` for the agent's final repo state.
3. Task prompts in `agent-pilot/task_*.md` are the test definitions; the
   harness runs them through whichever vLLM endpoint is configured.

## Reproducing a run

```
# Start a vLLM endpoint serving the model under test (e.g. on :8001)
docker run -d --name vllm-coder-next --gpus '"device=0"' --shm-size 8g \
  -v /home/michael/models:/models:ro -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit \
  --served-model-name qwen3-coder-next-awq \
  --host 0.0.0.0 --port 8000 --tensor-parallel-size 1 \
  --max-model-len 262144 --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# Build the sandbox image (one-time)
docker build -t bench-sandbox:latest agent-pilot/

# Run a task through the harness
python3 agent-pilot/harness.py <run_name> agent-pilot/task_investment_memo.md \
  --model qwen3-coder-next-awq --port 8001
```

Outputs land in `agent-pilot/logs/<run_name>/`.

## Conventions

- Commit messages explain *why*, not what. The agent runs themselves are
  the "what" — the commits document changes to the harness, tasks, and
  findings.
- Findings are dated and topic-named: `findings/YYYY-MM-DD-<short-topic>.md`.
- Each run gets a unique name; never reuse a run name (it'd nuke the prior
  workspace via the harness's `rm -rf` step).
- Models on vLLM are served at the OpenAI-compatible `/v1/chat/completions`
  endpoint. Tool calling is required for agent tasks (`--enable-auto-tool-choice
  --tool-call-parser <model-specific>`).
