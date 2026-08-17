# Corrective campaign mechanics (Phase A)

Machinery implementing PREREGISTRATION.md sections 3-5 for the Qwen3.6-27B vs
Qwen3.8-27B corrective study. Everything here is python3-stdlib-only + bash.
The prior campaign's graders, receipts, labels, and logs are never touched.

## Seed / sampler plumbing (verified firsthand at this checkout)

`benchmark_seed` flows end to end with no code change needed:

1. Campaign config `benchmark_seed` -> `BENCH_SEED` env
   (`bench_autopilot.py::benchmark_environment`, line 908 mapping; the
   corrective runner sets `BENCH_SEED` directly from the arm config + cell seed).
2. `tooling/scripts/run_microbench.sh` line 108:
   `[ -n "${BENCH_SEED:-}" ] && SEED_FLAG=(--seed "$BENCH_SEED")`.
3. `tooling/harness.py` `--seed` (default 42) -> `build_chat_payload()` puts
   `"seed": seed` into EVERY `/v1/chat/completions` request body
   (harness.py ~L768-784), and `record_environment()` writes it to
   `receipt.json.inference_request_defaults.seed` (~L358).

Per-invocation override therefore already exists (env var -> CLI flag); the
corrective runner sets a distinct `BENCH_SEED` per cell. Same verified path
for the sampler triple (BENCH_TEMP/TOP_P/TOP_K/MIN_P/PRESENCE_PENALTY/
REPEAT_PENALTY), `--thinking` (-> `chat_template_kwargs.enable_thinking`),
`--preserve-thinking`, and `--reasoning-effort` +
`--reasoning-effort-location top_level` (Qwen3.8 requires the OpenAI
top-level field; harness.py argparse help + build_chat_payload).

## Minimal change made to `evidence_manifest.py` for the quant pilot

`expected_cells` now reads `models[<key>].quant` with fallback to the
arm-level `quant` key. Default-preserving: no existing config carries a
model-level `quant`, so every previously built manifest row is
byte-identical; the quant-pilot config needs per-row quant for the
Q4-vs-Q8 pairing. Covered by
`test_evidence_manifest.py::test_model_level_quant_overrides_arm_quant`.

## Minimal changes made to `tooling/scripts/run_microbench.sh`

Two default-preserving additions (unset env = byte-identical behavior):

