# Trace: NRR 115%

**Slide:** 5 (SaaS Metrics)
**Claim:** "NRR: 115% (declining from 120%)"

**Source Chain:**
1. Primary source: `/input/repo/extracted/financial_summary.json`
   - Field: `nrr[4]` = 115
   - Field: `nrr[0]` = 120
2. Secondary: `/input/repo/memo/gitlab_investment_memo.md`
   - "NRR: 118% → 117% → 116% → 115%"
3. Tertiary: `/input/repo/raw/transcripts/GTLB_Q*_transcript.txt`
   - NRR disclosed in earnings call transcripts

**Note:** NRR is a management metric, not a GAAP figure. It was extracted from earnings call transcripts.

**Verification Steps:**
1. Open `/input/repo/extracted/financial_summary.json`
2. Find `nrr` array: [120, 118, 117, 116, 115]
3. Confirm: FY2026 NRR = 115% ✓
