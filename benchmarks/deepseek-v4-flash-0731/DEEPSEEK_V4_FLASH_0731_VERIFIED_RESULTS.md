# DeepSeek V4 Flash 0731 on Tower2: verified MMBT results

This report separates deployment measurements, raw historical-compatible
MMBT gates, corrected grader overlays, and stricter artifact-quality audits.
It does not treat an HTTP response, a large context setting, or a polished
artifact as proof of correctness.

## Accepted Tower2 deployment

- Hardware: 2x NVIDIA RTX PRO 6000 Blackwell Workstation Edition (97,887 MiB
  each), Threadripper Pro 7965WX.
- Persistent power limit: 500 W per GPU.
- Model revision: `9e165c30e2704aec5d9d593cce3eebd58bbef1cb`.
- Runtime image digest:
  `sha256:48518e91cf87dd0c0483c76ff86e81dfc0f46de7e364b46f7a82c481ce08188f`.
- Topology: tensor parallel 2, decode-context parallel 1, maximum model length
  1,048,576, FP8 KV cache, block size 256, prefix caching, async scheduling,
  CUDA graph cap 96, 16 maximum sequences, 2,112 maximum batched tokens, and
  0.9842 GPU-memory utilization.
- Generation defaults: temperature 1.0, top-p 0.95.

Accepted direct measurements at the 500 W limits:

| Check | Result |
|---|---:|
| Uncached 128K prefill | 7,255.113 prompt tok/s |
| One coding decode | 271.778 aggregate tok/s |
| Four concurrent decodes | 850.143 aggregate tok/s |
| Eight concurrent decodes | 1,373.176 aggregate tok/s |
| Near-full-context recall | PASS at 1,019,753 uncached prompt tokens |
| Clean restart | Healthy in 132.1 seconds; no OOM; restart count zero |
| Sanctuary and Pixel | Expected end-to-end markers before and after restart |

The 500 W setting retained 95.8% of the matched 600 W 128K-prefill result.
Ordinary decode remained below 500 W, so the lower ceiling materially improves
PSU headroom without a measurable ordinary-decode penalty.

## Canonical 12-family matrix

The N=3 canonical campaign contains 36 cells. Raw published grading reported
23/36. Independent review found two harness defects: generated cache files were
incorrectly treated as source changes in Phase 1, and three Phase-2 graders
crashed in the host environment. Two writing rules also contradicted their
audience briefs. Original grades remain preserved as `grade.raw.json` where
applicable.

After correcting only those reproducible grader defects and regrading the
unchanged archives, DeepSeek scores **35/36 (97.2%)**:

- 32 PASS
- 3 STRUCTURAL_PASS
- 1 genuine FAIL: the business-writing v2 response used 773 words against a
  700-word maximum

The equivalent non-destructive writing correction changes the historical
Qwen3.5-397B-A17B totals from 82/120 to 92/120 (76.67%) without thinking and
from 72/120 to 81/120 (67.5%) with thinking. DeepSeek's N=3 and Qwen's N=10,
sampling, and campaign dates differ, so these are directional results rather
than a statistically matched superiority claim.

## Extended suites

### Single-PR audit

All three runs shipped clean tagged repositories.

| Run | Wall time | Completion tokens | Model-call tok/s | Substantive result |
|---|---:|---:|---:|---|
| v1 | 303.8 s | 45,690 | 193.8 | Correct MERGE |
| v2 | 405.0 s | 52,171 | 193.7 | Correct MERGE |
| v3 | 1,530.8 s | 63,175 | 205.5 | Defensible but over-strict REVISE; expected MERGE |

The third run demonstrates a recurring tendency to over-investigate and turn
reasonable uncertainty into an unnecessarily conservative disposition.

### Investment research

Two later replicates met the historical `SHIPPED` artifact gate but neither is
a substantive finance pass.

- v2, Knife River: zero workbook formulas, no real three-statement model,
  interest and capex unit errors, and a central cash-flow contradiction.
  Correcting only the growth-capex unit error lowers DCF from $74.72 to about
  $52.67 per share.
- v3, Ollie's: zero workbook formulas, incomplete statements, working capital
  explicitly omitted, and FCFE/enterprise-value convention mixing.

Substantive finance result: **0/2** shipped workbooks valid.

### Board presentation

The valid replicate shipped a clean 23-slide PPTX and matching 23-page PDF
with strong research traceability and complete required content. Full visual
inspection nevertheless found material presentation defects: a collapsed
date-axis wedge on slide 8, unreadable confidence cards on slide 14, title
overflow on six slides, additional label/footer collisions, and incomplete
self-QA. Classification: `SHIPPED_WITH_MATERIAL_DECK_DEFECTS`.

### Frozen 75-PR audit

The authoritative valid-replicate policy preserves every run, excludes only a
run terminated by a configured convenience output ceiling below the served
context while safe context remained, and adds full-context replacements until
three valid outcomes exist.

