# Gemma 4 31B QAT Q4_0 on Tower2: verified MMBT campaign

This entry publishes the complete Gemma 4 31B QAT Q4_0 campaign on two RTX
PRO 6000 Blackwell Workstation Edition GPUs. It separates bounded-task grades,
grader corrections, serving measurements, operational completion, and strict
artifact review.

## Read order

1. [`GEMMA4_31B_Q4_VERIFIED_RESULTS.md`](GEMMA4_31B_Q4_VERIFIED_RESULTS.md)
   is the results and cross-model interpretation.
2. [`GEMMA4_31B_Q4_COMPLETION_AUDIT.md`](GEMMA4_31B_Q4_COMPLETION_AUDIT.md)
   maps campaign requirements to evidence.
3. `gemma4-canonical-n{3,10}-scorecard.json` preserve raw grades and runtime
   measurements; the project-management correction files are separate,
   hash-tied overlays.
4. `substantive-audit.json` records the independent finance, deck, code, and
   75-PR findings. `gemma4-extended-evidence-audit.json` is the separate
   identity/configuration/preservation audit.
5. The reproducible deployment package is under
   [`../../tooling/deployments/gemma4-31b-q4-tower2/`](../../tooling/deployments/gemma4-31b-q4-tower2/).

## Headline results

- Canonical N=3: **29/36 raw; 32/36 corrected**.
- Canonical N=10: **89/120 raw; 99/120 corrected**.
- Operational completion: **116/120** ordinary runs reached `done_signal`;
  four hallucination tasks stopped without the required output.
- Median model-call decode rate: **55.85 tok/s**; median task wall time:
  **113.05 seconds**.
- Extended strict substantive result: **0/12**. All evidence is preserved, but
  no extended replicate passed the full common and modality-specific gates.

The corrected overlay changes only ten project-management lexical false
negatives. Original grades remain untouched. No canonical failure is caused by
an artificial output ceiling: the model was served and requested at its native
262,144-token envelope. One server-transport timeout below that envelope was
classified infrastructure-invalid, preserved, and replaced exactly once.

## Comparison to Qwen3.6-27B

Gemma is the clear bounded-quality winner in the directly comparable N=3
matrix: 29/36 raw and 32/36 corrected versus Qwen3.6-27B thinking's 20/36 raw.
The models are nearly tied for short-context single-stream decode at 500 W
(70.3 tok/s Gemma versus 72.1 tok/s Qwen), but Qwen's vLLM stack is vastly
stronger under dense batching. Gemma's accepted two-replica llama.cpp topology
instead prioritizes four independent native-256K slots per GPU and failure
isolation.

Qwen3.6-27B no-think's published 113/118 is a `done_signal` rate, not a
quality-grade rate, and must not be compared directly to Gemma's 99/120
corrected quality score. On marathon work, neither model passes the frozen
75-PR standard: Qwen's published result contains 72 template verdicts, while
Gemma's three attempts completed only 6 reviews, 2 directories, and then 75
directories with just 14 parsable verdicts.

## Bottom line

Gemma is a strong dense local model for bounded coding, extraction, CI,
document synthesis, market research, and multi-audience writing. It is not the
best overall model for this 190 GB VRAM system: DeepSeek V4 Flash remains the
stronger default on corrected bounded quality, context, throughput, and
single-PR execution. Gemma also should not be trusted unattended for finance,
presentation QA, or monolithic repository-wide audits without hard artifact
gates and staged review.
