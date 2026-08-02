# Gemma 4 31B QAT Q4_0 on Tower2

This directory is the reproducibility package for the Gemma 4 31B Q4 campaign.
It is created before serving optimization so runtime choices cannot be selected
after seeing benchmark quality.

Read in this order:

1. `PREREGISTRATION.md` — immutable questions, cohorts, validity policy, and
   topology selection rule.
2. `model-manifest.json` — exact local artifacts, hashes, upstream revision,
   hardware, and runtime candidates.
3. `topology-matrix.json` — serving candidates, workloads, and winner rule.
4. `final-validation.json` — populated only after a serving candidate passes.
5. `campaign/` — launchers, units, telemetry, and benchmark supervision added as
   the preregistered phases execute.

The source is Google's [official QAT Q4_0 GGUF](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-gguf).
Google documents [llama.cpp as an OpenAI-compatible Gemma serving route](https://ai.google.dev/gemma/docs/integrations/llamacpp),
and the model repository pins the 256K context and temperature 1.0 / top-p 0.95 /
top-k 64 operating point.

This package deliberately tests one model per GPU as well as cross-GPU splitting.
The 17 GB text model fits on either 98 GB GPU; using both GPUs for every request
would add communication without necessarily improving latency or aggregate
throughput.

The campaign runtime is temporary. `production-restore.json` fingerprints the
proven DeepSeek launcher, image, OpenClaw routing, and a permission-restricted
pre-campaign config backup. Campaign completion requires stopping Gemma,
restoring that DeepSeek state byte-for-byte, and passing fresh Sanctuary and
Pixel end-to-end checks.

Serving files
-------------

- `run-gemma4-server.sh` is the foreground server launcher. It refuses any
  context pool that would leave a parallel slot with less than 262,144 tokens.
- `mmbt-gemma4@.service` and `topologies/*.env` define the preregistered serving
  candidates.
- `gemma4-topology-control.sh` enforces mutually exclusive topology candidates
  and refuses to start while the DeepSeek container still owns the GPUs.
- Split-GPU builds use the privately pinned NCCL runtime recorded in
  `model-manifest.json`; no system CUDA or NCCL package is modified.

Validated benchmark serving
---------------------------

The winning quality-preserving topology is two independent Q8-KV, four-slot
replicas: GPU 0 on port 8000 and GPU 1 on port 8001. Each request stays on one
GPU and retains a hard 262,144-token context; using both replicas concurrently
increases campaign throughput without introducing a cross-GPU dependency.

- `benchmark-serving-manifest.json` is the compact immutable receipt anchor for
  the artifact, runtime, topology, sampling point, context, output ceiling, and
  500 W power caps.
- `ensure-gemma4-winner.sh` starts and health-checks both systemd services; the
  benchmark supervisor uses it for recovery rather than assuming a container.
- `tooling/gemma4-31b-q4-mmbt.json` sends temperature 1.0, top-p 0.95, top-k 64,
  and the 262,144-token output ceiling to the harness. Work is assigned by
  stable run ordinal modulo two, so the lanes are disjoint and reproducible.
- Every run receipt captures the deployment manifest, live `/v1/models`
  identity, and the exact host `llama-server` path, arguments, and SHA-256.
- `gemma4_gpu_telemetry.py` samples both GPUs and the CPU package every five
  seconds. It attributes port 8000's active harness to GPU 0 and port 8001's to
  GPU 1, so simultaneous cells are not mislabeled as one dual-GPU request.
- `analyze_replica_telemetry.py` clips samples to authoritative summary windows
  and writes per-run power, utilization, memory, temperature, clock, energy,
  CPU-package context, coverage, and concurrent-lane evidence. AC wall draw is
  explicitly unavailable to software and is not fabricated from component data.

The two-lane optimization changes scheduling only. It does not change the
canonical run names, cohort membership, prompts, grading, or attempt-preservation
rules, and v1-v3 remain the immutable first cohort before expansion through v10.