1. `BENCH_TASK_ONLY` — optional comma-separated task-family allowlist so the
   crossover runner can drive ONE cell per invocation (required for the
   protocol's family-major interleave with alternating model start).
   Unknown family names fail fast.
2. The idempotent-resume skip check now also recognizes the two AUTOMATED
   terminal labels of this protocol (`loop-run30`, `timeout`, both requiring
   `"automated": true`) alongside the historical operator label
   `identical-call-loop`. Without this, a resumed invocation would archive a
   terminated cell's evidence to `logs/_invalid/` and re-run a completed cell,
   breaking the fixed-N ledger.

## Components

| file | role |
|---|---|
| `loop_terminator.py` | terminator (b): longest exact consecutive run over `(tool_name, canonical_json(args))`; `watch` kills the cell's harness at >= 30 and writes `label.json {primary: loop-run30, metric: consecutive_exact_run, value, automated: true}`; `recompute` = same functions offline |
| `delivery_validator.py` | deterministic delivery flag (done-signal finish + summary.json + workspace_final.tar.gz + per-family artifact existence/schema) + mechanical infra classification. Delivery and loop are distinct columns |
| `evidence_manifest.py` | `build` writes per-cell manifest.jsonl (family, arm, model, seed, host, sampler, quant, harness/grader shas, image digest, transcript sha256, delivery, loop metrics, consistency checks); `check` asserts the fixed-N grid (zero duplicates/missing/extras) |
| `cell_supervisor.py` | one cell end-to-end: env plumbing, live loop-terminator thread, 3 h wall ceiling (-> `timeout` label when the cell has >= 1 model turn, else infra), sandbox cleanup, quarantine + same-seed rerun ledger (`logs/corrective/rerun_ledger.jsonl`) |
| `run_quant_pilot.sh` | bounded Tower2 window runner for the quant crossover pilot (PREREGISTRATION section 7): 2 models x {UD-Q4_K_XL, Q8_0} x seeds 101/211 x 12 families = 96 cells on the two RTX PRO 6000s, GPU<->model assignment crossed between seeds. Refuses to open while DSV4 (`deepseek-v4-flash-0731`) is running (drain + restore are orchestrator-owned; it prints the restore reminder at close). Starts two llama-server containers per (seed, quant) wave from the pinned image digest with llama-server argv byte-identical to the historical `ensure-*-only.sh` lanes except `--model`/`--alias` (docker-level deltas documented in the config), verifies the pinned llama-server binary sha in every container, generates a per-seed serving manifest consumed via `BENCH_SERVING_MANIFEST`, and drives every cell through `cell_supervisor.py` (same terminators, rerun ledger, manifest machinery). Window evidence: `logs/corrective/preflight-quant-pilot-*.json` + `logs/corrective/quant-pilot/window_ledger.jsonl` |
| `run_crossover.sh` | six-seed host crossover: phase_a 101/211/307 = Tower1:Q3.8 + Tower3:Q3.6, phase_b 401/503/601 swapped; family-major interleave with alternating model start (first = q38 iff (seed_index+family_index) even, second staggered 30 s, both towers concurrent); preflight = 500 W cap on both towers + per-phase endpoint alias + Tower1 ODS drain (refuses if `ods-llama-server` runs); preflight evidence written to `logs/corrective/preflight-*.json` |
| `configs/official-nothink.json` | PRIMARY arm, both models, T0.7/0.8/20/min_p0/pp1.5/rp1, thinking off, 6 seeds |
| `configs/official-think.json` | secondary arm, T1.0/0.95/20/min_p0/pp0/rp1, thinking on; q38 xhigh-only + preserve_thinking (top_level), q36 normal thinking, 6 seeds |
| `configs/diag-t03.json` | exploratory diagnostic, T0.3/0.8/20/pp0/rp1, thinking off, seeds 101/211/307 only |
| `configs/quant-pilot.json` | exploratory quant-pilot arm: official-nothink sampler, thinking off, per-model `quant` + artifact pins (path/size/sha256/HF revision) for all four model x quant lanes; `host_plan` encodes the seed-level GPU crossover; `serving.waves` encodes quant co-residency. Qwen3.6 Q8_0 is NOT on disk yet — see `download-qwen36-q8_0.sh` |
| `download-qwen36-q8_0.sh` | staging script (written, deliberately not yet run) for the missing Qwen3.6-27B Q8_0 GGUF: revision-pinned HF URL, resume, size + full-sha256 verification before the artifact is moved into `/mnt/bulk/models/qwen3.6-27b-q8_0/` |
| `configs/family_artifacts.json` | per-family expected deliverables, derived from `tooling/tasks/*.md` required-structure sections; artifacts the briefs explicitly mark optional are NOT delivery-gated (preregistration-freeze fix, see _doc_freeze_fix in the file) |
| `test_*.py` | unittest suites incl. the digit-changing copyfileobj pattern (must NOT flag) and identical-args-different-tool (must NOT flag) |

Run names: `<family>_<model>-<arm>[-xhigh|-nothink]-s<seed>_v1` — labels
encode arm, thinking mode, effort, and seed, satisfying run_microbench.sh's
label-collision guards and making the idempotent resume per-cell.

Known recorded limitations:

* Tool arguments > 50 KB are stored by the harness as
  `{"_truncated_at_bytes": N}`; the loop metric compares those by byte count.
* `quant-pilot` (protocol section 7, Tower2 window) now has its own
  bounded-window runner: `run_quant_pilot.sh` + `configs/quant-pilot.json`
  (component table above). Built, not yet executed: the window opens only
  after the orchestrator drains DSV4, and the Qwen3.6 Q8_0 artifact must
  be staged first (`download-qwen36-q8_0.sh`).
* `serving_manifest` for the corrective deployment phases (esp. phase_b
  swapped hosts) is produced at deployment time; configs accept a
  `serving_manifest` key that the supervisor passes through when present.
