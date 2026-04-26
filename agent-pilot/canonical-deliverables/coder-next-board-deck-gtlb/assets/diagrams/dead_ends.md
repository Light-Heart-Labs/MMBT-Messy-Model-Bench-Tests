# Dead Ends Diagram

**Date:** June 18, 2025  
**Purpose:** Visualize hypotheses investigated and rejected

---

## Diagram Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Research Dead Ends                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRIMARY GOAL                                        │
│              Download SEC filings and earnings call transcripts            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATTEMPT 1: SEC Filing Downloads                          │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
          ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
          │ Direct URL     │ │ Session      │ │ curl with      │
          │ access         │ │ with cookies │ │ proper headers │
          └────────┬───────┘ └──────┬───────┘ └──────┬─────────┘
                     │              │                │
                     └──────────────┼────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │ Result: 403 Forbidden           │
                    │ Impact: No SEC filings          │
                    │ Resolution: Use yfinance        │
                    └─────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATTEMPT 2: GitLab IR Website                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │ DNS resolution failed           │
                    │ Domain: investors.gitlab.com    │
                    │ Impact: No official presentations│
                    │ Resolution: Use Seeking Alpha   │
                    └─────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATTEMPT 3: PRNewswire Search                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │ Search URL returned 404         │
                    │ Impact: No press releases       │
                    │ Resolution: Use yfinance data   │
                    └─────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATTEMPT 4: Initial CIK Lookup                            │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
          ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
          │ CIK from       │ │ SEC full-    │ │ Company info   │
          │ online sources │ │ text search  │ │ verification   │
          │ (0001687226)   │ │ API          │ │ (yfinance)     │
          └────────┬───────┘ └──────┬───────┘ └──────┬─────────┘
                     │              │                │
                     └──────────────┼────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │ Result: Wrong CIK mapped to     │
                    │ "Harper James P" not GitLab     │
                    │ Resolution: Use CIK 0001653482  │
                    └─────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ATTEMPT 5: Earnings Call Audio                           │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │ No accessible audio sources     │
                    │ Seeking Alpha requires JS       │
                    │ Impact: No audio analysis       │
                    │ Resolution: Use text transcripts│
                    └─────────────────────────────────┘

                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FINAL APPROACH                                      │
│              Use yfinance for financial data + transcripts                 │
│              + ADR-style decision records + trace files                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Learnings

1. **SEC actively blocks automated access** - 403 errors for all requests
2. **Some domains may be blocked** - investors.gitlab.com DNS resolution failed
3. **Online databases can be outdated** - CIK 0001687226 was wrong
4. **Audio content requires browser automation** - No accessible audio sources
5. **Secondary sources are reliable** - yfinance sources from SEC filings

---

## Impact on Analysis

| Dead End | Impact | Mitigation |
|----------|--------|------------|
| SEC filings | No original filings | Used yfinance (secondary source) |
| IR website | No official presentations | Used Seeking Alpha transcripts |
| PRNewswire | No press releases | Used yfinance data |
| Wrong CIK | Could not access filings | Found correct CIK via SEC API |
| Audio | No audio analysis | Used text transcripts |

---

## Verification

All dead ends are documented in:
- `/research/dead-ends.md` - Full list of dead ends
- `/research/questions.md` - Questions encountered
- `/audit/traces/dead_ends.md` - Trace file for dead ends
