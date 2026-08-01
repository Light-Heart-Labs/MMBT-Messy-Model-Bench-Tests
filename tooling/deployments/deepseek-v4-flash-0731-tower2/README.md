# DeepSeek V4 Flash 0731 on Tower2

Status: production and MMBT configuration accepted on 2026-08-01 afte
performance, full-context, concurrency, repeated-prefix, restart, Sanctuary,
and Pixel validation.

This is the reproduction and decision record for the exact DeepSeek V4 Flash
0731 build used by Tower2 and the MMBT campaign. It documents both the final
configuration and the failed/rejected configurations so a future operator does
not have to rediscover the same constraints.

## Scope and comparison policy

The objective was the strongest stable build this 2x 96 GB workstation can
serve, not an artificially matched 256K configuration. DeepSeek is therefore
served at its full 1,048,576-token checkpoint limit and at its recommended
agentic sampling point (`temperature=1.0`, `top_p=0.95`). MMBT receipts and
findings must explicitly disclose those differences from historical Qwen runs.

Quality claims must come from MMBT task artifacts and graders. Throughput
claims must come from the validation artifacts listed below. A model is not
credited merely for returning HTTP 200, using a large context limit, o
producing a persuasive-looking answer.

## Reproducibility pins

| Component | Exact pin |
|---|---|
| Host | Tower2; Threadripper Pro 7965WX; 2x RTX PRO 6000 Blackwell Workstation Edition, 97,887 MiB each |
| NVIDIA driver | 595.58.03 during acceptance |
| Checkpoint | `deepseek-ai/DeepSeek-V4-Flash-0731` |
| Model revision | `9e165c30e2704aec5d9d593cce3eebd58bbef1cb` |
| Model path | `/mnt/bulk/models/deepseek-ai-DeepSeek-V4-Flash-0731` |
| On-disk size | 155.43 GiB |
| Runtime image | `voipmonitor/vllm@sha256:48518e91cf87dd0c0483c76ff86e81dfc0f46de7e364b46f7a82c481ce08188f` |
| Runtime build | `v0.11.2.dev280+gilded.gnosis.v20.vllm1e9c9c3.sieec30ff.fi801d57a.cu132.20260731.r16` |
| Launcher SHA-256 | `4fca6a4a478f0876a1e6d7241dd87a3c9574bd970f29943bb3696993d4bfe25d` |
| Workspace overlay SHA-256 | `50b5a02e83a419e6da309efb2f78580b72e5b04c57babf6d34854ef3d3fb6dbe` |
| Unmodified image `workspace.py` SHA-256 | `c700b71cab503b93d825b8b52de25654982a68f74f74d07ce508c059712bdd95` |
| Power-limit unit SHA-256 | `0ddc863bd20ed48c71be6d0b53466c2b264636aaec5dcf7a05d3055db6a41ddb` |
| API | OpenAI-compatible endpoint on `127.0.0.1:8000`; served name `DeepSeek-V4-Flash-0731` |

The exact accepted launcher, full overlay, minimal overlay diff, and systemd
power-limit unit are stored beside this document. Verify their hashes before
replay.

## Accepted runtime configuration

| Area | Accepted value |
|---|---|
| Parallelism | tensor parallel 2; decode-context parallel 1; both GPUs participate in each request |
| Weights / KV | checkpoint-native FP4 expert weights; FP8 KV cache; block size 256 |
| Attention | `B12X_MLA_SPARSE` |
| MoE / linear | B12X with force-A8 MoE path / B12X linear |
| Speculation | attached DSpark; fixed depth; K=5; probabilistic draft sampling; standard rejection |
| Loading | InstantTensor, `BUFFERED` backend, persistent AOT/cache directory |
| Scheduling | async; chunked prefill; no full-ISL scheduler reservation |
| CUDA graphs | full and piecewise; maximum capture size 96 |
| Prefix caching | enabled |
| Context | `max_model_len=1048576` |
| Admission | `max_num_seqs=16`; `max_num_batched_tokens=2112` (effective 2,048-token chunks) |
| GPU allocation | `gpu_memory_utilization=0.9842` |
| Workspace safety floor | lane 0 minimum 1,152 MiB during unlocked startup profiling |
| Sampling | runtime and MMBT request defaults `temperature=1.0`, `top_p=0.95` |
| Power | persistent 500 W cap on each GPU |
| Container policy | `--init`, `--restart unless-stopped`, host IPC/network, 32 GiB shared memory |

Accepted startup accounting per GPU was 80.78 GiB weights, 1.85 GiB peak
activation, 0.50 GiB non-Torch, 0.16 GiB CUDA graphs, and 9.47 GiB KV. The
engine reported 1,660,655 KV tokens and 1.58x concurrency at the full 1,048,576
token request size. At 256K, the same pool supports roughly six full windows,
subject to generated-token growth and fragmentation. Requests beyond active
capacity queue in vLLM; system RAM is not configured as KV spill because it
would make latency much less predictable over PCIe.

