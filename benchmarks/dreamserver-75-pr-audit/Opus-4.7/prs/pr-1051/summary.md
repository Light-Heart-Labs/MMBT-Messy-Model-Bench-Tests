# PR #1051 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(resolver): hoist yaml import, guard empty manifests, align user-ext loop

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1029.** This branch shares `scripts/resolve-compose-stack.sh` with the resolver gpu_backends sweep in #1029. Mechanical conflict (yaml import position + user-ext loop overlap) is small and resolves cleanly with a `git rebase upstream/main` once #1029 lands. Promote to ready-for-review after that rebase.

## What
Three resolver-hygiene improvements in `scripts/resolve-compose-stack.sh`:
1. Hoist the optional PyYAML `import yaml` above both extension loops.
2. Add an `isinstance(manifest, dict)` guard after every `yaml.safe_load` / `json.load` so empty manifests warn-and-skip instead of crashing the resolver with `AttributeError`.
3. Align the user-extension loop's structure with the built-in loop (compose_file from manifest, .disabled handling, compose.local.yaml + compose.multigpu.yaml overlays). Deliberately omits `gpu_backends` filtering — that's #1029's scope.

## Why
**1. Yaml hoist:** post-#1029 the user-extension loop also reads manifests, so it also needs `yaml`. Hoisting now means one shared `yaml_available` binding instead of two duplicate try/except blocks.

**2. Empty-manifest guard:** `yaml.safe_load()` returns `None` for an empty / comment-only YAML file. `manifest.get("schema_version")` then raises `AttributeError: 'NoneType' object has no attribute 'get'`. The narrow exception handler at lines 205–221 only catches `yaml.YAMLError`, `json.JSONDecodeError`, and `(KeyError, TypeError)` — `AttributeError` falls through and crashes the e  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
