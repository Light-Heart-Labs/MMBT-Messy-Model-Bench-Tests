# Password Manager Recommendation — README

## Overview

This repository contains the research, analysis, and recommendation for standardizing a password manager for a 50-person engineering team at a Series-B SaaS company.

## Deliverables

| File | Description |
|------|-------------|
| [`recommendation.md`](recommendation.md) | **Primary deliverable.** 1-2 page recommendation memo with decision criteria, product recommendation, runner-up, and concerns. |
| [`comparison.md`](comparison.md) | Side-by-side feature/pricing/security comparison of the 5 evaluated products. |
| [`sources.md`](sources.md) | Every URL fetched during research, with timestamps and descriptions. |
| [`research/notes.md`](research/notes.md) | Working notes from the research process. |
| [`decisions/`](decisions/) | ADR-style records for key decisions: |
| &nbsp;&nbsp;`decisions/001-select-5-products.md` | Which 5 products were selected and why. |
| &nbsp;&nbsp;`decisions/002-evaluation-criteria.md` | What criteria were used and how they were weighted. |
| &nbsp;&nbsp;`decisions/003-recommendation.md` | The final recommendation and rationale. |

## Quick Summary

- **Recommended:** 1Password Business at $7.99/user/month ($4,794/year for 50 seats)
- **Runner-up:** Bitwarden Enterprise at $6.00/user/month ($3,600/year for 50 seats)
- **Disqualified:** LastPass (security incidents), Dashlane (no Linux support)
- **Not selected:** Keeper (less mature developer tooling)

## How to Read

1. Start with [`recommendation.md`](recommendation.md) for the executive summary and rationale.
2. Refer to [`comparison.md`](comparison.md) for detailed feature-by-feature comparison.
3. Check [`sources.md`](sources.md) for source verification of any factual claim.
4. Review [`decisions/`](decisions/) for the decision-making process.

## Methodology

- 5 password managers were evaluated: 1Password, Bitwarden, LastPass, Dashlane, Keeper.
- 7 weighted criteria were defined before evaluation (see ADR-002).
- All factual claims are cited with source URLs.
- Pricing data was extracted from official vendor pages and cross-checked with third-party comparison articles.
- Security incident history was verified against Wikipedia and official vendor statements.

## Limitations

- LastPass and Dashlane Business pricing are not publicly listed; "contact sales" was required.
- Some vendor pages are JavaScript-rendered, requiring extraction from embedded JSON data.
- Keeper Business pricing was found in a ZDNet comparison article, not on Keeper's own site.
