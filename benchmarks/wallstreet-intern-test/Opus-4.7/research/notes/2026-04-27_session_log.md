# Working notes — 2026-04-27 research session

## Goal
Build an investment memo on a public US company with $1B-$10B market cap. Pick a target where the bull/bear debate is real and identify something the sell-side may be missing.

## Time spent on key decisions

- **Target selection (~10 min).** Considered six candidates. Ruled out OLO (LBO noise), BASE (announced take-private), CHEF (rate-cycle bet), SWIM (housing-cycle bet), SSTI (sub-$1B). Vita Coco selected for clean disclosure + live debate on margin durability.
- **Filing pull (~15 min).** Set up EDGAR fetcher with proper User-Agent. Pulled 5 FY 10-Ks, 3 latest 10-Qs, 9 earnings press releases, latest DEF 14A, XBRL companyfacts JSON.
- **Transcripts (~10 min).** 5 most recent earnings calls. Motley Fool was primary source; Insider Monkey for Q1-2025 and Q4-FY2024 (Fool didn't have those). Wrote a small extractor that pulls `<p>` blocks from streaming-rendered HTML.
- **Extraction & model (~25 min).** Annual P&L/BS/CF from XBRL. Segment x brand from press release tables. Three-statement model with single-cell scenario toggle and three cross-checks for valuation.
- **Variant view (~15 min).** Pulled peer multiples (CELH/BRBR/SMPL). Walked back from sell-side consensus target to implied exit multiple. Realized consensus implicitly assumes COCO's 22x forward multiple holds through FY27, then wrote up why I think that's the soft assumption.
- **Memo + PDF (~20 min).** Wrote markdown memo. Built a small reportlab-based MD-to-PDF renderer because pandoc isn't installed.

## Key data points anchored in extraction

- FY2025 net sales: **$609.8M** [extracted/annual.csv]
- FY2025 GM: **36.5%** consolidated, 36.8% Americas, 34.9% International [press release table_06]
- FY2026 guidance: $680-700M net sales, ~38% GM, $122-128M Adj EBITDA [Q4 call line 34]
- Customer A: 30% → 25% → 19% over FY23-25 [10-K Note 12]
- Tariffs paid 2025: $16M ($14M expensed, $2M in inventory) [Q4 call line 29]
- Walmart shelf reset adds ~6% to brand scans [Q4 call line 22]
- International growth FY25: +37% segment, +43% on the branded line [press release table_05]

## Insights that shaped the recommendation

1. **The recent stock run was largely multiple expansion.** EBITDA forecast moved up ~25% over 12 months while the multiple moved from ~22x to ~33x trailing. The fundamentals story has been re-rated harder than re-modeled.
2. **CELH is the cleanest historical analog for COCO.** Both are pure-play growth beverages. CELH peaked above 50x EV/EBITDA in 2024 and compressed to 16x by 2026 as growth normalized. COCO is on a similar growth-deceleration path; it's hard to argue the multiple should not similarly compress.
3. **FY26 guidance is achievable but doesn't justify the multiple.** Even hitting management's guide produces $125M EBITDA — at current EV that's 22x forward. Bullish for the stock only if the multiple holds; modestly bearish if it normalizes.
4. **International is the only structural upside lever I see.** The Bull case really is "International compounds at 35%+ for three more years AND multiple holds." Plausible but not a base case.

## Open methodological concerns

- The 17x Base exit multiple is defensible but not bulletproof. A reasonable analyst could land at 15x (more bearish) or 19x (more bullish). The variant view holds across that range — the 22x-implied-by-consensus is the outlier.
- The probability weights (25/50/25) are subjective. The downside case requires multiple conditions simultaneously; the upside case requires a single condition (International acceleration sustained).
- I did not separately model the M&A optionality. Vita Coco has $200M cash and management has said M&A is a possibility. A poorly-priced acquisition could erode value; a well-priced one could expand the platform.
- Today is 2026-04-27. Q1 2026 results are imminent (per management Q4 call: "we look forward to talking to everybody when we announce our Q1 results in late April"). This memo could become stale within days. Reader should re-validate the key numeric anchors against the Q1 release before acting.
