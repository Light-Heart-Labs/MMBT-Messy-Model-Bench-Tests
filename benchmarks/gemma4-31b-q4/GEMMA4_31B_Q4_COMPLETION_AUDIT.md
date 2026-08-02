# Gemma 4 31B Q4 campaign completion audit

| Requirement | Evidence | Status |
|---|---|---|
| Exact model and runtime pinned | Deployment `model-manifest.json` and `benchmark-serving-manifest.json` include upstream revision, byte size, SHA-256, llama.cpp commit/binary hash, CUDA build, and sampling | Complete |
| Best stable two-GPU topology selected | Preregistered topology bakeoff rejected corrupt/unsupported split modes and selected two independent four-slot Q8-KV replicas | Complete |
| Full native context used | Every slot and request cap is 262,144; long-context recall passed at 245,347 total tokens | Complete |
| 500 W safety envelope | Both replicas and every receipt use 500 W per GPU; telemetry records actual per-run power/utilization | Complete |
| Sanctuary and Pixel validated before testing | Both agents passed isolated routing, chat, tool-call, and tool-follow-up checks on their dedicated replicas | Complete |
| Canonical N=3 and N=10 complete | 36/36 and 120/120 evidence cells audited; raw and corrected results remain separate | Complete |
| Low-ceiling failures excluded | No canonical failure hit an artificial output cap. One proven one-hour transport cancellation below native context is preserved as infrastructure-invalid and exactly replaced | Complete |
| Extended suites complete | Twelve valid runs plus one preserved invalid supervisor attempt; identity/configuration/preservation audit rerun after replacement | Complete |
| Strict modality review complete | Workbooks inspected, deck files rendered and visually reviewed, single-PR results independently reproduced, all 75-PR outputs structurally audited | Complete |
| Harness findings repaired | Substance monitor handles malformed arguments; tag gate requires clean repo + annotated tag at HEAD; 75-PR auditor fails closed on missing files | Complete |
| Cross-model comparison pinned | `tooling/gemma4-comparison-sources.json` freezes Qwen3.6-27B, Qwen3.6-35B-A3B, Coder-Next, Qwen3.5-397B, and DeepSeek evidence hashes | Complete |
| Publish/merge | This entry, audit overlays, scorecards, and deployment package are delivered by the merge containing this audit | Complete |
| Restore production | Exact pre-campaign OpenClaw config and proven DeepSeek launcher restored; DeepSeek health/model route, 500 W caps, portals, and fresh Sanctuary/Pixel `exec` calls passed with no fallback | Complete |

The evidence audit and the quality audit answer different questions. The former
proves what ran and that the bytes were preserved. The latter deliberately
fails polished-but-incomplete artifacts. Consequently, all 12 extended runs
are accounted for while zero receive a strict substantive pass.

The post-campaign restore receipt is also embedded in
`tooling/deployments/gemma4-31b-q4-tower2/final-validation.json`. The restored
OpenClaw config exactly matches its pre-campaign SHA-256, DeepSeek advertises
the proven 1,048,576-token route, and both production agents independently
executed and observed a marker command. Ninety-six campaign sandbox containers
were stopped but not deleted, preserving their recoverability while returning
the production host to the proven DeepSeek stack.
