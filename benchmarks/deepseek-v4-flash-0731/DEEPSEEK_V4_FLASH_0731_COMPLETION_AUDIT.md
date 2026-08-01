# DeepSeek V4 Flash 0731 completion audit

Audit date: 2026-08-01

This checklist maps every requested outcome to current authoritative evidence.
An item is marked complete only where the evidence covers the full requirement.

| Requirement | Authoritative evidence | Verdict |
|---|---|---|
| Stable, optimal two-GPU deployment | `tooling/deployments/deepseek-v4-flash-0731-tower2/final-validation.json`; active launcher SHA-256 `4fca6a4a...`; active image `sha256:48518e91...`; current container `running`, zero restarts, `OOMKilled=false` | Complete |
| Direct correctness, performance, load, context, and restart proof | Accepted validation records 7,255.113 prompt tok/s at 128K, 271.778 single decode, 850.143 C4, 1,373.176 C8, successful 1,019,753-token recall, shared-prefix A/B passes, and 132.1-second clean restart | Complete |
| Safe power envelope | Persistent `nvidia-powerlimit.service` enabled and active; both GPUs currently report 500 W; matched test retained 95.8% of 600 W prefill performance | Complete |
| Sanctuary and Pixel functional before benchmarking | Accepted validation records successful pre- and post-restart checks for both agents before the campaign | Complete |
| Sanctuary and Pixel functional at handoff | Isolated post-campaign gateway turns used provider `tower`, model `DeepSeek-V4-Flash-0731`, 1,048,576-token context, and no fallback. Final turns actually invoked sandbox `exec`, received successful tool results, and returned exact markers in 1.812 s and 2.284 s | Complete |
| Historical MMBT suites and standards inspected | `tooling/deepseek-v4-flash-extended-matrix.json` names the Qwen3.5-397B-A17B, Qwen3.6-27B-AWQ/Q8, and Qwen3-Coder-Next-AWQ comparison arms; pins suite/task hashes, sampling, output limits, fixture identity, logging requirements, and every known comparability difference | Complete |
| Comparable DeepSeek matrix prepared and smoke-tested | Canonical config `tooling/deepseek-v4-flash-0731-mmbt.json`, extended matrix, two preflight smoke logs, shared-prefix smoke logs, and the frozen-fixture set SHA-256 `569b95b3...` | Complete |
| Canonical suites run and scored | 36/36 N=3 run directories contain cost, transcript, receipt, workspace archive, GPU telemetry, summary, and grade. `status.corrected-35of36.json` records 32 PASS, 3 STRUCTURAL_PASS, and 1 genuine FAIL | Complete |
| Grader defects remediated without rewriting model output | Raw grades and status remain preserved; `canonical-regrade-audit.json` hashes unchanged workspace archives and both raw and corrected grades; `model_rerun=false` | Complete |
| Extended suites run | Three single-PR, three investment, three board-presentation, and five preserved 75-PR attempts are present with receipts, transcripts, summaries, archives, and GPU telemetry or an explicit terminal audit | Complete |
| Invalid runs handled fairly | The live-272 attempt is retained under `_infra_invalid`; old-cap 75-PR v2/v3 are preserved but excluded; full-context v4/v5 replacements produced exactly three valid campaign outcomes | Complete |
| 75-PR campaign complete at model capability ceiling | `logs/_campaign_audit/75pr-valid-replicates.json` reports `status=complete`, served and configured ceiling 1,048,576, dynamic reserve 14,000, and valid v1/v4/v5 outcomes. Strict result is 0/3, including the valid 815,279-token runaway-generation terminal failure | Complete |
| Complete artifacts and telemetry preserved | Canonical logs contain 227 parse-valid JSON artifacts; extended logs contain 67. The copied valid-replicate manifest matches its live source at SHA-256 `9a246372...`; compact audits and full run archives remain available | Complete |
| Results, caveats, configuration, and lessons documented | `benchmarks/deepseek-v4-flash-0731/README.md`, `DEEPSEEK_V4_FLASH_0731_VERIFIED_RESULTS.md`, compact audit JSONs, deployment README, campaign README, and `tooling/MMBT-75PR-AUDIT-PROTOCOL.md` | Complete |
| Clean operational handoff | Benchmark services inactive; campaign power logger stopped after flush; 14 sandbox containers stopped but retained; production model healthy; persistent power cap and OpenClaw gateway active | Complete |

## Final disposition

All requested deployment, validation, benchmarking, preservation, comparability,
documentation, and production-handoff requirements are proven complete. The
model itself did not pass every benchmark: the verified 75-PR result is 0/3,
finance quality is 0/2 substantively valid, and the board deck has material
visual defects. Those are benchmark findings, not missing campaign work.
