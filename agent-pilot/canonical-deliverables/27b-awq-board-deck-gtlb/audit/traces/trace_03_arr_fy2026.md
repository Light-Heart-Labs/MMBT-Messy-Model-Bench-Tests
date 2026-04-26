# Trace: ARR FY2026 = $860M

**Slide:** 5 (SaaS Metrics)
**Claim:** "ARR reached $860M in FY2026"

**Source Chain:**
1. Primary source: `/input/repo/extracted/financial_summary.json`
   - Field: `arr[4]` = 860 (in millions)
2. Secondary: `/input/repo/memo/gitlab_investment_memo.md`
   - "ARR: $860M (FY2026)"
3. Tertiary: `/input/repo/raw/transcripts/GTLB_Q*_transcript.txt`
   - ARR figures disclosed in earnings call transcripts

**Note:** ARR is a management metric, not a GAAP figure. It was extracted from earnings call transcripts and is an estimate based on management disclosures.

**Verification Steps:**
1. Open `/input/repo/extracted/financial_summary.json`
2. Find `arr[4]` = 860
3. Confirm: $860M ✓
4. For original source: check `/input/repo/raw/transcripts/GTLB_Q4_2024_transcript.txt` for ARR disclosure
