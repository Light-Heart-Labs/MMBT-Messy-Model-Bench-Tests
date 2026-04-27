# Dead Ends

Lines of investigation that did not pan out, and why.
Reasoning that did not make it into the memo lives here.

## Volume × ASP modeling

**What I tried:** Using the disclosed CE (case equivalent) volumes from press release Table 7 to model revenue as Volume × ASP, separately by segment and brand.

**Why it didn't work:** ASP per CE varies by 30%+ across years, mostly due to mix shifts (multipack vs. single-serve, Treats coconut milk vs. coconut water, container size, geography). When I tried to back-cast, the implied ASP movements didn't reconcile with management's stated price increases on calls. The "real" pricing dynamic is buried inside trade promotion spend, channel mix, and SKU mix — none of which is disclosed.

**What I did instead:** Forecast revenue directly as a YoY % growth rate per segment-brand. Volume CE numbers stay in the History tab as a sanity check.

**What it would take to do this properly:** Sell-side scanner data (Circana, Nielsen) at the SKU level. Or company-issued bridge of "pricing actions" to "realized net pricing" at quarterly grain. Neither is publicly available.

## Coconut commodity cost stack-up

**What I tried:** Build a COGS stack from disclosed input costs: green coconut, packaging (Tetra Pak), ocean freight, US duties, co-packing fees, domestic logistics. The idea was to forecast each component separately and roll up to a defendable GM% by year.

**Why it didn't work:** Vita Coco discloses none of these line items. The 10-K says COGS includes "products sold... inbound and outbound shipping... freight and duties... shipping and packaging supplies... and warehouse fulfillment costs" but no $ allocation. I'd be making up the entire stack from public commodity index data (which doesn't directly correspond to Vita Coco's actual costs because they have multi-source procurement and contract pricing).

**What I did instead:** A single GM% per segment, with the structural-vs-cyclical question expressed in the Bear/Bull spread (35.5% vs 40.0% Americas GM). The variant-view discussion handles the GM debate qualitatively.

## Counter-thesis: International is undervalued

**What I tried:** Argue that International growing at 35-40% off a $101M base is being underpriced by sell-side. If International compounds at 35% for 5 years, it reaches $450M by 2030 — at International EBITDA margins similar to consolidated (~16%), that's $72M of EBITDA from one segment. At a 20x growth multiple, that's $1.4B of value — close to half the current EV from one segment alone.

**Why it didn't pan out as a *primary* thesis:** Two reasons.

First, International is not yet at scale where peer multiples are cleanly applied. EBITDA margins in International are not yet disclosed at consolidated levels — the segment Gross margin is now slightly higher than Americas, but International likely runs at lower SG&A leverage given its smaller scale.

Second, the sell-side knows about International. The growth rate has been front-page on every earnings call and press release. It's being priced. The 22x consolidated multiple already reflects International optionality. Pushing this thesis hard would require believing International growth is durable beyond 5 years AND will translate to consolidated margin expansion AND the multiple holds — three independent bets stacked.

**What I did instead:** Acknowledged International as the upside lever in the Bull case. Bull-case Intl-VC growth of 40% in FY26 → 35% in FY27 → 30% in FY28 captures it. Did not build a separate "International-only valuation" because the segment isn't separately monetizable.

## DCF as the primary valuation

**What I tried:** A 10-year DCF with an explicit terminal-value calculation, intended to anchor the price target.

**Why it didn't work:** Vita Coco's 10-year terminal value would constitute >70% of the EV given growth runway and capital-light model. WACC sensitivity (8% vs 9% vs 10%) moves the answer by ~25%. Terminal growth rate sensitivity (2% vs 3%) moves it by ~15%. The model ends up being mostly an expression of the WACC and terminal-growth assumptions — not the operating thesis. A consumer-brand DCF with 70% terminal-value is mostly an opinion about the discount rate.

**What I did instead:** Used DCF as a cross-check, not the primary valuation. Primary anchor is exit-EV/EBITDA, where the multiple discussion is grounded in actual peer trading levels — making the assumption auditable. The DCF cross-check sits in the Valuation tab rows 30-40 of the model.

## Searching for a hidden negative catalyst in the proxy

**What I tried:** Read the latest DEF 14A for executive comp surprises, board changes, or related-party transactions that might suggest distress.

**Why it didn't pan out:** The FY2025 proxy is largely standard. Compensation is reasonable for a $3B-cap consumer brand. Board composition is stable. Verlinvest (early backer) monetized fully in Q1 2025; no governance drama. There isn't a hidden negative here. (This is reassuring rather than a dead end — confirmed governance is clean.)
