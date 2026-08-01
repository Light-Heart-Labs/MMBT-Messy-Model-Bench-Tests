#!/usr/bin/env bash
set -euo pipefail

# Reproducible foreground launcher for one Gemma server process.  A service
# manager or the topology harness owns backgrounding, logs, and restart policy.

RUNTIME_ROOT="${GEMMA_RUNTIME_ROOT:-/home/michael/llama.cpp-gemma4-11924d4/build-cuda-tower2}"
SERVER_BIN="${GEMMA_SERVER_BIN:-$RUNTIME_ROOT/bin/llama-server}"
MODEL="${GEMMA_MODEL:-/mnt/bulk/models/google-gemma-4-31B-it-QAT-Q4_0-GGUF/gemma-4-31B_q4_0-it.gguf}"
MMPROJ="${GEMMA_MMPROJ:-/mnt/bulk/models/google-gemma-4-31B-it-QAT-Q4_0-GGUF/gemma-4-31B-it-mmproj.gguf}"

export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES="${GEMMA_CUDA_VISIBLE_DEVICES:-0}"
export GGML_CUDA_ENABLE_UNIFIED_MEMORY=0

HOST="${GEMMA_HOST:-127.0.0.1}"
PORT="${GEMMA_PORT:-8000}"
# llama.cpp exposes the last comma-separated alias as the primary /v1/models
# identity. Keep the temporary rollback-transition alias first and Gemma last.
ALIASES="${GEMMA_ALIASES:-DeepSeek-V4-Flash-0731,Gemma-4-31B-it-QAT-Q4_0}"
CTX_SIZE="${GEMMA_CTX_SIZE:-262144}"
PARALLEL="${GEMMA_PARALLEL:-1}"
SPLIT_MODE="${GEMMA_SPLIT_MODE:-none}"
MAIN_GPU="${GEMMA_MAIN_GPU:-0}"
TENSOR_SPLIT="${GEMMA_TENSOR_SPLIT:-}"
CACHE_TYPE_K="${GEMMA_CACHE_TYPE_K:-f16}"
CACHE_TYPE_V="${GEMMA_CACHE_TYPE_V:-f16}"
BATCH_SIZE="${GEMMA_BATCH_SIZE:-2048}"
UBATCH_SIZE="${GEMMA_UBATCH_SIZE:-512}"
THREADS="${GEMMA_THREADS:-16}"
THREADS_BATCH="${GEMMA_THREADS_BATCH:-24}"
THREADS_HTTP="${GEMMA_THREADS_HTTP:-16}"
CACHE_REUSE="${GEMMA_CACHE_REUSE:-256}"

NATIVE_CONTEXT=262144
required_ctx=$((PARALLEL * NATIVE_CONTEXT))
if (( CTX_SIZE < required_ctx )); then
  printf 'Refusing GEMMA_CTX_SIZE=%s with GEMMA_PARALLEL=%s: each slot must retain the full %s-token native context.\n' \
    "$CTX_SIZE" "$PARALLEL" "$NATIVE_CONTEXT" >&2
  exit 64
fi

test -x "$SERVER_BIN"
test -r "$MODEL"
test -r "$MMPROJ"

cmd=(
  "$SERVER_BIN"
  --model "$MODEL"
  --mmproj "$MMPROJ"
  --alias "$ALIASES"
  --host "$HOST"
  --port "$PORT"
  --ctx-size "$CTX_SIZE"
  --parallel "$PARALLEL"
  --n-predict -1
  --n-gpu-layers all
  --split-mode "$SPLIT_MODE"
  --main-gpu "$MAIN_GPU"
  --flash-attn on
  --cache-type-k "$CACHE_TYPE_K"
  --cache-type-v "$CACHE_TYPE_V"
  --batch-size "$BATCH_SIZE"
  --ubatch-size "$UBATCH_SIZE"
  --threads "$THREADS"
  --threads-batch "$THREADS_BATCH"
  --threads-http "$THREADS_HTTP"
  --timeout 3600
  --cont-batching
  --cache-prompt
  --cache-reuse "$CACHE_REUSE"
  --metrics
  --slots
  --jinja
  --no-webui
)

if [[ -n "$TENSOR_SPLIT" ]]; then
  cmd+=(--tensor-split "$TENSOR_SPLIT")
fi

printf 'Launching:' >&2
printf ' %q' "${cmd[@]}" >&2
printf '\n' >&2
exec "${cmd[@]}"
