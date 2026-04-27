# Variant view: multiple compression is mispriced

## What sell-side appears to be missing

**Sell-side consensus 12m target: $57.75 (avg of 8 analysts).**
At spot $52.39, the consensus implies +10% upside.

Decomposing the consensus target:

- Consensus FY26 EPS: $1.58 → at $58 target = 36.7x P/E on forward earnings
- Consensus FY27 EPS: $1.85 → at $58 target = 31.4x P/E on FY27 (12 months out)
- Working backward to EBITDA: $58 × 60M shares = $3.48B equity − $200M cash ≈ $3.28B EV; FY27E EBITDA in the $140-150M area implies an exit multiple of **22-23x EV/EBITDA on FY27 numbers**.

That's almost exactly the multiple at which COCO trades today.

**The implicit assumption: COCO will trade at the same EV/EBITDA multiple in 18 months that it does now.**

That's the assumption I think is wrong.

## Why multiple compression is the more likely path

### 1. Growth is decelerating from current pace

| | FY24 | FY25 | FY26E (mgmt) | FY27 cons. | FY28E (model) |
|---|---|---|---|---|---|
| Net sales | $516M | $610M | $690M (mid) | $789M | $871M (Base) |
| Growth | +4.5% | +18.2% | +13.1% | +11.4% | +10.7% |

By FY28, COCO is a low-double-digit grower. That's a different multiple regime than +18-20%.

### 2. Peer evidence on what happens to the multiple when growth decelerates

Snapshot 2026-04-27 (analysis/peer_comps.md):

| Ticker | Profile | EV/EBITDA TTM |
|---|---|---|
| **COCO** | Pure-play, +18% TTM growth, decelerating | **33.4x** |
| CELH | Was high-growth, now decelerating | 16.1x |
| BRBR | Mature single-product | 9.2x |
| SMPL | Mature low-growth | 6.6x |

Celsius (CELH) is the cleanest analog. CELH was growing 100%+ in 2023; it carried multiples north of 50x. As growth normalized to 25%, the multiple compressed to 16x — a **>60% compression** in <18 months despite continuing positive growth.

If COCO follows the same path — current 33x TTM (22x forward) compressing toward 16-18x as the growth profile becomes more visible — then a $46-48 price by April 2027 is the more likely outcome than the consensus $58.

### 3. The category-leader premium has limits

Bulls argue COCO deserves a permanent premium because:
- Category leadership (~50% US share)
- 30%+ international growth
- Asset-light model

These are real but each has a counter:

- **Category leadership** matters less when private label is taking share. Customer A (likely Costco) has been reducing Vita Coco's regional supply over multiple years (30% → 25% → 19% of sales). That's the largest single account walking down. Read 10-K p. ~233 / `extracted/mda_FY2025_10K.txt:53-54`.

- **International growth** off a $101M FY25 base is great, but it would need to compound at 30%+ for many years to materially change the consolidated picture. Even at +30% CAGR, International only reaches ~$220M by FY28 — still <25% of total. The Americas business is what drives the multiple.

- **Asset-light model** helps cash conversion (FCF/EBITDA ≈ 50% historically) but doesn't get a premium on EBITDA — it gets the premium on cash flow, which the FCF/share analysis already captures.

### 4. Why I don't think this is "priced in"

If 8 sell-side analysts already had this view, the consensus target wouldn't be $58. The pattern of ratings (3 Strong Buy, 4 Buy, 2 Hold, 0 Sell) and the tight target range ($54-$60) suggest a remarkably uniform bullish view that has not yet contemplated multiple normalization.

The recent stock action also fits the "sell-side anchored on current multiple" hypothesis. COCO ran from ~$30 in mid-2024 to $52 today — a ~75% rally — driven by:
1. Tariff relief (real)
2. Walmart shelf reset (real, ~6% top-line lift)
3. International acceleration (real)
4. **Multiple expansion** (the largest contributor)

The first three should sustain. The fourth is the fragile leg.

## Quantifying the variant view

If FY27 exit multiple is:
- **22x** (consensus implied): equity value $3.6B → $58/share end FY27 → **$58 12m target** (+10%)
- **17x** (Base, my view): equity value $2.9B → $48/share → **$45-46 12m target** (-13%)
- **13x** (Bear, "BRBR-style mature"): equity value $2.3B → $38/share → **$35 12m target** (-33%)

I assign probabilities:
- 25% Bull (22x holds, growth re-accelerates) → $58
- 50% Base (17x exit) → $46
- 25% Bear (13x compression to mature beverage) → $23 (model output uses 12x)

**Probability-weighted target ≈ $43.** That's −18% vs spot.

## The mispricing claim

If consensus is right (multiple holds), COCO returns ~+10% over 12 months.
If consensus is wrong about the multiple (the variant view), COCO returns ~−15% over 12 months.

Sell-side ratings imply they think the consensus is highly likely. Our analysis suggests it's more like 50/50, which means the asymmetry tilts negative.

This isn't a "the company will miss numbers" thesis. The company will probably hit FY26 guide. The variant view is purely about valuation: **a beverage company decelerating from +18% to +11% growth should not trade at the same multiple at the end of the deceleration as at the start of it.** Sell-side is letting that re-rating happen quietly through earnings growth ("the stock won't fall, EBITDA will catch up to the multiple") but more likely the multiple compresses faster than EBITDA compounds.
