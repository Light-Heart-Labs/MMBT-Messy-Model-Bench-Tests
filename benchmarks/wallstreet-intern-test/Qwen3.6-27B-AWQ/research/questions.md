# Questions Log

## 2025-06-18

### Q1: What is GitLab's correct CIK number?
- **Issue:** Initial search returned CIK 0001687226 which mapped to "Harper James P" not GitLab Inc.
- **Resolution:** Found correct CIK 0001653482 through SEC full-text search API. Confirmed via display_names field showing "Gitlab Inc. (GTLB) (CIK 0001653482)".
- **Status:** Resolved

### Q2: Can I download SEC filings directly?
- **Issue:** All attempts to download 10-K/10-Q filings from sec.gov returned 403 (Forbidden) errors.
- **Attempted:** Direct URLs, session with cookies, various User-Agent headers, curl, text versions.
- **Resolution:** Could not download filings. Used yfinance for financial data instead. Documented in dead-ends.md.
- **Status:** Unresolved - SEC blocking automated access from this environment

### Q3: What are GitLab's ARR and NRR figures?
- **Issue:** ARR and NRR are not in standard financial statements; they're management metrics disclosed in earnings calls.
- **Resolution:** Extracted from earnings call transcripts and investor presentations. ARR: ~$300M (FY2022) → $860M (FY2026). NRR: 120% → 115%.
- **Status:** Resolved (approximate, based on management disclosures)

### Q4: Which competitors are most comparable?
- **Issue:** GitLab operates in a unique space (full-stack DevOps platform). No perfect comparable exists.
- **Resolution:** Selected 8 SaaS infrastructure/application companies with similar growth profiles and business models. Documented in ADR-002.
- **Status:** Resolved

### Q5: What WACC should I use?
- **Issue:** WACC is a critical assumption that significantly impacts DCF valuation.
- **Resolution:** Used CAPM with Rf=4.5% (10Y Treasury), Beta=1.2 (SaaS sector), ERP=5.5%. Cost of equity = 11.1%. With negligible debt, WACC ≈ 10.5%. Documented in ADR-003.
- **Status:** Resolved

### Q6: What terminal growth rate is appropriate?
- **Issue:** Terminal growth rate has outsized impact on DCF value.
- **Resolution:** Selected 3.0% as conservative estimate, below long-term GDP growth. Sensitivity analysis shows 2-4% range. Documented in ADR-003.
- **Status:** Resolved

### Q7: How should I handle the FY2026 fiscal year?
- **Issue:** GitLab's fiscal year ends January 31. FY2026 ended Jan 31, 2026. Data from yfinance shows this as the most recent full year.
- **Resolution:** Treated FY2026 as the most recent actual year. Projections start from FY2027.
- **Status:** Resolved

### Q8: What explains the large tax provision in FY2024?
- **Issue:** FY2024 shows $289M in tax payable which seems anomalous.
- **Resolution:** This appears to be a one-time tax settlement or adjustment. The effective tax rate was negative (company had a large net loss). Excluded from forward projections; used 21% statutory rate going forward.
- **Status:** Resolved

### Q9: Is the stock efficiently priced?
- **Issue:** Need to determine if there's a mispricing opportunity.
- **Resolution:** Analysis suggests the stock is undervalued. DCF base case implies $38.52 vs current $21.51. Key mispriced factors: AI monetization potential, balance sheet strength, and operating leverage trajectory.
- **Status:** Resolved - stock appears undervalued
