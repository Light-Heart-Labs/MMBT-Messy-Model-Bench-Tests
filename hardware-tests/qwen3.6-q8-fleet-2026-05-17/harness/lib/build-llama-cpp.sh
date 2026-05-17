#!/usr/bin/env bash
# build-llama-cpp.sh — clone (or update to pinned SHA) and build llama.cpp for a backend.
# Runs on the target host. Backend determines cmake flags.
#
# Usage: build-llama-cpp.sh <backend> <pinned_sha> [llama_cpp_dir]
#   backend ∈ {cuda-tower2, cuda-spark, rocm, vulkan, metal}
#   pinned_sha — exact commit
#   llama_cpp_dir — defaults to $HOME/bench-fleet-llama-cpp
#
# Builds: llama-server, llama-bench, llama-cli into build-<backend>/bin/

set -euo pipefail

BACKEND="${1:?usage: build-llama-cpp.sh <backend> <sha> [dir]}"
SHA="${2:?sha required}"
SRC="${3:-$HOME/bench-fleet-llama-cpp}"
REPO="https://github.com/ggml-org/llama.cpp"

log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

# 1) Get the source at the pinned SHA
if [[ ! -d "$SRC/.git" ]]; then
    log "cloning $REPO -> $SRC"
    git clone --quiet "$REPO" "$SRC"
fi
cd "$SRC"
git fetch --quiet origin
git -c advice.detachedHead=false checkout --quiet "$SHA"
log "source at $(git rev-parse --short HEAD) ($(git log -1 --format=%s))"

# 2) Configure
CMAKE_FLAGS=(
    -DCMAKE_BUILD_TYPE=Release
    -DLLAMA_BUILD_SERVER=ON
    -DLLAMA_BUILD_TESTS=OFF
    -DLLAMA_CURL=ON
)
BUILD_DIR="build-$BACKEND"

case "$BACKEND" in
    cuda-tower2)
        export PATH=/usr/local/cuda/bin:$PATH
        if [[ -x "$HOME/.local/bin/cmake" ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
        # CUDA 13 dropped sm_52, which cmake hardcodes in its CUDA compiler-id
        # probe. Force-skip the probe — we already know nvcc works.
        CMAKE_FLAGS+=(
            -DGGML_CUDA=ON
            -DCMAKE_CUDA_ARCHITECTURES="120-real"
            -DCMAKE_CUDA_COMPILER_FORCED=ON
            -DCMAKE_CUDA_COMPILER_WORKS=ON
            -DCMAKE_CUDA_COMPILER_ID=NVIDIA
            -DCMAKE_CUDA_COMPILER_VERSION=13.1
            -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc
        )
        ;;
    cuda-spark)
        export PATH=/usr/local/cuda/bin:$PATH
        CMAKE_FLAGS+=(
            -DGGML_CUDA=ON
            -DCMAKE_CUDA_ARCHITECTURES="121-real"
            -DCMAKE_CUDA_COMPILER_FORCED=ON
            -DCMAKE_CUDA_COMPILER_WORKS=ON
            -DCMAKE_CUDA_COMPILER_ID=NVIDIA
            -DCMAKE_CUDA_COMPILER_VERSION=13.0
            -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc
        )
        ;;
    rocm)
        export PATH=/opt/rocm/bin:/opt/rocm/llvm/bin:$PATH
        export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
        CMAKE_FLAGS+=(
            -DGGML_HIP=ON
            -DAMDGPU_TARGETS=gfx1151
            -DCMAKE_C_COMPILER=/opt/rocm/llvm/bin/amdclang
            -DCMAKE_CXX_COMPILER=/opt/rocm/llvm/bin/amdclang++
        )
        ;;
    vulkan)
        CMAKE_FLAGS+=(-DGGML_VULKAN=ON)
        ;;
    metal)
        # M5: cmake from /opt/homebrew
        export PATH=/opt/homebrew/bin:$PATH
        CMAKE_FLAGS+=(-DGGML_METAL=ON -DGGML_METAL_EMBED_LIBRARY=ON)
        ;;
    *)
        echo "unknown backend: $BACKEND" >&2
        exit 2
        ;;
esac

log "configuring backend=$BACKEND build_dir=$BUILD_DIR"
log "cmake ${CMAKE_FLAGS[*]}"
cmake -B "$BUILD_DIR" "${CMAKE_FLAGS[@]}" -S . > "$BUILD_DIR.configure.log" 2>&1

# 3) Build the three binaries we need
NPROC="$( ( nproc 2>/dev/null || sysctl -n hw.logicalcpu 2>/dev/null || echo 4 ) )"
log "building targets llama-server llama-bench llama-cli with -j$NPROC"
cmake --build "$BUILD_DIR" -j"$NPROC" --target llama-server llama-bench llama-cli \
      > "$BUILD_DIR.build.log" 2>&1

# 4) Verify binaries exist
for bin in llama-server llama-bench llama-cli; do
    if [[ ! -x "$BUILD_DIR/bin/$bin" ]]; then
        log "FAIL: $BUILD_DIR/bin/$bin not built"
        tail -50 "$BUILD_DIR.build.log" >&2
        exit 1
    fi
done

log "DONE backend=$BACKEND"
log "  llama-server: $BUILD_DIR/bin/llama-server"
log "  llama-bench:  $BUILD_DIR/bin/llama-bench"
log "  llama-cli:    $BUILD_DIR/bin/llama-cli"
