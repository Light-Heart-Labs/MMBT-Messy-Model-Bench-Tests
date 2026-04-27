# PR #1054 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): require deployable compose.yaml to mark extension installable

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Tighten `_is_installable` in `routers/extensions.py` so an extension is only advertised as installable when it actually has a deployable `compose.yaml` on disk.

## Why
The library currently ships three entries that have only `compose.yaml.disabled` or `compose.yaml.reference` files:

- `dify`, `jan` — only `compose.yaml.disabled`
- `fooocus` — only `.reference` files

The predicate did `(library_dir / ext_id).is_dir()`, so the dashboard rendered Install buttons for them. Clicking Install copied the directory into `user-extensions/`, but the host agent could not start a service because no compose was deployable. Users saw cryptic errors with no clear cause.

`aider` keeps a real `compose.yaml` with `entrypoint: ["echo"]` and `restart: "no"` — that's intentional CLI-tool surface and remains installable, matching existing UX.

## How
Single-function change. New body checks both directory presence AND a deployable `compose.yaml`:

```python
def _is_installable(ext_id: str) -> bool:
    ext_dir = EXTENSIONS_LIBRARY_DIR / ext_id
    return ext_dir.is_dir() and (ext_dir / "compose.yaml").exists()
```

No schema change, no manifest field added, no frontend change. Catalog response shape is unchanged — only the `installable` boolean flips for the three affected entries. Both call sites consume the bool directly; no signature change.

## Testing
- `python3 -m py_compile` PASS.
- `ruff check` PASS.
- `pytest tests/` (dashboard-api) — 137/137 PASS, no new failures.
- Sanity-chec  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
