# Sources

Every external content fetched or referenced during this presentation build.

## Chart Dependencies

| Source | URL | Version | Notes |
|--------|-----|---------|-------|
| matplotlib | https://matplotlib.org/ | 3.10.9 | Chart generation |
| numpy | https://numpy.org/ | 2.4.4 | Numerical computing |
| pandas | https://pandas.pydata.org/ | 3.0.2 | Data manipulation |
| scipy | https://scipy.org/ | (installed) | Probability distributions |
| python-pptx | https://python-pptx.readthedocs.io/ | (installed) | PowerPoint generation |

## Input Data Sources

| Source | Path | Notes |
|--------|------|-------|
| Investment memo | /input/repo/memo/gitlab_investment_memo.md | Primary source for all claims |
| Financial data | /input/repo/extracted/ | Parsed financial data from yfinance |
| Competitor data | /input/repo/extracted/competitor_data.json | Peer company financials |
| Earnings transcripts | /input/repo/raw/transcripts/ | Seeking Alpha transcripts |
| Decision records | /input/repo/decisions/ | ADRs from original analysis |
| Dead ends | /input/repo/research/dead-ends.md | Failed approaches |

## Fonts

| Font | Source | Notes |
|------|--------|-------|
| Calibri | System font | Default presentation font |

## Icons & Imagery

None used. All visuals are data-driven charts generated from scripts.

## Color Palette

Defined in /workspace/decisions/004-color-palette.md (ADR-004).
