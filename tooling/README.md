# tooling/ — the harness, task prompts, and scripts that produced the entries

This folder is the *reproduction pack*. With everything here, plus a CUDA-capable Linux box, plus the Cyankiwi quantizations of the Qwen3.x models from HuggingFace, an external reader can rerun any of the local-model entries in this repo and see how their results compare.

It exists because the entry READMEs and findings docs only show *deliverables and analysis* — they describe what happened but don't let you actually run the experiments. This pack closes that gap.

## What's here

```
tooling/
  harness.py              The agent-task harness — vLLM tool-calling loop +
                          per-run Docker sandbox. ~600 lines, stdlib-only,
                          stream-friendly logging. Reads a task file, drives
                          a model through the bash/write_file/read_file/done
                          tool loop, captures everything in a receipt +
                          transcript + final workspace tarball.
  Dockerfile              The bench-sandbox image. python:3.11-slim +
                          standard CLI tools + analysis libs + gh CLI +
                          docker CLI (static binary). ~1.5 GB built.
  launch-commands.md      Canonical vLLM `docker run` for each model
                          (Qwen3.6-27B-AWQ, Qwen3-Coder-Next-AWQ,
                          Qwen3.6-35B-A3B-AWQ, Qwen3.6-27B-FP8). Includes
                          flag rationale per model — getting the
                          tool-call-parser or reasoning-parser wrong
                          silently breaks the run.
  REPRODUCING.md          Setup-to-rerun walkthrough for an external reader.
                          Covers prereqs, build, vLLM launch, harness usage,
                          where artifacts land, troubleshooting common
                          silent failures.
  HARNESS-CHANGELOG.md    Why each harness flag exists. Documents the
                          determinism trap, the stuck-threshold tuning,
                          the strict-done ablation, and other findings
                          that motivated each change. Useful for
                          understanding why the harness has its current shape.
  FAILURE-TAXONOMY.md     The 13-entry vocabulary used in label.json files
                          across the entries (success-shipped,
                          partial-no-spec-output, scaffold-and-stop,
                          identical-call-loop, cyclic-name-slop,
                          stuck-in-research, floor-failure, timeout, etc.).
  tasks/
    task_dreamserver_pr_audit.md    The 75-PR audit task spec
    task_pr_audit_n1.md             The single-PR variant (escalation floor)
    task_investment_memo.md         The wallstreet investment-memo task
    task_board_presentation.md      The follow-on board-deck task
    task_code_adoption.md           A separate code-bug-surgery task
                                    (used in the consolidated 2026-04-26
                                    grid; not currently published as MMBT
                                    entries)
  scripts/
    extract_cost.py                 Post-hoc cost/throughput metrics
                                    extraction from receipt + transcript.
                                    Produces cost.json sibling.
    apply_labels.py                 The hand-labeling script for failure
                                    modes. Run-name → label mapping is
                                    in the script body. Re-run after
                                    edits to refresh label.json files.
```

## Quick start

```bash
# 1. Build sandbox (one-time, ~1.5 GB)
docker build -t bench-sandbox:latest tooling/

# 2. Pull vLLM image
docker pull vllm/vllm-openai:latest

# 3. Download a model (e.g. Coder-Next AWQ-4bit) to ~/models/
huggingface-cli download cyankiwi/Qwen3-Coder-Next-AWQ-4bit --local-dir ~/models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit

# 4. Start a vLLM endpoint (use the canonical command from launch-commands.md)
docker run -d --name vllm-coder-next --gpus '"device=0"' --shm-size 8g \
  -v ~/models:/models:ro -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3-Coder-Next-AWQ-4bit \
  --served-model-name qwen3-coder-next-awq \
  --host 0.0.0.0 --port 8000 --tensor-parallel-size 1 \
  --max-model-len 262144 --gpu-memory-utilization 0.92 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder

# 5. Wait for ready
until curl -sf http://127.0.0.1:8001/v1/models >/dev/null; do sleep 5; done

# 6. Run a task — outputs land in tooling/logs/<run_name>/
python3 tooling/harness.py my_first_run tooling/tasks/task_pr_audit_n1.md \
  --model qwen3-coder-next-awq --port 8001 \
  --temperature 0.3 --stuck-threshold 500 \
  --docker-socket --gpus all
```

`REPRODUCING.md` has the full version with all the flag explanations, hardware-equivalence notes for smaller GPUs, and troubleshooting.

## Mapping entries to runs

Each MMBT entry is the published deliverable from one specific run. To replay an entry exactly (modulo bf16 non-determinism), use the receipt that will land in PR C of the local-model addition sequence:

```bash
cat benchmarks/<task>/<model>/receipt.json | jq '.vllm.containers[0].args'   # vLLM launch args
cat benchmarks/<task>/<model>/receipt.json | jq '.harness.git_sha'            # which harness version
cat benchmarks/<task>/<model>/receipt.json | jq '.task.sha256'                # which task file SHA
cat benchmarks/<task>/<model>/receipt.json | jq '.sandbox.runtime'            # the per-run flags used
```

The current `tooling/harness.py` may have moved past the harness git SHA pinned in any specific receipt. To replay a past run identically: check out the source bench repo's git tree at that SHA, rebuild the sandbox image from the corresponding Dockerfile, then run the harness. For new runs against current `tooling/`, results will diverge in the variance band the entries already document.

## Caveats

**Approximate determinism only.** vLLM bf16 paths aren't bitwise-deterministic, so even at `--temperature 0.0 --seed 42` two runs of the same model on the same prompt will diverge. We operate at `--temperature 0.3` for current PR-audit runs to break deterministic loop traps; that adds intentional variance on top of the bf16 non-determinism. Expect the same model on the same task to produce different outcomes between runs — the entries' READMEs document the variance characterized at N=3.

**Live data drift.** Tasks that reference real public state (DreamServer PRs, SEC filings, market prices) will see that state drift over time. Receipts pin a baseline commit for the DreamServer task; for the wallstreet task there's no such anchor since the company-pick is the agent's decision. Take time-of-run into account when comparing across replicates.

**Hardware variation.** All published runs were on a workstation with 2× RTX PRO 6000 Blackwell (96 GB each). Smaller GPUs work — drop `--max-model-len` to 32768-65536 and `--gpu-memory-utilization` to 0.85 — but token-throughput numbers and time-to-X metrics will differ. Don't compare cost.json between hardware setups without normalization.

**Quantization specificity.** The Cyankiwi 4-bit AWQ quantizations are community releases. Different quants of the same base model (FP8, BF16, different AWQ tools) will behave differently. The entries pin specific HuggingFace model paths; respect those when comparing.

## Privacy / sanitization note

This pack was extracted from a private working bench repo. A scrub pass replaced personal-name and absolute-path references with neutral language. The minor path-default change in `harness.py` (script-relative paths instead of hardcoded absolutes) is portable and works the same whether the script lives in the original bench layout or here. No functional changes other than that.

If you find a missed personal-info reference in this pack, please open an issue.
