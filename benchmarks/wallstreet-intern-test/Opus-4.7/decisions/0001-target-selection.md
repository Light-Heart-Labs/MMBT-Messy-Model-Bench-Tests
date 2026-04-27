# ADR-0001: Target Selection — The Vita Coco Company (NASDAQ: COCO)

- Status: Accepted
- Date: 2026-04-27

## Context

The brief requires picking a publicly traded US company with market cap $1B–$10B and producing a complete investment memo. The choice itself is the first major decision and should be defensible.

I want a target that satisfies several constraints simultaneously:

1. **Market cap inside the band.** Latest closing price × outstanding shares must put the company between $1B and $10B.
2. **Filing history.** A recent 10-K, ≥4 trailing 10-Qs, and at least four reported earnings calls. Companies that IPO'd in the last 12 months have too short a track record.
3. **Single-product / pure-play.** A company with one core business is dramatically easier to model in the time available than a multi-segment conglomerate. The model can focus on revenue drivers and unit economics rather than segment allocations.
4. **Genuine debate.** The bull/bear thesis should not be obvious. If sell-side consensus and buy-side consensus already agree, there is no edge to find.
5. **Disclosure quality.** Volume + ASP, segment, geography, and customer concentration disclosure makes a model much more grounded.

## Candidates considered

| Ticker | Company | Mkt cap est. | Why considered | Why rejected |
|--------|---------|--------------|----------------|--------------|
| OLO | Olo Inc. | ~$1.3B | Restaurant SaaS, Wingstop departure noise | Take-private rumored repeatedly; thesis becomes "is this an LBO target" rather than fundamentals. |
| BASE | Couchbase | ~$1.0B | Database, Capella mix shift story | Already announced going-private deal in 2025; price is essentially fixed. |
| CHEF | Chefs' Warehouse | ~$1.7B | Specialty food distributor to high-end restaurants | Macro-cyclical, hard to disentangle interest expense math without rate forecast. |
| SWIM | Latham Group | ~$1.0B | Pool manufacturer, post-COVID normalization | Heavy housing-cycle bet; thesis = housing turn. |
| SSTI | SoundThinking | ~$0.4B | Gunshot detection, Chicago contract loss | Below market cap floor. |
| HIMS | Hims & Hers | ~$15B+ | Telehealth, GLP-1 story | Above market cap ceiling. |
| **COCO** | **The Vita Coco Company** | **~$2.0B** | **Pure-play category leader; recent inflation/cost normalization debate; dual-channel (own brand + private label)** | **Selected.** |

## Decision

Target: **The Vita Coco Company (NASDAQ: COCO)**.

Rationale:

- **Pure-play.** Coconut water (and adjacent better-for-you beverages) is essentially the only thing the company does. Two reportable segments (Vita Coco Coconut Water and Other) let the model stay tractable.
- **Market position.** Vita Coco is the U.S. coconut water category leader by a wide margin and is also the largest co-packer/private-label supplier in the category — an unusual structural position worth probing.
- **Live debate.** The stock had a strong run after ocean freight rates and coconut input costs both collapsed through 2023–24. The question for 2026 is whether the gross margin level achieved in those years is structural or cyclical. This is a real question with no obvious answer.
- **Filing depth.** Public since October 2021 (IPO at $15 / share). Five fiscal years of post-IPO 10-Ks should be available (FY21–FY25), plus 10-Qs and proxy filings — enough history for cohort/margin analysis.
- **Disclosure.** 10-K historically discloses revenue split between branded and private label, geographic split, and key cost-of-goods drivers (concentrate, packaging, shipping). This is exactly what is needed to build a defensible model.
- **Variant view potential.** There is at least one obvious place to look for a non-consensus view: the share of recent gross margin expansion that came from one-time freight and procurement timing vs. structural mix and pricing. Sell-side often anchors on "current GM rate" as the base case; if a meaningful portion is non-recurring, the right base case is materially lower.

## Alternatives explicitly considered and rejected late

- **Cal-Maine Foods (CALM).** Real, but the stock IS the avian flu cycle. Thesis would collapse to a forecast of egg prices, which is genuinely outside what can be done responsibly in this format.
- **Stagwell (STGW).** Marketing services holding company, real disclosure, cap fits — but heavy customer concentration and a related-party CEO ownership stake make governance the dominant narrative.

## Consequences

- I have to be honest about the freight/cost-tailwind question. If the answer is "structural," I will likely be more bullish than current consensus; if "cyclical," more bearish. Either way it has to be backed by what is in the filings, not by hand-waving.
- I will need to handle two related-but-distinct revenue streams (own brand vs. private label) in the model. This adds modeling work but is also the most likely place a variant view sits.
- Coconut commodity and shipping cost data are partial-public. I will have to lean on what management discloses on calls; I may not be able to fully triangulate from independent sources.
