# Trace File: NRR FY2026

**Number:** 115%  
**Slide:** 4 (Financial Trajectory)  
**Date:** 2025-06-18

---

## Source Path

`/input/repo/extracted/financial_summary.json`

## File Details

- **File:** financial_summary.json
- **Key:** nrr[4]
- **Value:** 115
- **Formatted:** 115%

## Data Provenance

1. **Source:** Management disclosure (earnings call transcript)
2. **Earnings Call:** GTLB Q4 2024 Earnings Call (March 4, 2024)
3. **Transcript Source:** Seeking Alpha
4. **Transcript File:** `/input/repo/raw/transcripts/GTLB_Q4_2024_transcript.txt`

## Verification Steps

1. Open `/input/repo/extracted/financial_summary.json`
2. Find key "nrr"
3. Value: [120, 118, 117, 116, 115]
4. Index 4 (FY2026): 115
5. Format: 115%

## Notes

- NRR is a management metric, not a GAAP figure
- Derived from earnings call transcripts
- May differ from official figures in SEC filings

## Related Files

- `/input/repo/memo/gitlab_investment_memo.md` - Shows 115% in "Financial Summary"
- `/input/repo/raw/transcripts/GTLB_Q4_2024_transcript.txt` - Original source
- `/input/repo/extracted/financial_summary.json` - Parsed data

## Traceability Chain

```
Deck Slide 4 → 115% → financial_summary.json → earnings call transcript → management disclosure
```

## Verification Time

- **Time to verify:** <2 minutes
- **Steps:** 4 simple steps
- **Difficulty:** Easy
