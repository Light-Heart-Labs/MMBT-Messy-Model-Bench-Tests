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
| `run_crossover.sh` | six-seed host crossover: phase_a 101/211/307 = Tower1:Q3.8 + Tower3:Q3.6, phase_b 401/503/601 swapped; family-major interleave with alternating model start (first = q38 iff (seed_index+family_index) even, second staggered 30 s, both towers concurrent); preflight = 500 W cap on both towers + per-phase endpoint alias + Tower1 ODS drain (refuses if `ods-llama-server` runs); preflight evidence written to `logs/corrective/preflight-*.json` |
| `configs/official-nothink.json` | PRIMARY arm, both models, T0.7/0.8/20/min_p0/pp1.5/rp1, thinking off, 6 seeds |
| `configs/official-think.json` | secondary arm, T1.0/0.95/20/min_p0/pp0/rp1, thinking on; q38 xhigh-only + preserve_thinking (top_level), q36 normal thinking, 6 seeds |
| `configs/diag-t03.json` | exploratory diagnostic, T0.3/0.8/20/pp0/rp1, thinking off, seeds 101/211/307 only |
| `configs/family_artifacts.json` | per-family expected deliverables, derived from `tooling/tasks/*.md` required-structure sections; artifacts the briefs explicitly mark optional are NOT delivery-gated (preregistration-freeze fix, see _doc_freeze_fix in the file) |
| `test_*.py` | unittest suites incl. the digit-changing copyfileobj pattern (must NOT flag) and identical-args-different-tool (must NOT flag) |

Run names: `<family>_<model>-<arm>[-xhigh|-nothink]-s<seed>_v1` — labels
encode arm, thinking mode, effort, and seed, satisfying run_microbench.sh's
label-collision guards and making the idempotent resume per-cell.

Known recorded limitations:

* Tool arguments > 50 KB are stored by the harness as
  `{"_truncated_at_bytes": N}`; the loop metric compares those by byte count.
* `quant-pilot` (protocol section 7, Tower2 window) is deliberately NOT
  configured here; it needs its own bounded-window runner.
* `serving_manifest` for the corrective deployment phases (esp. phase_b
  swapped hosts) is produced at deployment time; configs accept a
  `serving_manifest` key that the supervisor passes through when present.
