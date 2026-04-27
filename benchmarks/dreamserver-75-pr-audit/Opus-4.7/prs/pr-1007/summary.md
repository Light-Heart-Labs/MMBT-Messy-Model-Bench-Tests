# PR #1007 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): double-quote tmpdir in gpu_reassign RETURN trap

## Author's stated motivation

The PR body says (paraphrased):

> ## What
`_gpu_reassign` registered its cleanup trap with single-quoted outer
syntax:

```bash
trap 'rm -rf "$tmpdir"' RETURN
```

Single-quoted outer defers `$tmpdir` expansion until trap fire time.
RETURN traps are process-level (not function-scoped), so after
`_gpu_reassign` returns to `cmd_gpu` the trap fires again in
`cmd_gpu`'s scope where `$tmpdir` is unbound. Under `set -u` that
triggers `tmpdir: unbound variable` and exit 1 even on a successful
reassign.

## How
Switched to double-quoted outer so `$tmpdir` is baked in at
trap-set time:

```bash
trap "rm -rf '$tmpdir'" RETURN
```

Single-quoted inner continues to protect paths containing spaces.
Matches the already-landed pattern at `dream-cli:542`.

## Platform Impact
- macOS Apple Silicon / AMD / CPU: unaffected — the `nvidia-smi`
  early-return at line 2825 precedes the trap registration.
- Linux NVIDIA: fixed.
- Windows WSL2 + NVIDIA passthrough: fixed (same Bash semantic).
- Windows WSL2 + AMD / Linux AMD Lemonade: unaffected (no
  `nvidia-smi`, same early-return).

## Testing
- `bash -n` passes.
- `shellcheck` shows the same `SC2064` on line 2869 as on the
  precedent line 542 — intentional (we want expansion at set time).
- Bash repro: `bash -c 'set -u; f(){ local t; t=$(mktemp -d); trap "rm -rf \"$t\"" RETURN; }; g(){ f; return 0; }; g'` → exit 0.

## Merge order (important)
This fix is **preventive** on upstream/main today: `dream-cli` is
on `set -e` only, so the unbound-variable crash does not manifest
yet. I  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
