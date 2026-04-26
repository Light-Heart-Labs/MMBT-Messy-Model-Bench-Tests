# Dead-Ends — Slide Concepts and Visualizations That Didn't Make the Cut

## 1. Pie Chart for Market Share
**Concept:** Show GitLab's market share in the DevOps market as a pie chart.
**Rejected because:** A pie chart would show GitLab as a tiny slice, reinforcing the narrative that GitLab is a niche player. But the thesis is that GitLab is *undervalued* relative to its growth and competitive position. The pie chart obscures the actual thesis (margin compression at scale doesn't apply here — the thesis is about growth at a low multiple).
**Alternative used:** Scatter plot of growth vs. margin (ADR-004).

## 2. Tornado Diagram for DCF Sensitivity
**Concept:** Show how the DCF value changes with each assumption (WACC, terminal growth, revenue growth).
**Rejected because:** A tornado diagram shows sensitivity to individual variables but doesn't show the overall distribution. The board needs to see the probability-weighted outcome, not just which assumptions matter most.
**Alternative used:** Probability distribution histogram (ADR-005).

## 3. Radar Chart for Competitive Position
**Concept:** Show GitLab vs. competitors on multiple dimensions (growth, margin, valuation, TAM, moat).
**Rejected because:** Radar charts are hard to read at presentation size. With 8 competitors and 6 dimensions, the chart becomes a mess of overlapping polygons. The scatter plot (growth vs. margin) is cleaner and more informative.
**Alternative used:** Scatter plot with bubble size for market cap.

## 4. Timeline of Stock Price Events
**Concept:** Show key events (earnings, product launches, analyst upgrades) on a timeline with price.
**Rejected because:** The historical price data doesn't have event annotations. Adding events would require external data sources that weren't available. The timeline would be speculative.
**Alternative used:** Simple price history chart with key levels marked.

## 5. Customer Segmentation Chart
**Concept:** Show GitLab's customer base by segment (SMB, mid-market, enterprise) and growth by segment.
**Rejected because:** This data is not available in the input repo. The earnings call transcripts mention enterprise focus but don't provide segment breakdowns. Creating this chart would require assumptions not supported by the data.
**Alternative used:** SaaS metrics chart (ARR, NRR) which is the closest available proxy for customer quality.

## 6. Monte Carlo Simulation
**Concept:** Run 10,000 Monte Carlo simulations of the DCF to show the full probability distribution.
**Rejected because:** Too complex for a board presentation. The three-scenario distribution (bear/base/bull) is sufficient and more interpretable. A Monte Carlo histogram would look like a smooth curve and obscure the fact that the distribution is based on three discrete scenarios.
**Alternative used:** Three-scenario distribution with histogram.

## 7. EV/Revenue Bar Chart
**Concept:** Show GitLab's EV/Revenue vs. each competitor as a bar chart.
**Rejected because:** A bar chart only shows one dimension (valuation). The scatter plot shows both growth AND margin, which is more informative. The bar chart would also be cluttered with 9 bars.
**Alternative used:** Scatter plot with EV/Revenue labels.

## 8. Waterfall Chart for Revenue Bridge
**Concept:** Show the bridge from FY2023 revenue to FY2026 revenue, with each year's growth as a separate bar.
**Rejected because:** The financial trajectory chart already shows revenue growth as a line chart with annotations. A waterfall would be redundant and less visually clear.
**Alternative used:** Line chart with inflection point annotations.

## 9. Heat Map for Risk
**Concept:** Show a heat map of risks across dimensions (probability, impact, likelihood of mitigation).
**Rejected because:** The risk matrix (bubble chart) already shows probability vs. impact. Adding a third dimension (mitigation likelihood) would make the chart too complex. The risk details are better presented as text.
**Alternative used:** Bubble chart with text details in sidebar.

## 10. Animated Slide Transitions
**Concept:** Use PowerPoint animations to reveal each part of the reasoning trail step by step.
**Rejected because:** Animations don't translate well to PDF export. The board may view the PDF without animations. Static charts are more reliable and reproducible.
**Alternative used:** Static charts with clear visual hierarchy.
