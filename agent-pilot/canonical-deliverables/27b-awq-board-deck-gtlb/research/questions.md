# Questions Log

## 2025-06-18

### Q1: How many slides should the deck have?
- **Issue:** Requirements say 15-25 slides for a 30-minute presentation.
- **Resolution:** Chose 16 slides — enough to cover all required content without padding. Each slide has a clear purpose.
- **Status:** Resolved

### Q2: Should I include management quotes?
- **Issue:** The memo doesn't contain direct management quotes — it contains the agent's analysis.
- **Resolution:** Used the agent's own words from the memo as "quotes" since the agent is the analyst. Documented in /audit/quotes.md with surrounding context.
- **Status:** Resolved

### Q3: How to handle the peer average EV/Revenue discrepancy?
- **Issue:** The memo states 7.03x but recalculating from the JSON data yields ~6.80x.
- **Resolution:** Documented the discrepancy in /audit/reconciliation.md. Used the actual JSON data values in charts. The memo's figure may use a different comp set or rounding.
- **Status:** Resolved (documented)

### Q4: What color to use for the "human would do differently" category?
- **Issue:** Need a color that signals "outside our capability" without being negative.
- **Resolution:** Used gray (#64748B) — neutral, not alarming. Green for confident, orange for estimating, gray for human-different.
- **Status:** Resolved

### Q5: Should the reasoning trail chart show the SEC filing block?
- **Issue:** The SEC filing downloads failed (403). Should this be shown in the reasoning trail?
- **Resolution:** Yes — it's an important part of the reasoning. The agent tried and failed, then used yfinance instead. This shows the actual process, not a sanitized version.
- **Status:** Resolved

### Q6: How to make the scenario distribution look like a real distribution?
- **Issue:** Three discrete scenarios (bear/base/bull) need to be shown as a continuous distribution.
- **Resolution:** Used scipy.stats.norm to create three normal distributions weighted by probability, then summed them. This creates a realistic-looking distribution with the three scenarios as components.
- **Status:** Resolved