- v1: valid `done_signal`; 1,426.5 seconds; 136,544 completion tokens; strict
  classification `SCAFFOLD_AND_STOP`.
- v2 and v3: preserved but excluded. Each hit the old 180,000 per-response
  ceiling while the server safely exposed a 1,048,576-token context. They are
  infrastructure-invalid for the best-capability comparison, not model
  failures.
- v4: valid `done_signal`; 727.8 seconds; 116,266 completion tokens; 186.6
  model-call tok/s; clean nine-commit tagged archive. It produced all 75 PR
  packages but failed the strict standard because all 75 reviews were under
  800 bytes, bounty tiers were absent, 14/205 high-confidence overlap pairs
  were omitted, one test/skip record was inadequate, and the tool log covered
  only 16/233 tool events. Classification `SCAFFOLD_AND_STOP`.
- v5: valid full-context model-terminal outcome. The run completed 231
  iterations over 3,233.9 seconds before one response consumed the entire
  dynamically safe allowance: 220,237 prompt tokens plus 815,279 completion
  tokens, with 14,000 tokens reserved inside the served 1,048,576-token
  context. That response contained 3,099,116 characters, no tool call, and
  terminated with `length` after 2,501.26 seconds at 325.9 tok/s. The partial
  workspace had 36 PR directories, 51 test artifacts, 14 commits, no final
  reviews, and no tag. Classification `MODEL_TERMINAL_FAILURE` with pathology
  `runaway-generation`.

The three valid outcomes are therefore two `SCAFFOLD_AND_STOP` completions and
one full-context `MODEL_TERMINAL_FAILURE`: **0/3 strict 75-PR passes**. This is
not a context-capacity or server-stability result. V5 telemetry covered 99.96%
of 3,233.9 seconds, averaged 844.22 W across both GPUs, reached 970.52 W
combined, recorded both GPUs decoding for 89.8% of wall time, and observed no
preemption. The deployment sustained the terminal 815K-token response without
an API error or OOM.

## Post-campaign production validation

The final production check on 2026-08-01 confirmed that the benchmark campaign
did not destabilize the serving stack:

- `deepseek-v4-flash-0731` remained running after seven hours with zero
  restarts and `OOMKilled=false`; the unauthenticated local `/health` endpoint
  returned success.
- Both RTX PRO 6000 GPUs retained their 500 W limits and held 96,899 MiB and
  96,903 MiB of 97,887 MiB at idle after the campaign. Idle temperatures were
  35 C and 37 C.
- The OpenClaw gateway was active. The Sanctuary and Pixel portals were healthy
  and their isolated agent sandboxes remained running.
- Fresh, isolated, non-delivered Sanctuary and Pixel agent turns both returned
  `status=ok` through provider `tower`, model `DeepSeek-V4-Flash-0731`, with a
  1,048,576-token context and `fallbackUsed=false`. Compact verification turns
  completed in 2.028 seconds and 1.841 seconds respectively.
- Final post-cleanup tool-use turns provided stronger end-to-end evidence.
  Sanctuary and Pixel each called the sandbox `exec` tool, successfully ran a
  read-only `printf` command, consumed the returned tool result, and replied
  with the exact requested marker. They completed in 1.812 seconds and 2.284
  seconds respectively, again using the Tower2 model with no fallback.
- All campaign services and 14 idle benchmark sandboxes were stopped after
  artifact validation; the sandbox containers were retained rather than
  removed. The separate persistent 500 W power-limit service remained enabled
  and active, and the production model stayed healthy throughout cleanup.

The system-wide `/usr/bin/openclaw` client is an older 2026.2.12 installation
and cannot speak to the newer gateway protocol. This is a client-version skew,
not an agent outage: the gateway's configured 2026.6.33 client at
`/home/michael/.npm-global/bin/openclaw` completed both end-to-end probes. It
should be used for operational checks until the old system client is upgraded
or removed.

The short marker probes also exposed a minor instruction-formatting quirk: the
model sometimes inserted a newline inside a requested literal marker or chose
a natural-language acknowledgement instead. This did not affect routing or
service availability, but it is consistent with the broader finding that exact
output control is weaker than the model's raw analysis capability.

## Current evidence-based interpretation

DeepSeek V4 Flash 0731 is extremely fast and highly capable on bounded coding,
CI, writing, and research tasks. It is not uniformly reliable across artifact
modalities: spreadsheet finance correctness and final visual QA are material
weaknesses. On marathon agent tasks it can perform excellent investigation and
testing, yet either stop after scaffolding or enter an extremely long response
instead of continuing tool use. The full-context campaign proves that this is
a model-control failure rather than an artifact of the earlier 180K convenience
ceiling: one valid run generated 815,279 tokens in a single response and still
did not recover tool use.