`gpu_memory_utilization=0.9842` is intentional. Higher values can add a modest
amount of KV, but the accepted setting already proves the full checkpoint
window and useful concurrency while retaining approximately 1.5 GiB of the
runtime's desired safety envelope per GPU. Stability under prefix-cache and
agent traffic was prioritized over a small capacity-only gain that would not
increase decode throughput.

## Why this topology

- The 155.43 GiB checkpoint plus runtime state does not fit on one 96 GB GPU.
  TP=2 is therefore necessary, and both GPUs normally execute every token.
- These workstation cards communicate over PCIe without a validated native
  peer-to-peer path. Custom all-reduce and direct NCCL P2P stalled in testing.
  The accepted NCCL Ring/LL host-shared-memory path disables P2P and custom
  all-reduce and is both fast and repeatably restartable.
- B12X MLA, MoE, and linear kernels plus DSpark K=5 are the primary reason the
  accepted r16 build is dramatically faster than the original serving stack.
- FP8 KV is required to keep the full 1M context plus concurrency on GPU.
- Prefix caching remains enabled because Sanctuary, Pixel, and MMBT reuse large
  system/tool prefixes. The workspace overlay makes that path safe rather than
  disabling the optimization to hide the bug.
- A 500 W cap reduces the combined GPU power ceiling by 200 W. On the original
  runtime's matched 128K sweep it retained 95.8% of 600 W prefill throughput;
  ordinary decode did not reach even the 500 W cap. This leaves materially more
  PSU headroom for simultaneous CPU load.

## The repeated-prefix workspace failure

### Symptom

The first MMBT extraction smoke passed. A second identical run, which reused a
1,024-token prefix and had a 234-token continuation prefill, crashed the engine:

```text
Workspace is locked but allocation from 'b12x.py:354:_run_compressed_mla'
requires 954.37 MB, current size is 596.58 MB. Workspace growth is not allowed
after locking.
```

This was not a GPU OOM. Gilded Gnosis r16 had locked the workspace after graph
warmup without exercising the worst B12X compressed-MLA continuation shapes.

### Shape probe

An isolated planner probe of the 4,096-wide scratch contract found a
non-monotonic peak close to 256 rows:

| Rows | Planner peak |
|---:|---:|
| 96 | 385.526 MiB |
| 128 | 514.034 MiB |
| 192 | 771.050 MiB |
| 232 | 931.685 MiB |
| 234 | 939.717 MiB before runtime overhead; 954.37 MB in the failure |
| 256 | 1,028.065 MiB |
| 384 | 96.472 MiB |

Raising the CUDA graph capture cap from 96 to 256 did not warm this contract
and reproduced the same 954.37/596.58 MB crash. It is explicitly rejected as a
fix.

### Accepted fix

The overlay adds one narrowly scoped rule in
`WorkspaceManager._ensure_workspace_size`: while lane 0 is still unlocked,
raise its required startup allocation to the optional
`VLLM_WORKSPACE_LANE0_MIN_MIB` floor. The launcher sets 1,152 MiB. It does not
permit growth after lock, replace a pointer after graph capture, or change othe
lanes. The 1,152 MiB floor covers the measured 1,028.065 MiB maximum plus
runtime overhead.

The overlay costs about 0.54 GiB per GPU versus the incomplete warmup, visible
in peak activation accounting. It has no material throughput cost.

## Acceptance evidence

All figures below are from the final overlay, 500 W caps, and accepted launcher.
Synthetic decode rows use exactly 1,024 completion tokens per stream.

| Check | Result |
|---|---:|
| Uncached 128K prefill | 7,255.113 prompt tok/s; 128,000 measured tokens; 17.643 s |
| Single coding decode, temperature 1 | 271.778 aggregate tok/s |
| Four concurrent synthetic decodes | 850.143 aggregate tok/s |
| Eight concurrent synthetic decodes | 1,373.176 aggregate tok/s |
| Near-full-context recall | PASS; 1,019,753 uncached prompt tokens; start/middle/end all recalled; 222.223 s |
| Container restart | health recovered in 132.1 s; restart count 0; OOM false |
| Repeated-prefix MMBT A/B after restart | both `done_signal`; both grader PASS at 18/20; server remained healthy |
| Sanctuary before/after restart | expected end-to-end marker returned both times |
| Pixel before/after restart | expected end-to-end marker returned both times |

The original Jasl 500 W serving path produced 848.141 prompt tok/s on the same
128K probe. The accepted final result is about 8.55x that baseline. An earlie
accepted-r16 sample reached 7,528 prompt tok/s; the final overlay repeats at
7,255-7,309, a normal 2.9-3.6% spread rather than a systematic regression.

Authoritative host artifacts:

```text
/home/michael/context-ablation-deepseek-v4-flash-0731-20260801/
  prefill-workspace1152-final-postrestart-500w.json
  decode-workspace1152-final-postrestart-500w-c1-coding.json
  decode-workspace1152-final-postrestart-500w-c4.json
  decode-workspace1152-final-postrestart-500w-c8.json
  workspace1152-final-500w-1m-recall.json
  openclaw-workspace1152-final-e2e.log
  openclaw-workspace1152-final-postrestart-e2e.log

/home/michael/bench-deepseek-v4-flash-0731/logs/
  smoke_workspace1152_sharedprefix_a/
  smoke_workspace1152_sharedprefix_b/
  smoke_workspace1152_postrestart_a/
  smoke_workspace1152_postrestart_b/
```

