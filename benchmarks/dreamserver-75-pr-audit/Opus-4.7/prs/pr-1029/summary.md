# PR #1029 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Two resolver fixes bundled:
1. Stop appending `docker-compose.override.yml` twice to `COMPOSE_FLAGS`.
2. Apply the same `gpu_backends` filter to user-installed extensions that built-in extensions already receive.

## Why
**Defect 1:** `installers/lib/compose-select.sh` called the resolver (which appends `docker-compose.override.yml` internally) and then appended it again at the bash layer. Docker merges the file twice — idempotent for scalars but a foot-gun for anchors / `extends:` / list-merge semantics.

**Defect 2:** `scripts/resolve-compose-stack.sh` read the manifest and filtered by `gpu_backends` for built-in extensions but included every `data/user-extensions/*/compose.yaml` unconditionally. A user-library extension declaring `gpu_backends: [nvidia]` would be merged on AMD/Apple and fail at container start — or worse, block any `depends_on` chain.

## How
- **compose-select.sh:** delete the now-redundant `if [[ -f ... override.yml ]]` block after `load_env_from_output`.
- **resolve-compose-stack.sh (inline Python):** mirror the built-in loop's filter verbatim into the user-extension loop. Same manifest lookup order (`.yaml` -> `.yml` -> `.json`), same `schema_version == "dream.services.v1"` gate, same `gpu_backends` default `["amd","nvidia"]`, same `"all"`/`"none"` sentinels, same narrow yaml/json/structure exception dispatch honouring `skip_broken`.

The intentional scope limit: user-extension loop still hardcodes `compose.yaml` and does not apply `compose.loc  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
