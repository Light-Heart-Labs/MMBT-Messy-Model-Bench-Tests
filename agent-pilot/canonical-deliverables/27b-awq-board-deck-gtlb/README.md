# GitLab (GTLB) Board Presentation — Audit Trail Repository

**Recommendation: BUY** | **Price Target: $42.00** | **Upside: 95%**

This repository contains a complete, auditable board presentation for GitLab Inc. (NYSE: GTLB), including the reasoning trail, audit files, and reproducible chart scripts.

## Quick Start (10 minutes)

1. **Read the presentation:** Open `deck/gitlab_board_presentation.pptx` (16 slides)
2. **Understand the narrative:** Read `narrative/storyboard.md` for the full arc
3. **Verify a claim:** Pick any number → check `audit/numbers.md` → follow the trace → land on source data
4. **Reproduce a chart:** Run any script in `assets/charts/` to regenerate the exact chart

## Repository Structure

```
/workspace/
├── README.md                    # This file
├── sources.md                   # External sources with URLs and versions
├── tool-log.md                  # Every tool call with justification
├── deck/
│   ├── gitlab_board_presentation.pptx   # Final 16-slide presentation
│   └── source/
│       └── build_presentation.py        # Script that built the PPTX
├── assets/
│   ├── charts/                # Every chart as standalone PNG + generation script
│   │   ├── 01_revenue_margins.png + .py
│   │   ├── 02_arr_nrr.png + .py
│   │   ├── 03_competitive_position.png + .py
│   │   ├── 04_scenario_distribution.png + .py
│   │   ├── 05_risk_heatmap.png + .py
│   │   ├── 06_reasoning_trail.png + .py
│   │   └── 07_confidence_spectrum.png + .py
│   ├── diagrams/              # Process diagrams (empty — reasoning trail is in charts/)
│   ├── images/                # Photography/icons (empty — no decorative imagery used)
│   └── tables/                # Source data for every table, as CSV
│       ├── financial_summary.csv
│       ├── revenue_and_margins.csv
│       ├── competitor_data.csv
│       └── comp_set.csv
├── audit/
│   ├── traces/                # For every claim, a trace file pointing to /input/repo/
│   │   ├── trace_01_current_price.md
│   │   ├── trace_02_revenue_fy2026.md
│   │   ├── trace_03_arr_fy2026.md
│   │   ├── trace_04_price_target.md
│   │   └── trace_05_nrr.md
│   ├── numbers.md             # Every number in the deck with source path
│   ├── quotes.md              # Every quote with file + line + surrounding context
│   └── reconciliation.md      # 5 random numbers fully reconciled
├── narrative/
│   ├── storyboard.md          # Full narrative arc (committed BEFORE any slides)
│   ├── alternatives.md        # Other narrative structures considered and rejected
│   └── audience-analysis.md   # Board profile and how the deck addresses each concern
├── research/
│   ├── notes/                 # Working notes, dated, one file per session
│   │   ├── 2025-06-18-repo-setup.md
│   │   ├── 2025-06-18-charts.md
│   │   ├── 2025-06-18-audit.md
│   │   └── 2025-06-18-deck.md
│   ├── questions.md           # Questions about the input repo and resolutions
│   └── dead-ends.md           # Slide concepts that didn't make the cut, with why
└── decisions/                 # ADR-style records for every non-obvious choice
    ├── 004-color-palette.md   # Why this color palette
    └── 005-chart-conventions.md  # Why these chart types
```

## How to Verify Any Claim

1. **Pick a number** from any slide (e.g., "Revenue FY2026 = $955M")
2. **Find the trace** in `audit/numbers.md` or `audit/traces/`
3. **Follow to source** — the trace points to a specific file in `/input/repo/`
4. **Verify** — open the source file and confirm the number

Example:
```bash
# Pick: Revenue FY2026 = $955M
cat audit/traces/trace_02_revenue_fy2026.md
# → Points to /input/repo/extracted/income_statement_annual.csv
# → Row "Total Revenue", column "2026-01-31" = 955224000.0
# → $955.2M → $955M ✓
```

## How to Reproduce Any Chart

```bash
# Regenerate any chart from source data
python3 assets/charts/01_revenue_margins.py
python3 assets/charts/02_arr_nrr.py
python3 assets/charts/03_competitive_position.py
python3 assets/charts/04_scenario_distribution.py
python3 assets/charts/05_risk_heatmap.py
python3 assets/charts/06_reasoning_trail.py
python3 assets/charts/07_confidence_spectrum.py
```

## How to Regenerate the Deck

```bash
# Regenerate the full presentation
python3 deck/source/build_presentation.py
# Output: deck/gitlab_board_presentation.pptx
```

## Reading Order

1. `narrative/storyboard.md` — Understand the narrative arc
2. `deck/gitlab_board_presentation.pptx` — The presentation itself
3. `audit/numbers.md` — Verify the numbers
4. `audit/reconciliation.md` — See how spot-checks work
5. `decisions/` — Understand the methodology choices
6. `research/dead-ends.md` — See what didn't make the cut

## Technical Requirements

- Python 3.x with: `matplotlib`, `numpy`, `pandas`, `scipy`, `python-pptx`
- Any PowerPoint viewer for the PPTX file
- Image viewer for chart PNGs

## Disclaimer

This presentation is for informational and educational purposes only. It does not constitute investment advice. All valuations are based on assumptions that may not materialize. Past performance does not guarantee future results.
