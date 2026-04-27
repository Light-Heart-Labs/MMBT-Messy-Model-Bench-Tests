# PR #1057 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Seven small surgical edits in \`dream-server/bin/dream-host-agent.py\` that harden the host agent's install and model-validation paths against silent failures, misleading error surfacing, and a couple of long-form Compose volume cases the pre-create logic was missing.

## Why
The host agent is the dispatcher between the dashboard-api and Docker. Most of its current failure paths either truncate diagnostics (head-truncation of stderr drops the actual error in favour of the layer-pull preamble), swallow OSError silently (frozen progress bars, no journal record), or conflate distinct error classes (HTTP 403 vs 500). When something goes wrong, operators see a misleading symptom and have to read the journal — often to find that nothing was logged because the failure was swallowed.

Concretely:

1. **Narrow \`docker compose pull\`.** Currently runs with the FULL merged compose stack, so a single \`\${VAR:?}\` guard in any unrelated extension's compose aborts the pull for the target extension with an error message naming the wrong extension.
2. **\`stderr[:N]\` head-truncation at three sites in \`_handle_install\`.** Docker-compose puts the real error at the END of stderr — head-truncation drops exactly the diagnostic bytes the operator needs.
3. **\`_write_model_status\` silent OSError swallow.** Disk-full or permission errors freeze the dashboard progress bar with no journal trace.
4. **\`_recreate_llama_server\` silent docker-run failure.** Logs but does not raise; caller  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
