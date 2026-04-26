# External Content Sources

**Date:** June 18, 2025  
**Purpose:** Document any external content fetched (icons, fonts, reference imagery)

---

## Fonts

### Arial
- **Usage:** Typography for all charts and slides
- **Source:** System font (Windows/Mac)
- **License:** Proprietary (Microsoft Core Fonts)
- **SHA:** N/A (system font)
- **Notes:** Used for all text in charts and slides. Falls back to sans-serif if not available.

### Font Alternatives
- **Helvetica:** Close alternative, used if Arial unavailable
- **DejaVu Sans:** Open source alternative, used if Arial unavailable

---

## Icons

### No external icons used
- All icons are simple shapes (circles, squares, triangles)
- Created using matplotlib's built-in markers
- No external icon libraries used

---

## Reference Imagery

### No external imagery used
- All visuals are data-driven charts
- No clip-art, stock imagery, or AI-generated faces
- No photography used

---

## Color Palette

### GitLab Brand Colors
- **Primary Blue:** #1E88E5 (from GitLab logo)
- **Source:** GitLab brand guidelines (publicly available)
- **SHA:** N/A (public brand guidelines)

### Data-Driven Colors
- **Green (Positive):** #43A047
- **Red (Negative):** #E53935
- **Bear Scenario:** #D32F2F
- **Base Scenario:** #388E3C
- **Bull Scenario:** #1976D2

### Neutral Colors
- **Text (Dark):** #212121
- **Text (Light):** #FFFFFF
- **Background:** #FAFAFA
- **Grid Lines:** #E0E0E0

---

## Chart Libraries

### Matplotlib
- **Version:** 3.7.0+
- **Source:** Python package (pip install matplotlib)
- **License:** Matplotlib License (BSD-style)
- **SHA:** N/A (pip package)

### Pandas
- **Version:** 1.5.0+
- **Source:** Python package (pip install pandas)
- **License:** BSD 3-Clause
- **SHA:** N/A (pip package)

---

## Data Sources

### yfinance
- **Source:** https://github.com/ranaroussi/yfinance
- **License:** Apache License 2.0
- **SHA:** N/A (pip package)
- **Usage:** Financial data, competitor data, company info

### SEC Filings
- **Source:** https://www.sec.gov/
- **Access:** Blocked (403 errors)
- **Resolution:** Used yfinance as secondary source

### Seeking Alpha
- **Source:** https://seekingalpha.com/
- **Usage:** Earnings call transcripts
- **License:** Terms of Service (no direct scraping)

---

## No External Content Used

The following are explicitly NOT used:
- Clip-art
- Stock imagery
- AI-generated faces
- External icons (all simple shapes)
- External photography
- External templates

---

## Verification

All external content is documented above. No external content was used beyond:
1. Fonts (Arial, system fallback)
2. Chart libraries (matplotlib, pandas)
3. Data sources (yfinance, SEC, Seeking Alpha)

All visuals are data-driven and created from scratch using the input repo data.
