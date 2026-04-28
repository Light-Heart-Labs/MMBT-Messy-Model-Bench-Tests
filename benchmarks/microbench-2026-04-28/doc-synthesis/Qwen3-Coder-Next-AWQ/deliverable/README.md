# Nimbus Logistics, Inc. — Deal Evaluation Package

## Overview

This package contains the deliverables for an executive brief evaluating whether to make a follow-on investment in Nimbus Logistics, Inc., a Series-B logistics-tech startup.

## Files

| File | Purpose |
|------|---------|
| `brief.md` | **The 1-page executive brief** — your primary deliverable. Contains the recommendation (Pass), key facts, tensions, and conditions for reconsideration. |
| `key-facts.md` | A list of every material fact incorporated into the brief, with source attribution. |
| `research/notes.md` | Working notes from reading the five sources, including source summaries, key tensions, and source quality assessment. |
| `decisions/adr.md` | ADR-style records for framing choices (e.g., why “Pass” instead of “More Diligence Needed”). |
| `README.md` | This file — how to read the output. |

## How to Read the Brief

1. **Start with the recommendation** — “Pass, unless…” — stated in the first paragraph.
2. **Read the company’s story** — the press release narrative ($84M raise, $560M valuation, $42M ARR).
3. **Read the reality check** — contradictions from TechCrunch, the leaked memo, and the former employee blog.
4. **Review the key risks** — customer concentration, churn, high burn, layoffs.
5. **Note the conditions for reconsideration** — what would need to be verified to change the stance.

## Source Attribution

All facts in `brief.md` are cited inline using `[Source N]`:
- `[Source 1]` — Press release (company-issued)
- `[Source 2]` — TechCrunch news article
- `[Source 3]` — Former-employee blog post
- `[Source 4]` — Leaked internal memo
- `[Source 5]` — SEC Form D filing summary

## Key Contradictions

The brief highlights tensions between the company’s narrative and the reality reported elsewhere:
- **Valuation:** $560M (press release) vs. repriced from $720M (TechCrunch)
- **ARR:** $42M (press release) vs. $36–37M adjusted (TechCrunch)
- **Growth:** “Accelerate international expansion” (press release) vs. “Pause EMEA hiring, reduce Berlin” (internal memo)
- **Runway:** Aggressive growth narrative vs. “insurance, not operating capital” (internal memo)

## Recommendation Logic

The recommendation is **Pass** because:
- The company is in defensive mode (layoffs, international retreat, credit facility as insurance)
- High customer concentration (top 5 = 38% of ARR) with two top-5 customers lost
- High burn ($4M/mo vs $3.5M/mo revenue) suggests unsustainable model
- Net retention >110% is inconsistent with churn unless offset by massive new logo growth

The stance is calibrated: if the investor can verify net retention >110%, adjusted ARR stable/growing, and the three new $1M+ contracts fully signed, the recommendation would change.
