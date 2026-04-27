# PR #1052 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> test(langfuse): structural guard for setup_hook + hook file coexistence

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1040.** This PR's tests assert that langfuse's `service.setup_hook` and `hooks/post_install.sh` exist. Both are added by upstream PR #1040 (the langfuse postgres uid 70 install fix). Until #1040 merges, these tests fail on bare `upstream/main` — that's expected. Promote to ready-for-review after `git rebase upstream/main` post-#1040.

## What
Add `TestLangfuseManifestHook` to `dream-server/extensions/services/dashboard-api/tests/test_hooks.py`. Two narrow structural-guard assertions that langfuse's manifest declares `service.setup_hook = "hooks/post_install.sh"` AND that the referenced hook file exists on disk.

## Why
The langfuse postgres uid 70 install fix relies on `service.setup_hook` pointing at `hooks/post_install.sh`. If either drifts (file renamed, manifest field removed, hook deleted), the host agent's `_validate_hook_path` returns `None`, `_handle_install` silently skips the hook at the `if hook_path:` guard, and langfuse silently regresses to the broken Linux postgres uid mismatch behaviour with **no CI signal**. The structural guard catches that.

## How
Append a single test class to the existing `test_hooks.py` (the established home for hook-related tests, sharing its `import yaml`, `pathlib.Path`, and class-based conventions):

```python
class TestLangfuseManifestHook:
    def test_langfuse_manifest_declares_post_install_hook(self):
        ext_dir = Path(__file__).resolve().parents[2] / "langfuse"
        manifest = yaml.safe_load(  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
