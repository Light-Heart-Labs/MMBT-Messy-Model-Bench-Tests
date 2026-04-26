# Research Notes — Session 2: Chart Design and Data Preparation
**Date:** 2026-04-26
**Topic:** Designing charts for the deck, preparing data from input repo

## Chart Design Decisions

### Color Palette
- **Primary:** Teal (#0D9488) for GitLab — signals growth, technology
- **Bear scenario:** Red (#DC2626) — universally understood as downside
- **Base scenario:** Blue (#2563EB) — neutral, professional
- **Bull scenario:** Green (#16A34A) — universally understood as upside
- **Competitors:** Distinct colors, consistent across all slides
- **Background:** White with subtle grid lines — clean, professional

### Typography
- **Headings:** System sans-serif (Inter/Helvetica) — clean, modern
- **Body:** System sans-serif — readable at presentation size
- **Numbers:** Monospace for financial figures — aligns decimal points

### Chart Conventions
- **Revenue chart:** Line chart with confidence bands
- **Margin chart:** Area chart showing improvement trajectory
- **Competitive position:** Scatter plot (growth vs. margin) — not pie chart
- **Risk matrix:** Bubble chart (probability vs. impact)
- **Scenarios:** Distribution visualization (not bullet points)
- **Reasoning trail:** Dependency graph (nodes and edges)

### Why Sequential Colormap for Financial Trajectory
The financial trajectory uses a sequential colormap (light to dark teal) because:
1. The data has a natural zero point (current price $21.51)
2. We're showing improvement over time, not deviation from a mean
3. A diverging colormap would imply a symmetric distribution around zero, which doesn't apply to revenue growth
4. Sequential colormap reinforces the narrative of "getting better"

## Data Preparation

### Revenue Data (from /input/repo/extracted/income_statement_annual.csv)
- FY2022: $424M (actually FY2023 label in CSV)
- FY2023: $580M (actually FY2024 label)
- FY2024: $759M (actually FY2025 label)
- FY2025: $955M (actually FY2026 label)

Note: CSV column headers are dates (2026-01-31, etc.) but the memo uses FY labels.
Need to map: 2022-01-31 → FY2022, 2023-01-31 → FY2023, etc.

### Competitor Data (from /input/repo/extracted/competitor_data.json)
- 10 competitors with market cap, EV/Revenue, growth, margins
- Need to filter to 8 most relevant for scatter plot
- Exclude Doximity (healthcare sector, not comparable)
- Exclude Palo Alto (too large, different sector)

### Historical Prices (from /input/repo/extracted/historical_prices.csv)
- Daily prices from Aug 2025 to Apr 2026
- Current price: $21.51 (last data point)
- 52-week range: $18.73 - $54.08
- 52-week change: -54.2%
