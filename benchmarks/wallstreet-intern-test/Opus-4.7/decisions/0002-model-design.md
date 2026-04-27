# ADR-0002: Model design — drivers, granularity, scenario structure

- Status: Accepted
- Date: 2026-04-27

## Context

I need to build a three-statement model that ties the memo's recommendation and price target back to an auditable spreadsheet. The model needs to be:

1. **Granular enough to express the variant view.** The thesis lives in segment x brand mix, so the model has to model that grain explicitly.
2. **Linked.** Every cell in the IS/BS/CF should derive from drivers + history, not be hand-typed.
3. **Scenario-able.** Bear / Base / Bull need to switch off a single named cell so we don't maintain three parallel sheets.
4. **Tractable.** A dozen sheets of nested macros is overkill for a $3B-cap company with two segments.

## Decision

**Granularity: segment x brand.** Six revenue lines:

- Americas — Vita Coco Coconut Water
- Americas — Private Label
- Americas — Other (Treats coconut milk + ancillary)
- International — Vita Coco Coconut Water
- International — Private Label
- International — Other

Each line is driven by **prior-period revenue × growth %**. Growth % is the scenario driver. Volume vs. price is *not* a separate dimension in the model — management discloses it in the press releases but the public split is too noisy to use as a forecasting input. We model revenue directly and reference volume CAGR as a sanity check in the assumptions tab.

**Gross margin: by segment.** Two GP margins (Americas, International) applied to segment subtotals. The cost stack — coconut concentrate + packaging + ocean freight + tariffs + co-packing + domestic logistics — collapses into a single GM% per segment because: (a) the 10-K does not break out the underlying components, (b) management commentary is more informative than would-be modelled stack-ups, and (c) the differential between Americas and International GM is the modeling lever that matters most.

**Operating expenses: SG&A as % of net sales** with a separate "marketing intensity" toggle so we can capture management's stated plan to invest into category growth without bloating the line.

**Below-the-line:** flat $0 net interest (historical interest income roughly offsets minimal interest expense; $197M cash earning ~5% partially offset by $0 debt). Other income/expense forecasted at zero for simplicity (FX swings around it but we don't have visibility to forecast direction). Effective tax rate: 23% per FY2025 actual.

**Shares outstanding:** held flat at 60M diluted (FY25 weighted avg = 59.97M). Repurchases roughly offset SBC dilution; this is a reasonable simplification given the small magnitudes.

**Forecast horizon: FY2026, FY2027, FY2028.** Beyond three years, terminal-value sensitivity dominates, and we'll handle that in valuation, not in the linked model.

**Scenarios: a single named cell `Scenario` in {1, 2, 3}** drives a CHOOSE() across all the growth and margin inputs. Bear / Base / Bull are explicit columns on the assumptions tab; the live values flow through CHOOSE().

**Three-statement linking:** the model is "fully linked" in the limited sense that NI flows to retained earnings on the BS, and net change in cash from the CF reconciles BS cash. We are NOT modeling working capital line-by-line at the granularity Bloomberg analysts would (e.g., DSO/DPO/DIO drivers); instead, working capital is held to its 2025 ratios on the BS and we only flex the inventory line because that's the most material moving piece for an inventory-heavy business.

## Alternatives considered

- **Volume-driven model.** Tempting because the press releases give us CE volumes by segment. Rejected because (a) ASP requires assumptions about price take rate, mix, and promo intensity that are individually noisy, (b) revenue is what matters for the model and for valuation, and (c) the three published quarters of 2025 already give us a tight read on the volume vs. price split — we don't need to forecast it explicitly.
- **Detailed COGS stack.** Tempting for the variant view ("freight is X% of COGS, here's our freight forecast..."). Rejected because Vita Coco doesn't disclose COGS components in its filings — we'd be making up the stack from sell-side notes we don't have access to. Better to express the variant view as a GM% range and explain why.
- **One-pass DCF.** Standard, but Vita Coco's 10-year terminal value would be 80%+ of EV given their growth runway, and "what's the right WACC for a single-product brand with limited debt history" is a fragile anchor. We will use both DCF and exit-multiple comparable approaches and triangulate.
- **Bottom-up SG&A modeling.** People + facilities + marketing + R&D as separate lines. Vita Coco discloses this in aggregate only — top-down works.

## Consequences

- The model can be defended in 5 minutes because every forecast cell points at a Scenario CHOOSE() formula. There's nothing hard-coded that isn't traceable to a driver.
- The structural-vs-cyclical margin question is captured by the spread between Bear (35.5% Americas) and Bull (39.0% Americas) GM assumption — a live debate, not a buried number.
- We may understate growth volatility because we're modeling segment-brand revenue at the annual level rather than quarter-by-quarter. That's accepted: investment thesis works at FY grain.
