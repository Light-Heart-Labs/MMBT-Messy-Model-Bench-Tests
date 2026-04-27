# MMBT — Messy Model Bench Tests

Working repo for agentic-LLM benchmarks conducted on Tower2 (WRX90E, TR PRO 7965WX, 2× RTX PRO 6000 Blackwell, 252 GB RAM). The "Messy" framing is intentional — the harness was iteratively fixed during the runs (see `agent-pilot/HARNESS-CHANGELOG.md`), some tasks exposed model failure modes that informed the harness design itself, and we keep the unsuccessful runs in the record because the *kinds* of failure are themselves diagnostic. Commits are the audit trail; receipts are the reproducibility artifact; findings synthesize across runs.

## Tasks (in order added)

| task | shape | what it measures |
|---|---|---|
| `agent-pilot/task_investment_memo.md` | open-ended research, ~1 hr expected | depth in unbounded-search territory (pick a $1-10B company, build a memo) |
| `agent-pilot/task_board_presentation.md` | bounded-input, ~30 min | execution against a pre-staged input (build a deck from an earlier memo run) |
| `agent-pilot/task_code_adoption.md` | concrete codebase, ~30-60 min | bug surgery + test design + perf, with programmatic grading via `agent-pilot/graders/` |
| `agent-pilot/task_dreamserver_pr_audit.md` | real public repo, 75 PRs, multi-hour | long-horizon agentic work — does the model hold quality under scope? |
| `agent-pilot/task_pr_audit_n1.md` | single PR (#1057) | the floor of the PR-audit family; built after the 75-PR runs revealed scale-related failures and we needed to find each model's ceiling rather than just confirm "all three fail at the top" |

The full `task_pr_audit_*.md` ladder (1, 2, 4, 8, 16, 32 PRs, nested) was sketched after N=1 produced enough signal to update the daily-driver picture; only N=1 has been run.

## Layout

```
agent-pilot/                 Agent-task harness (vLLM tool-calling loop, Docker sandbox)
  harness.py                 Runs (model × task) → records transcript + workspace
  Dockerfile                 The sandbox image (python + git + gh + docker CLI + analysis libs)
  task_*.md                  Task prompts, one per evaluation
  launch-commands.md         Canonical vLLM `docker run` form per model
  HARNESS-CHANGELOG.md       Why the harness has its current shape — log of bugs/findings that motivated each change
  logs/<run>/                Per-run artifacts (receipt.json, transcript.jsonl, summary.json, workspace tarball)
  workspace/                 Live sandboxes for in-flight runs (gitignored)
  inputs/                    Pre-staged inputs for tasks that consume earlier runs
  canonical-deliverables/    Curated successful outputs from prior batches
  graders/                   Programmatic graders for the code-adoption task

findings/                    Narrative writeups, dated. Read these first.
qwen3.5-397b/                Earlier Qwen3.5-397B-A17B llama.cpp benchmarking (separate work, kept for reference)
suite/                       General benchmark scratch
results/                     Aggregated cross-run summaries (when there are multiple)
REPRODUCING.md               Setup-to-rerun walkthrough for external readers
```

External (not tracked here, but part of the same research):

```
~/thermal-tests/     Burn-in / thermal harness (dual-GPU + CPU stress, CSV logger)
~/models/            Persistent model library (FP8, AWQ, BF16, GGUFs)
```

## How to read this repo

1. **Start with `findings/`** — the narrative writeups synthesize across runs. The most recent ones are the cleanest entry points:
   - `findings/2026-04-27-dreamserver-pr-audit-summary.md` — three local 30B-class models, three different ways of failing the PR-audit task class. Includes the N=1 escalation results and the daily-driver implications
   - `findings/2026-04-26-2x3x3-grid-consolidated.md` — the prior batch (memo + board × three models × three replicates each). Establishes the baseline behavior of each model on bounded vs unbounded tasks
2. **For a specific run referenced in a finding**, the artifacts are at `agent-pilot/logs/<run>/`:
   - `receipt.json` — vLLM args, harness git SHA, task SHA, GPU snapshot, sandbox runtime config
   - `transcript.jsonl` — full model+tool trace
   - `summary.json` — final state (only present for clean exits)
   - `workspace_final.tar.gz` — the agent's complete final workspace
3. **For the harness itself**, `agent-pilot/HARNESS-CHANGELOG.md` documents each substantive change with the bug or finding that motivated it. Useful context for why specific flags exist.

## Reproducing a run

`REPRODUCING.md` is the full walkthrough — flags, models, troubleshooting, how to replay a specific past run from its receipt. Quick form for the impatient:

```bash
# 1. Build sandbox image (one-time, ~1.5 GB)
docker build -t bench-sandbox:latest agent-pilot/

# 2. Start a vLLM endpoint (use the canonical command from agent-pilot/launch-commands.md)
docker run -d --name vllm-coder-next --gpus '"device=0"' --shm-size 8g \
  -v ~/models:/models:ro -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit \
  --served-model-name qwen3-coder-next-awq \
  --host 0.0.0.0 --port 8000 --tensor-parallel-size 1 \
  --max-model-len 262144 --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# 3. Wait for vLLM to be ready (loading + CUDA graph capture takes 60-150 s)
until curl -sf http://127.0.0.1:8001/v1/models >/dev/null; do sleep 5; done

# 4. Run a task
python3 agent-pilot/harness.py my_run_name agent-pilot/task_pr_audit_n1.md \
  --model qwen3-coder-next-awq --port 8001 \
  --temperature 0.3 --stuck-threshold 500 \
  --docker-socket --gpus all
```

Outputs land in `agent-pilot/logs/<run_name>/`. A live progress log streams to stdout (one line per iter — see `REPRODUCING.md` for the format).

### Flags worth knowing

| flag | typical value | why |
|---|---|---|
| `--temperature` | 0.3 for agentic tasks | At temp=0.0 + seed=42, models can fall into deterministic fixed-point loops on long-horizon work. 0.3 breaks the trap. |
| `--stuck-threshold` | 80-500 for long-horizon tasks | The default 30 was tuned on memo/board-scale tasks (~100-iter shape). Long-horizon work does legitimate read-only recon that doesn't change the workspace hash; 30 punishes that. |
| `--docker-socket` | on for tasks that test installer/container behavior | Mounts host docker socket. Sandbox can spawn sibling containers. Root-equivalent on the host daemon. |
| `--gpus` | `all` for tasks that exercise GPU code paths | Pass-through to `docker run --gpus`. Sandbox shares GPUs with the vLLM container. |
| `--gh-token` | `@gh` (or `@env`, or literal) | GitHub auth in the sandbox. Token never recorded in receipts. |

Full flag table in `REPRODUCING.md`.

## Conventions

- **Commit messages explain *why*, not what.** The runs themselves are the "what" — receipts capture the launch flags and transcripts capture the per-iter work. Commits document why a harness flag was added, why a verdict was assessed wrong, why a run was killed.
- **Findings are dated and topic-named**: `findings/YYYY-MM-DD-<short-topic>.md`. Cross-cutting writeups go here; per-run analysis goes in commit messages.
- **Run names are unique** — the harness `rm -rf`s the workspace dir at start. Reusing a name destroys the prior run's working state (the `workspace_final.tar.gz` in `logs/<run>/` is the canonical preserved copy regardless).
- **Receipts are mandatory.** Every run writes `receipt.json` before the loop starts. Every claim about a run should be checkable from its receipt + transcript + workspace tarball.
- **Approximate determinism**: vLLM bf16 paths aren't bitwise deterministic, so `temperature=0.0 + seed=42` doesn't give identical runs. Plan N≥3 per (model × task) for any claim about model behavior.
- **Tool calling is required for agent tasks**: vLLM launched with `--enable-auto-tool-choice --tool-call-parser <model-specific>`. Wrong parser silently gives empty `tool_calls` arrays — it's the most common silent-failure on a fresh setup.
