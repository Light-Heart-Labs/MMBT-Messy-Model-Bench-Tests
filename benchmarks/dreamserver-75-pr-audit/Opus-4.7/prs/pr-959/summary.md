# PR #959 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix: address audit findings — Windows docs, Token Spy auth, and incubator disclaimers

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

Addresses all 4 findings from the project audit (3 High, 1 Medium):

### Windows support messaging (High)
- **WINDOWS-QUICKSTART.md**: remove "Coming Soon" language, update to reflect current supported status with actual working commands
- **SUPPORT-MATRIX.md**: update CI section to reflect all smoke coverages already running; fix roadmap framing
- **README.md**: minor alignment with platform support table

### Token Spy auth flow (High)
- **main.py**: strip `authorization` from forwarded headers in both Anthropic and OpenAI proxy endpoints; inject upstream auth via new `_get_upstream_auth_headers()` helper that uses `UPSTREAM_API_KEY` for hosted providers and allows local upstreams without auth
- **TOKEN-SPY-GUIDE.md, README.md**: document the two-key model (`TOKEN_SPY_API_KEY` for dashboard, `UPSTREAM_API_KEY` for upstream) and explicitly state this is not a transparent drop-in proxy

### Incubator doc disclaimers (High)
- **PHASE1-ARCHITECTURE.md**: add prototype/incubator disclaimer, change "Implementation Complete" to "Prototype Complete"
- **resources/products/token-spy/README.md, PRODUCT-SCOPE.md**: add disclaimers distinguishing incubator work from shipped extension

### CI smoke claims (Medium)
- **SUPPORT-MATRIX.md**: accurately reflects all four smoke coverages (Linux AMD, Linux NVIDIA, Windows/WSL, macOS) as already running

## Test plan

- [ ] Verify WINDOWS-QUICKSTART.md, SUPPORT-MATRIX.md, and README.md all say Windows is supported today
- [ ] Verif  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
