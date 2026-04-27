# PR #959 — Verdict

> **Title:** fix: address audit findings — Windows docs, Token Spy auth, and incubator disclaimers
> **Author:** [boffin-dmytro](https://github.com/boffin-dmytro) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/audit-docs-and-token-spy-auth`
> **Diff:** +23 / -9 across 3 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/959

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 1 | _see review.md_ |
| **Total** | **6** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REVISE — small.** Good intent, but the diff and the PR body are out of sync. The body promises four audit-finding fixes (Windows docs, Token Spy auth, incubator disclaimers, CI smoke claims). The actual diff only delivers the **incubator disclaimer** changes across three files in `resources/products/token-spy/` (PHASE1-ARCHITECTURE.md, PRODUCT-SCOPE.md, README.md). No `WINDOWS-QUICKSTART.md`, no `SUPPORT-MATRIX.md`, no `main.py` Token Spy auth changes, no header strip helper. As shipped, this is just docs disclaimer hygiene.

## Findings

- **Diff is a strict subset of the body.** The actual changes are limited to prepending a "Prototype / incubator track" callout to three docs, changing "Implementation Complete" → "Prototype Complete," and softening "transparent proxy" claims to "prototype drop-in proxy vision." That's a coherent, low-risk change on its own — but the title says "address audit findings" and lists three High-severity items the diff does not touch.
- **The disclaimer copy itself is well-pitched.** The new wording in `README.md:5-11` distinguishes the `resources/products/token-spy/` incubator subtree from the shipped `dream-server/extensions/services/token-spy/` extension, which is exactly the audit's framing concern. If shipped as-is, this is real value: stops new readers from assuming the prototype docs describe production behavior.
- **Overlap with PR #966.** Dmytro's #966 is the Windows-docs sync that the body of #959 promises. If the maintainer wants the Windows-doc fix specifically, that's #966's scope; #959 should be re-titled to its actual scope ("docs(token-spy): mark incubator subtree as prototype") or have the missing changes pushed.

## Cross-PR interaction

- Same author as PR #966 (also Dmytro / boffin-dmytro). #966 is the Windows-docs PR claimed by #959's body but not delivered. Recommend treating these as "scope split" — #959 = token-spy disclaimers, #966 = Windows docs.
- No file overlap with the other 15 PRs in this batch.
- No semantic conflict with PR #973 (Yasin's docs sync) — different files (`docs/*.md` vs `resources/products/token-spy/*.md`).

## Trace

- `resources/products/token-spy/README.md:5-11` — new "Prototype / incubator track" admonition block.
- `resources/products/token-spy/PHASE1-ARCHITECTURE.md:3-12` — "Implementation Complete" → "Prototype Complete" + admonition.
- `resources/products/token-spy/PRODUCT-SCOPE.md:3-7` — incubator-track admonition.
- Body promises `WINDOWS-QUICKSTART.md`, `SUPPORT-MATRIX.md`, `main.py` (Token Spy `_get_upstream_auth_headers()` helper) — none present in diff.
