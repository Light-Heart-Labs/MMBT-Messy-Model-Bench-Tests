# ADR-0003: Recommendation and price target

- Status: Accepted
- Date: 2026-04-27

## Context

The model and competitive analysis are complete. We need to convert them into a recommendation and a 12-month price target.

Inputs:
- Model output: Bear $23, Base $46, Bull $76 (12-month price target)
- Spot price: $52.39 (2026-04-27)
- Sell-side consensus target: $57.75 (8 analysts; 0 sell ratings)
- Variant view (analysis/variant_view.md): consensus assumes flat multiple; we expect compression as growth decelerates.

## Decision

**Rating: HOLD with a bearish lean.**
**12-month price target: $46.**
**Conviction: Moderate.** Asymmetric risk/reward leans negative but not enough to justify SELL.

### Probability weights

| Scenario | Probability | Target | Implied return |
|---|---|---|---|
| Bear  | 25% | $23 | -56% |
| Base  | 50% | $46 | -12% |
| Bull  | 25% | $76 | +45% |
| **Probability-weighted** | | **$48** | **-9%** |

Probability rationale:
- 25% Bear because the bear thesis requires *both* multiple compression AND growth deceleration AND PL business loss AND tariff return. Each piece is plausible alone (~40% individual prob) but the joint requires all four. 25% feels right.
- 50% Base because the multiple-compression thesis is the most defensible single thread. Even if growth holds, multiple compression alone gets us to Base.
- 25% Bull because the bull case requires International to compound at 35%+ AND the multiple to hold at 22x AND no tariff or competitive setbacks. Possible but requires several things to go right.

### Why not SELL

A SELL would require:
- Probability-weighted return below ~-15%
- High conviction in the Bear case (>40%)
- Limited optionality on Bull

We're at -9% expected with strong bull optionality (45% upside if right). The downside is real but the upside isn't dead. HOLD is the honest recommendation.

### Why not BUY

A BUY would require:
- Probability-weighted return positive
- Margin of safety
- Variant view supporting consensus

Our variant view runs *opposite* to consensus. The expected return is negative. BUY is intellectually inconsistent with the analysis.

### What would change the rating

- **To BUY**: stock pulls back to $40-42 (Base scenario starts producing positive expected return), or evidence emerges that International growth is +40% sustainable rather than tapering.
- **To SELL**: stock rallies above $60 (Bull case mostly priced in, asymmetry turns sharply negative), or Q1 2026 earnings (late April / early May) reveal Walmart reset benefit fading or PL recovery slipping.

## Alternatives considered

- **SELL with $35 target** (variant view priced fully). Rejected because the variant view, while defensible, isn't rock-solid. The multiple could re-rate higher first if International momentum surprises. SELL needs higher conviction than I have.
- **BUY with $58 target** (consensus). Rejected because it would require ignoring the analysis above. The variant view is the entire point of the work.
- **HOLD with $50 target** (closer to consensus). Defensible — basically says "I don't have a strong view either way." But this analysis does support a slight downward bias. $46 reflects that bias honestly.

## Consequences

- The memo will lead with HOLD and a $46 target. The price-action triggers (BUY < $42, SELL > $60) will be explicit.
- Reading public-side coverage of this name should not change the recommendation; the analysis is anchored to fundamentals and multiple, not to news flow.
- If the next 1-2 quarters validate the multiple-compression path (i.e., the stock stops grinding higher despite numbers), the conviction can grow toward SELL. If International acceleration intensifies materially, the conviction grows toward BUY.
