# Vendored harness snapshot

This directory is the `bench-fleet` harness as used to produce every cell in `../{tower2,strix-halo,spark,m5-mbp,sustained,aggregate,audit}/`. It's a frozen snapshot — the bench-fleet repo continues to evolve in the maintainer's workspace; **this copy is the one that produced the published data**.

## Provenance

The exact source SHA is in [`VENDORED-FROM-SHA.txt`](VENDORED-FROM-SHA.txt). If you compare against bench-fleet upstream, expect divergence — fixes land there first and percolate to the next published bundle's vendored copy.

## What's here

| path | purpose |
|---|---|
| `run.sh` | orchestrator (`--phase prepare|smoke|bench|aggregate|report`) |
| `lib/bench-host.sh` | per-(host, model, backend) cell loop |
| `lib/bench-cell.py` | per-cell asyncio parallel-request driver |
| `lib/bench-cell-vllm.py` | vLLM appendix driver (streams `/v1/completions`) |
| `lib/sustained-host.sh` | sustained-thermal sub-study driver (1 cell × duration) |
| `lib/probe-power.sh`, `lib/probe-thermals.sh` | 1 Hz samplers |
| `lib/aggregate.sh`, `lib/report.sh` | post-run analysis |
| `lib/post-grid.sh` | M5 backfill + sustained + MMBT Phase B Q8 + final aggregate |
| `lib/run-bench.sh` | invokes `bench-host.sh` on one (host, model, backend) tuple |
| `lib/common.sh` | shared helpers |
| `lib/semantic-equiv-vllm.py` | cross-engine SHA-comparison driver |
| `engines/llama-server.sh` | start/wait/stop wrapper for `llama-server` |
| `targets.json` | host inventory + per-host cost / chassis / sampler config (sanitized — `user_home` etc. replaced with `$HOME`) |
| `workloads/grid.json` | 4 ctx × 3 gen × 3 conc × N=10 grid spec |
| `workloads/smoke-grid.json` | 1-cell smoke variant |
| `workloads/generate_corpus.py` | prompt-corpus regeneration script |
| `README.md` | upstream bench-fleet README (kept verbatim) |
| `AUDIT.md` | upstream bench-fleet audit (the polished public version lives at `../AUDIT.md`) |

## What's *not* here

| omitted | why |
|---|---|
| `results/` | This is the data — see `../{host}/{model}/{backend}/{cell}/` for the cell artifacts and `../aggregate/` for the rollups. |
| `downloads/` | Model files downloaded during `--phase prepare`. Reproducers need to re-fetch from the canonical sources (see `../README.md § Reproducing`). |
| `.git/` | History excluded to keep the bundle small. `VENDORED-FROM-SHA.txt` pins what was used. |
| `__pycache__/`, `*.pyc` | Build artifacts. |

## Reproducing on a single host

```bash
cd harness
# 1) Prepare: fetch+verify model files and the prompt corpus (resolves $HOME)
./run.sh --phase prepare --hosts <yourhost>

# 2) Smoke: 1-cell validation on every (model, backend)
./run.sh --phase smoke --hosts <yourhost>

# 3) Full bench: the canonical 4×3×3×N=10 grid
./run.sh --phase bench --hosts <yourhost>

# 4) Aggregate + report
./run.sh --phase aggregate
./run.sh --phase report
```

## Reproducing the full cross-host study

You need `ssh_alias` resolvable to each remote host (with passwordless key auth) and the harness installed at `$HOME/bench-fleet` on each. `lib/prepare-host.sh` rsyncs the harness + models to each remote on `--phase prepare`. See `README.md § Cross-host orchestration` for the long-form walkthrough.

## Known harness issues (not yet fixed in the snapshot above)

- `bench-host.sh` cleanup_cell trap historically didn't fire on parent SIGTERM — children reparented to init on orchestrator pause. A trap fix landed on the bench-fleet upstream after this snapshot was taken; will appear in the next vendored bundle.
- `auto-pr.sh` stashes its own fix when the pending changes are the only dirty files. Manual `git add + commit + push` workaround.
- `live-snapshot.sh` headline section sometimes prints null cells — script bug, the underlying `aggregate/headline.json` is correct.

Document these so reproducers know what behavior to expect and can apply local patches.
