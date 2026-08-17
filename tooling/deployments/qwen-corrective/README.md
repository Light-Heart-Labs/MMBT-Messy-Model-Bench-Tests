# Corrective crossover serving deployment (phase_a / phase_b)

Serving-side machinery for the host crossover of the Qwen3.6-27B vs
Qwen3.8-27B corrective study (`benchmarks/qwen36-vs-qwen38-corrective-2026-08/
PREREGISTRATION.md`, section 3 — BINDING).

| phase | seeds | tower1 (18101) | tower3 (18103) | ensure scripts |
|---|---|---|---|---|
| phase_a | 101 / 211 / 307 | Qwen3.8-27B | Qwen3.6-27B | `../qwen3.8-27b-q4-fleet/ensure-q38-tower1-only.sh` + `../qwen3.8-27b-q4-fleet/ensure-q36-tower3-only.sh` |
| phase_b | 401 / 503 / 601 | Qwen3.6-27B | Qwen3.8-27B | `./ensure-q36-tower1-only.sh` + `./ensure-q38-tower3-only.sh` |

The crossover swaps HOSTS, never artifacts: both towers hold both GGUFs
locally and every model file sha256 was measured on both towers on
2026-08-16 — `Qwen3.6-27B-UD-Q4_K_XL.gguf` = `ff6941de…`,
`Qwen3.8-27B-UD-Q4_K_XL.gguf` = `bee238bb…` on tower1 AND tower3.
llama-server flags are byte-identical everywhere; only `--model`/`--alias`
differ. The phase_b ensure scripts are line-mirrors of the phase_a scripts
with exactly these deltas: model block (alias/rel-path/size/sha256),
container name, server profile, lane spec (tower/port/GPU UUID/tunnel unit),
the `mmbt.campaign` label, and one added guard — they refuse to start while
the OPPOSITE-phase bench container is running (same GPU, same remote port
11434), alongside the existing ods-llama-server refusal.

## Phase swap procedure (phase_a -> phase_b)

1. Finish all phase_a seeds (101/211/307) for the arm(s) being run.
2. On tower1: `docker stop mmbt-qwen38-bench` (ods-llama-server must already
   be stopped for clean runs; at prep time its container id was
   `834bdb6c901d` — restore after the campaign with
   `ssh tower1 docker start ods-llama-server`).
3. On tower3: `docker stop mmbt-qwen36-bench`.
4. From Tower2 (this repo): `bash ensure-q36-tower1-only.sh --check` and
   `bash ensure-q38-tower3-only.sh --check` (read-only), then run both
   without `--check` to start the swapped servers.
5. Point the arm config key `serving_manifest` at the ABSOLUTE path of
   `phase_b.json` (cell_supervisor.py passes it through as
   `BENCH_SERVING_MANIFEST` -> `harness.py --serving-manifest`; the harness
   embeds the manifest and resolves the lane by `coordinator_port`).
   Use `phase_a.json` while phase_a seeds run.
6. Re-run the runner preflight:
   `bash tooling/corrective/run_crossover.sh --config <arm>.json --seeds 401,503,601 --dry-run`
   — endpoint checks must show 18101 -> Qwen3.6 alias and 18103 -> Qwen3.8
   alias before any clean phase_b cell starts.

Reverting to phase_a is the mirror: stop the phase_b bench containers and
re-run the two phase_a ensure scripts (the containers are preserved with
`--restart=no` and restart via `docker start` after label verification).

## Files

| file | role |
|---|---|
| `ensure-q36-tower1-only.sh` | phase_b lane: Qwen3.6 on tower1 behind 18101 |
| `ensure-q38-tower3-only.sh` | phase_b lane: Qwen3.8 on tower3 behind 18103 |
| `phase_a.json` | serving manifest for seeds 101/211/307 (BENCH_SERVING_MANIFEST) |
| `phase_b.json` | serving manifest for seeds 401/503/601 (BENCH_SERVING_MANIFEST) |

Both manifests carry the full pinning evidence (model sha256s per tower,
image digest, llama-server binary sha256, GPU UUIDs, power caps, tunnel unit
sha256s) and were verified live on 2026-08-16.
