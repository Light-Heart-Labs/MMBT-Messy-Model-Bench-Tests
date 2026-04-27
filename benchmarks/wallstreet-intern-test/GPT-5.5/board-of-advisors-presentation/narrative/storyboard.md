# Storyboard

## Thesis

The agent recommended `HOLD` on YETI with a $41 target because the company is high quality, but public consensus already credits the obvious upside and the market is appropriately discounting tariff, US category, and execution risk.

## Arc

Recommendation -> evidence base -> model and scenario distribution -> competitive/mispricing test -> reasoning graph -> dead ends -> self-audit mechanism -> confidence limits.

## Audience Shift

The board should leave less focused on whether $41 is "right" and more able to judge whether the agent produced an auditable, appropriately skeptical reasoning trail.

## Slide List

1. **Cover: HOLD Is The Point, Not The Dodge**  
   Open with the recommendation and the meta-claim: the agent's restraint is the capability demonstration.

2. **Recommendation Snapshot**  
   Show current price, target, upside, confidence band, and model status.

3. **The Agent's Thesis In One Slide**  
   Three-part thesis: quality brand, fair price, no forced mispricing claim.

4. **What Would Change The Recommendation**  
   Three gates: tariff relief, US Drinkware recovery, international growth beyond consensus.

5. **Evidence Stack**  
   Visualize the input repo evidence corpus: raw filings, transcripts, press releases, market pages, extraction, model, memo.

6. **Financial Trajectory**  
   Revenue, free cash flow, and operating margin history/forecast with FY2025 tariff/mix compression and FY2026 guide-derived recovery called out.

7. **Business Mix Matters**  
   DTC, wholesale, and international mix from 10-K sales-breakdown extraction.

8. **Valuation Bridge**  
   DCF, EV/EBITDA, and P/E cross-checks blending to $41.

9. **Scenario Distribution**  
   Bear/base/bull values as a probability-weighted distribution, including current price and target.

10. **Competitive Position**  
   Peer EV/EBITDA and margin context, plus why `GOLF`, `MAT`, and `NWL` were used.

11. **Efficient Pricing, Not A Manufactured Edge**  
   Compare consensus target/revenue/EPS against the guide-derived base case and explain why no sell-side miss was claimed.

12. **Risk Register**  
   Prioritized risk heat map: tariffs, US Drinkware/wholesale inventory, consumer cyclicality, valuation assumptions.

13. **Reasoning Trail Graph**  
   Dependency graph from raw inputs -> extraction scripts -> ADRs/questions/dead ends -> model checks -> memo recommendation.

14. **Commit History As Reasoning Evidence**  
   Timeline of commits that show how the analysis hardened, including the cash-tag and other-assets corrections.

15. **Dead Ends The Agent Did Not Hide**  
   Investor-day deck, Solo Brands comp, and sell-side blind-spot thesis.

16. **Traceability System**  
   Explain trace IDs, memo trace table, audit files, source hashes, and how to get from slide claim to input repo source.

17. **Self-Auditing Slide**  
   Board member workflow: pick a claim -> open trace -> inspect input file/line -> model cell -> raw source path.

18. **Five-Number Reconciliation**  
   Show the five random spot checks and their full source chains.

19. **Confidence Map**  
   Visual matrix: high confidence in historicals/source capture; medium in guidance/model mechanics; lower in WACC/multiples and channel checks.

20. **Limitations And Next Analyst Work**  
   End with visual limits: paid sell-side detail, channel checks, retailer sell-through, tariff bill-of-materials sensitivity.

## Progression System

Each slide has a quiet trace footer and a top-left section marker:

- `CALL` for recommendation and thesis.
- `EVIDENCE` for source and financial slides.
- `UNCERTAINTY` for scenarios and risks.
- `REASONING` for graph, commits, dead ends, and audit mechanics.
- `LIMITS` for confidence and next work.

## Text Economy

The deck is for live discussion. Use sparse assertions, direct labels, charts, and diagrams. Keep detailed provenance in `/audit/`, not on slides.
