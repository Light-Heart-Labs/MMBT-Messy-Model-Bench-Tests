#!/usr/bin/env bash
set -euo pipefail

MODEL_HOST_PATH=/mnt/bulk/models/deepseek-ai-DeepSeek-V4-Flash-0731
CACHE_HOST_PATH=/mnt/bulk/models/runtime-cache/deepseek-v4-flash-0731-gilded-r16
WORKSPACE_PATCH_HOST_PATH=/home/michael/deepseek-r16-patches/workspace.py
CONTAINER_NAME=deepseek-v4-flash-0731
IMAGE=voipmonitor/vllm@sha256:48518e91cf87dd0c0483c76ff86e81dfc0f46de7e364b46f7a82c481ce08188f

GPU_MEMORY_UTILIZATION="${DEEPSEEK_GPU_MEMORY_UTILIZATION:-0.9842}"
MAX_MODEL_LEN="${DEEPSEEK_MAX_MODEL_LEN:-1048576}"
MAX_NUM_SEQS="${DEEPSEEK_MAX_NUM_SEQS:-16}"
MAX_NUM_BATCHED_TOKENS="${DEEPSEEK_MAX_NUM_BATCHED_TOKENS:-2112}"
MAX_CUDAGRAPH_CAPTURE_SIZE="${DEEPSEEK_MAX_CUDAGRAPH_CAPTURE_SIZE:-96}"
WORKSPACE_LANE0_MIN_MIB="${DEEPSEEK_WORKSPACE_LANE0_MIN_MIB:-1152}"
DSPARK_TOKENS="${DEEPSEEK_DSPARK_TOKENS:-5}"
ALLREDUCE_MODE="${DEEPSEEK_ALLREDUCE_MODE:-nccl}"

test -d "$MODEL_HOST_PATH"
test -f "$WORKSPACE_PATCH_HOST_PATH"
mkdir -p "$CACHE_HOST_PATH"/{cache,tmp}

exec docker run -d --init \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --gpus all \
  --runtime nvidia \
  --privileged \
  --ipc host \
  --shm-size 32g \
  --network host \
  --ulimit memlock=-1 \
  --ulimit nofile=1048576:1048576 \
  --ulimit stack=67108864 \
  -v "$MODEL_HOST_PATH":/model:ro \
  -v "$CACHE_HOST_PATH/cache":/cache \
  -v "$CACHE_HOST_PATH/tmp":/container-tmp \
  -v "$WORKSPACE_PATCH_HOST_PATH":/opt/venv/lib/python3.12/site-packages/vllm/v1/worker/workspace.py:ro \
  -e CUDA_VISIBLE_DEVICES=0,1 \
  -e CUDA_DEVICE_ORDER=PCI_BUS_ID \
  -e NCCL_P2P_LEVEL=SYS \
  -e NCCL_P2P_DISABLE=1 \
  -e NCCL_PROTO=LL \
  -e NCCL_ALGO=Ring \
  -e NCCL_MIN_NCHANNELS=8 \
  -e NCCL_NTHREADS=512 \
  -e NCCL_IB_DISABLE=1 \
  -e NCCL_CUMEM_ENABLE=0 \
  -e NCCL_CUMEM_HOST_ENABLE=0 \
  -e NCCL_SOCKET_IFNAME=eno2np1 \
  -e HF_HUB_OFFLINE=1 \
  -e MODEL_PATH=/model \
  -e SPEC_MODEL_PATH=/model \
  -e SERVED_MODEL_NAME=DeepSeek-V4-Flash-0731 \
  -e PORT=8000 \
  -e MODE=dspark \
  -e BACKEND=b12x-a8 \
  -e TP_SIZE=2 \
  -e DCP_SIZE=1 \
  -e DSPARK_DEPTH_MODE=fixed \
  -e DSPARK_TOKENS="$DSPARK_TOKENS" \
  -e ALLREDUCE_MODE="$ALLREDUCE_MODE" \
  -e MAX_NUM_SEQS="$MAX_NUM_SEQS" \
  -e MAX_MODEL_LEN="$MAX_MODEL_LEN" \
  -e MAX_NUM_BATCHED_TOKENS="$MAX_NUM_BATCHED_TOKENS" \
  -e MAX_CUDAGRAPH_CAPTURE_SIZE="$MAX_CUDAGRAPH_CAPTURE_SIZE" \
  -e GPU_MEMORY_UTILIZATION="$GPU_MEMORY_UTILIZATION" \
  -e VLLM_WORKSPACE_LANE0_MIN_MIB="$WORKSPACE_LANE0_MIN_MIB" \
  -e LOAD_FORMAT=instanttensor \
  -e INSTANTTENSOR_BACKEND=BUFFERED \
  -e KV_OFFLOADING_SIZE=0 \
  --entrypoint /usr/local/bin/serve-ds4-flash.sh \
  "$IMAGE" \
  --override-generation-config '{"temperature":1.0,"top_p":0.95}'
