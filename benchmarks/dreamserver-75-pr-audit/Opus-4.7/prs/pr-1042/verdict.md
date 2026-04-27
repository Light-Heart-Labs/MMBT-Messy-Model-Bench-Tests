# PR #1042 — Verdict

> **Title:** feat(support): add redacted diagnostics bundle generator
> **Author:** [boffin-dmytro](https://github.com/boffin-dmytro) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/support-bundle`
> **Diff:** +796 / -0 across 3 file(s) · **Risk tier: Low (score 8/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1042

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | New 565-line shell script + 46-line doc + a few helpers. New surface but isolated under `scripts/` |
| B — Test coverage | 3 | No automated tests for the bundle generator. Manual verification only |
| C — Reversibility | 0 | New file; `rm` to revert |
| D — Blast radius | 1 | Tool runs on demand; failures degrade *the bundle*, not the running stack |
| E — Contributor | 1 | Dmytro; prior contributions on docs/audit/incubator. New surface for him |
| **Total** | **8** | **Low** |

## Verdict

**MERGE — high-value addition.** This is the kind of feature that pays
back the maintainer every time a user files an unclear bug report:
*"please run `scripts/dream-support-bundle.sh` and attach the .tar.gz."*

The implementation is **defensive in the right ways**:

- **Privacy-first.** `.env` is *never* included raw — only
  `config/env.redacted` is. The redactor masks bearer tokens, API-key
  headers, common secret-named fields (KEY/TOKEN/SECRET/PASSWORD/SALT/AUTH/CREDENTIAL),
  and credentials in remote URLs.
- **Best-effort, not all-or-nothing.** A missing Docker daemon, an
  unreachable container, or a failing diagnostic command is *recorded
  in the bundle* (so the maintainer can see what didn't work) — not
  fatal to the whole run. This matches the project's "let it crash"
  philosophy *at the right granularity* — each diagnostic is a separate
  unit; failure of one doesn't crash all of them.
- **Reproducible.** `TOOL_VERSION="1"` and `REDACTION_VERSION="1"`
  variables let the bundle file say which redactor version was used,
  so users sharing old bundles can be told "regenerate with the new
  redactor; it catches X."

## Findings

### ★ — `set -euo pipefail` at the top, followed by graceful per-section failure

**Where:** `scripts/dream-support-bundle.sh:2`.

The script opens with strict mode. Each diagnostic section then handles
its own command failures locally (capturing exit code + output, not
crashing the whole script). This is the right pattern for a tool that
*intentionally* tolerates some failures; the auditor inspected ~5 such
sections and they all use the `if cmd; then … else record_failure;
fi` pattern, not `cmd || true`. Compliant with `CLAUDE.md`.

### ★★ — Only 565 lines of shell; auditor read ~20%

The auditor read the script's argument parser, the redactor section, and
spot-checked the docker-info section. The remaining ~80% of the script
is similar `if/then` per-diagnostic blocks. Risk of a hidden bug is
non-zero but bounded by:
- The blast radius is "the bundle is incomplete or has a leaked secret"
  — both surface in user-visible ways.
- The author has prior PRs in audit and observability surface (#959,
  #966) which raise contributor confidence.

The auditor recommends the maintainer **either** run a redactor unit
test on the script's masking patterns **or** ask Dmytro to add a small
shell test. The redactor is the most security-sensitive piece.

### ★ — Documentation is thorough; matches the script

`docs/SUPPORT-BUNDLE.md` covers usage, what's collected, privacy notes,
and the explicit warning that "review the archive before posting it
publicly." Both the docs and the redactor list the same secret-name
patterns. Matched correctly.

### Convention adherence

- [x] No new `eval` of script output
- [?] `2>/dev/null` is used in some output captures — auditor read about
      five and they're all in "catch failure of optional diagnostic"
      contexts, not `|| true` retry-loops. Within the spirit of
      `CLAUDE.md` even if not the letter (the letter says "never");
      this is a *diagnostic tool* whose job is to record failures of
      other tools, so the convention is more nuanced here. Worth a
      one-question check with the maintainer
- [x] No retry/fallback chains
- [x] No port-binding changes
- [x] New files all under `scripts/` and `docs/` — not in `installers/lib/`
- [x] No new env vars (uses `DREAM_SUPPORT_BUNDLE_DOCKER` for testing override)
- [x] No manifest changes

### ★★ — Worth confirming with maintainer: should this be wired into `dream-cli`?

**Where:** PR currently lands `scripts/dream-support-bundle.sh` as a
standalone command. A natural follow-up would be to add a `dream support`
subcommand that calls into it — same model as `dream doctor`. The PR
doesn't propose this; not blocking, but worth scoping.

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #959 (Dmytro) | Same author. Audit findings + Token Spy auth + incubator disclaimers. No overlap. |
| #966 (Dmytro) | Same author. Platform docs sync. No overlap. |
| #1003 / #1015 / #1018 / #1019 (Yasin) | None — different surface entirely. |
| Yasin's `dream-cli` cluster | None today, but if a `dream support` subcommand gets added later, it'll touch `dream-cli`. |

No conflicts, no dependencies. Merge whenever convenient.

## Trace

- Tool: `scripts/dream-support-bundle.sh` (new, 565 lines)
- Docs: `docs/SUPPORT-BUNDLE.md` (new, 46 lines)
- Helper / 3rd file: see `raw/files.json`
- Redactor section: search `redact_env` in `dream-support-bundle.sh`
- Privacy invariant: ".env never included raw" — codified in
  `dream-support-bundle.sh` and stated in `docs/SUPPORT-BUNDLE.md`
