# GitLab (GTLB) — Board of Advisors Presentation

## Quick Start

```bash
# Clone this repo
git clone /workspace/

# Read the deck
open deck/gitlab_board_presentation.pptx   # PowerPoint
open deck/gitlab_board_presentation.pdf    # PDF

# Verify any claim
cat audit/traces/slide4_revenue.md         # Trace for "Revenue: $955M"
cat audit/numbers.md                       # All numbers with sources
cat audit/quotes.md                        # All quotes with context
cat audit/reconciliation.md                # 5 spot-checked numbers
```

## How to Navigate This Repo

### In Order of Reading (10 minutes)

1. **README.md** (this file) — You are here
2. **deck/gitlab_board_presentation.pdf** — The deck (15 slides, 30 min presentation)
3. **audit/reconciliation.md** — Proof that the audit mechanism works
4. **narrative/storyboard.md** — The narrative arc before any slides were built

### For Deep Dives

5. **audit/traces/** — Every claim traces to a specific file in /input/repo/
6. **audit/numbers.md** — Every number in the deck with its source path
7. **audit/quotes.md** — Every quote with surrounding paragraph context
8. **assets/charts/** — Every chart with the script that generated it
9. **decisions/** — ADR-style records for every non-obvious choice
10. **research/notes/** — Dated working notes, one per session
11. **research/dead-ends-deck.md** — Slide concepts that didn't make the cut
12. **narrative/audience-analysis.md** — Who's on the board, what they care about
13. **narrative/alternatives.md** — Other narrative structures considered and rejected
14. **tool-log.md** — Every tool call in order with justification
15. **sources.md** — External content (fonts, libraries) with URLs

### For Verification

16. **/input/repo/** — The original investment memo repository (read-only mount)
17. Run any chart script: `python assets/charts/01-financial-trajectory.py`
18. Check any trace: `cat audit/traces/slide8_scenarios.md`

## What This Deck Is

A board-of-advisors presentation for GitLab Inc. (GTLB) that walks the board through:
- **What** the agent recommended: BUY, $42 price target, 95% upside
- **How** it got there: the reasoning trail from filings → analysis → conclusion
- **Why** you should trust it: the audit trail mechanism

The audience is technical and skeptical. They want to evaluate the agent system's reasoning, not just rubber-stamp a stock pick.

## What This Deck Is Not

- A sales pitch. It's a capability demonstration.
- A re-delivery of the memo. The board has read the memo.
- A polished marketing deck. It's a discussion tool.

## Repository Structure

```
/deck/                  Final presentation (pptx + PDF export)
/deck/source/           Source files used to build the deck
  build_deck.py         PPTX generation script
  build_pdf.py          PDF generation script
/assets/
  /charts/              Every chart + the script that built it (10 charts)
  /diagrams/            Process diagrams, dependency graphs
  /images/              Any photography, icons, or imagery
  /tables/              Source data for every table (CSV)
/audit/
  /traces/              For every claim, a trace file pointing to /input/repo/
  /numbers.md           Every number with its source path
  /quotes.md            Every quote with file + line number + context
  /reconciliation.md    Spot-check: 5 random numbers, fully reconciled
/narrative/
  /storyboard.md        The full narrative arc before any slides were built
  /alternatives.md      Other narrative structures considered and rejected
  /audience-analysis.md Who's on the board, what they care about
/research/
  /notes/               Working notes, dated, one file per session
  /questions-deck.md    Questions about the input repo and how resolved
  /dead-ends-deck.md    Slide concepts that didn't make the cut
/decisions/             ADR-style records for every non-obvious choice
/sources.md             External content (fonts, libraries) with URLs
/tool-log.md            Every tool call in order with one-line justification
README.md               This file
```

## The 15 Slides

| # | Title | Key Visual | Time |
|---|-------|-----------|------|
| 1 | Recommendation & Price Target | Confidence meter, price stats | 1 min |
| 2 | The Thesis in One Slide | 5 bullet points | 1 min |
| 3 | What Would Change the Recommendation | 3 condition cards | 1 min |
| 4 | Financial Trajectory | Revenue/margin/FCF chart | 2 min |
| 5 | Competitive Position | Growth vs. margin scatter | 2 min |
| 6 | The Mispricing Thesis | 3-column comparison | 2 min |
| 7 | Risk Assessment | Probability vs. impact matrix | 2 min |
| 8 | Bear/Base/Bull Scenarios | Probability distribution | 2 min |
| 9 | DCF Bridge | Waterfall chart | 2 min |
| 10 | The Reasoning Trail | Dependency graph | 2 min |
| 11 | Dead Ends | Failed approaches bar chart | 2 min |
| 12 | Confidence & Limitations | Radar chart | 2 min |
| 13 | How to Audit This Deck | Step-by-step instructions | 2 min |
| 14 | Number Reconciliation | Verification table | 2 min |
| 15 | Q&A / Discussion | Discussion prompts | 3 min |

**Total: 30 minutes presentation + 15 minutes Q&A**

## Key Numbers (All Traced)

| Number | Slide | Source |
|--------|-------|--------|
| $42.00 target | 1 | memo/gitlab_investment_memo.md |
| $21.51 current | 1 | extracted/company_info.json |
| $955M revenue FY2026 | 4 | extracted/income_statement_annual.csv |
| -7.4% op margin FY2026 | 4 | extracted/income_statement_annual.csv |
| $222M FCF FY2026 | 4 | extracted/cash_flow_annual.csv |
| 115% NRR | 7 | extracted/financial_summary.json |
| $38.52 DCF base case | 6 | memo/gitlab_investment_memo.md |
| $45.98 expected value | 8 | memo/gitlab_investment_memo.md |

## Reproducing Charts

Every chart in the deck has a script in `/assets/charts/` that regenerates it:

```bash
cd /workspace
python assets/charts/01-financial-trajectory.py  # Financial trajectory
python assets/charts/02-competitive-position.py  # Competitive scatter
python assets/charts/03-scenario-distribution.py # Bear/base/bull
python assets/charts/04-saas-metrics.py          # ARR/NRR
python assets/charts/05-risk-matrix.py           # Risk matrix
python assets/charts/06-reasoning-trail.py       # Reasoning graph
python assets/charts/07-dead-ends.py             # Dead ends
python assets/charts/08-confidence-limitations.py # Confidence radar
python assets/charts/09-dcf-bridge.py            # DCF waterfall
python assets/charts/10-stock-price.py           # Stock price history
```

## License

This deck is for informational and educational purposes only. It does not constitute investment advice.