## Rejected and superseded configurations

| Configuration | Disposition |
|---|---|
| Old Jasl server | Superseded; approximately 8.55x slower on matched uncached 128K prefill |
| 384K / util 0.97 | Superseded once native 1M context passed |
| Concurrent partial prefill | Backend reports it unsupported |
| Custom all-reduce | Stalled on this non-P2P PCIe topology |
| NCCL direct P2P | Stalled; rejected |
| CUDA graph cap 256 as workspace fix | Reproduced the identical locked-workspace crash |
| CUDA graph cap 96 without overlay | Reproduced the locked-workspace crash |
| Disabling prefix cache | Rejected; would hide the crash and discard a valuable production optimization |
| GPU caps 525/600 W | Superseded by requested 500 W envelope; ordinary decode showed no measurable cap loss |
| ForceP2P kernel/driver modification | Not authorized or needed for acceptance; would require a host-level change and reboot |
| Pre-context 131K benchmark attempts | Non-canonical and excluded; no final campaign entries were retained |

Stopped failed/candidate containers were retained during the audit so thei
logs could not be confused with accepted evidence. They are not launch targets.
The sole canonical serving name is `deepseek-v4-flash-0731`.

## Installation and operation

1. Install the exact checkpoint revision at the pinned model path.
2. Install `workspace.py` from this directory at
   `/home/michael/deepseek-r16-patches/workspace.py` and verify its SHA-256.
3. Install `nvidia-powerlimit.service` under `/etc/systemd/system`, then enable
   and start it. Verify both devices report 500 W after boot.
4. Install `start-deepseek-v4-flash-0731.sh` at `/home/michael/`, verify its
   SHA-256, and run it only when the canonical container name is free.
5. Wait for `curl -fsS http://127.0.0.1:8000/health`.
6. Run a direct tool-call smoke, the repeated-prefix A/B smoke, and the
   Sanctuary/Pixel end-to-end probe after any image, driver, patch, kernel,
   context, batching, or graph-setting change.

Useful checks:

```bash
docker inspect --format='{{.State.Status}}:{{.RestartCount}}:{{.State.OOMKilled}}' deepseek-v4-flash-0731
curl -fsS http://127.0.0.1:8000/health
nvidia-smi --query-gpu=index,power.limit,memory.used,memory.total,utilization.gpu --format=csv
sha256sum /home/michael/start-deepseek-v4-flash-0731.sh \
  /home/michael/deepseek-r16-patches/workspace.py \
  /etc/systemd/system/nvidia-powerlimit.service
```

Do not inspect or publish the environment of Sanctuary or Pixel containers;
their credentials are outside the benchmark evidence boundary.

## MMBT campaign requirements

The exact N=3 supervisors, systemd units, cost/power/telemetry sidecars, and
dual-GPU analyzer are pinned in [`campaign/`](campaign/README.md).

- Commit this record and all harness/config changes before score-producing
  runs, so every receipt points to a clean immutable harness SHA.
- Canonical microbench: 12 task families x N=3, with the same graders,
  transcript, receipt, summary, workspace archive, cost, power, telemetry, and
  pathology-monitoring standards as the historical Qwen campaigns.
- Extended matrix: 1-PR audit, investment memo, dependent board presentation,
  and 75-PR audit, each N=3.
- Record the exact runtime image digest, model revision, overlay mount, GPU
  power limit, full 1M served context, and sampling values in every receipt.
- A completion is valid only with the required artifacts or an explicit
  terminal-pathology label. Rerun gaps; never count a low output-token ceiling
  or the superseded 131K deployment as a model failure.
- Compare task quality separately from speed, context capacity, power, and
  operational stability. DeepSeek's 1.0/0.95 sampling differs from historical
  0.0/0.3 arms and must remain footnoted.

## External references consulted

- [Official DeepSeek checkpoint](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)
- [vLLM DeepSeek V4 recipe](https://recipes.vllm.ai/deepseek-ai/DeepSeek-V4-Flash)
- [Gilded Gnosis dual-RTX-PRO-6000 runbook](https://github.com/local-inference-lab/rtx6kpro/blob/master/models/ds4dspark-v20.md)
- [Optional PCIe ForceP2P experiment](https://github.com/local-inference-lab/rtx6kpro/blob/master/optimization/pcie-oneshot-allreduce.md)
- [vLLM workspace manager documentation](https://docs.vllm.ai/en/stable/api/vllm/v1/worker/workspace/)
- [Related vLLM locked-workspace issue](https://github.com/vllm-project/vllm/issues/43357)
- [Exact-hardware community performance thread](https://www.reddit.com/r/LocalLLaMA/comments/1vcaztx/what_speeds_are_everyone_getting_with_deepseek_v4/)

Community reports were used to identify optimizations to test, not as evidence
that Tower2 achieved them. Only the host artifacts above support accepted
performance and stability claims.
