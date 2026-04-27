# Dead Ends

## 1. SEC Filing Downloads (Attempted 2025-06-18)
**What I tried:** Downloaded 10-K and 10-Q filings directly from sec.gov
**Why it failed:** SEC's website returns 403 (Forbidden) for all automated requests from this environment. Tried multiple approaches:
- Direct URL access with various User-Agent headers
- Session-based requests with cookie collection
- curl with proper headers
- Text version of filings (.txt instead of .htm)
- SEC data API (data.sec.gov) - returned 404 for GitLab's CIK
**Impact:** Could not include original SEC filings in /raw/filings/. Used yfinance data instead, which sources from SEC filings but is a secondary source.
**Lesson:** SEC actively blocks automated access. A human analyst would download filings manually or use a paid data service.

## 2. GitLab Investor Relations Website (Attempted 2025-06-18)
**What I tried:** Accessed investors.gitlab.com for earnings presentations and transcripts
**Why it failed:** DNS resolution failed - the domain could not be resolved from this environment
**Impact:** Could not get official earnings presentations or press releases
**Lesson:** Some domains may be blocked or unreachable from the sandbox environment

## 3. PRNewswire Press Releases (Attempted 2025-06-18)
**What I tried:** Searched PRNewswire for GitLab press releases
**Why it failed:** Search URL returned 404
**Impact:** Could not include press releases in /raw/other/
**Lesson:** PRNewswire may have changed their search API or blocked automated access

## 4. Initial CIK Lookup (Attempted 2025-06-18)
**What I tried:** Used CIK 0001687226 (found in some online sources) for GitLab
**Why it failed:** This CIK mapped to "Harper James P" not GitLab Inc.
**Resolution:** Found correct CIK 0001653482 through SEC full-text search
**Lesson:** Online CIK databases can be outdated or incorrect. Always verify through SEC's own systems.

## 5. Earnings Call Audio (Attempted 2025-06-18)
**What I tried:** Looked for audio recordings of earnings calls
**Why it failed:** No accessible audio sources found. Seeking Alpha has "Play Call" buttons but these require JavaScript execution.
**Impact:** Could not include audio analysis. Relied on text transcripts instead.
**Lesson:** Audio content requires browser automation or paid services.
