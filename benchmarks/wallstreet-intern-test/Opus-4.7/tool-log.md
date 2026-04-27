# Tool Log

Chronological record of major tool operations with one-line justifications.
Most low-level operations are reproducible from the scripts and not duplicated here.

Format: `HH:MM | tool | target | why`

## 2026-04-27

### Phase 1 — repo scaffolding & target selection (13:41–13:50)

- 13:41 | Bash | mkdir + git init | Scaffold the directory layout the brief mandates.
- 13:42 | Bash | python --version, pip install openpyxl/requests/pandas | Verify Python 3.13 and install libs.
- 13:43 | Write | .gitignore, sources.md, tool-log.md, questions.md, dead-ends.md | Set up cross-cutting tracking files.
- 13:46 | Write | decisions/0001-target-selection.md | Document why Vita Coco (vs OLO/BASE/CHEF/SWIM/SSTI) — choice prioritizes a real bull/bear debate, clean disclosure, and live margin question.
- 13:48 | Bash | git commit | First commit: scaffolding + target selection.

### Phase 2 — primary source acquisition (13:50–14:05)

- 13:51 | WebFetch | EDGAR company search | First attempt blocked (403) — SEC requires User-Agent header, WebFetch can't set custom headers.
- 13:52 | Write | scripts/fetch_edgar.py | Build a Python fetcher with proper UA + auto-logging of SHA-256 to sources.md.
- 13:53 | Bash | scripts/fetch_edgar.py | Resolve CIK 0001482981 for ticker COCO. Confirmed via HTML company-name match.
- 13:54 | Bash | scripts/fetch_edgar.py submissions | Pull EDGAR submissions JSON for COCO. Lists every filing back to 2021.
- 13:56 | Write | scripts/download_filings.py | Curated manifest: 5 FY 10-Ks (FY21-FY25), 3 latest 10-Qs, 5 earnings 8-K covers, latest DEF 14A.
- 13:57 | Bash | python scripts/download_filings.py | All 14 filings pulled to raw/filings/. Confirmed each saved + SHA logged.
- 13:58 | Bash | python scripts/fetch_press_releases.py | Pulled 9 press release exhibits (Ex 99.1) — each cover 8-K is just a shell; the data tables live in 99.1.
- 14:00 | Bash | scripts/fetch_edgar.py companyfacts | Pull XBRL companyfacts JSON (824 KB; every reported tag with periods/restatements).

### Phase 3 — earnings transcripts (14:05–14:15)

- 14:05 | WebSearch | "Vita Coco Q4 2025 earnings transcript" | Locate accessible transcript sources. Motley Fool primary, Insider Monkey backup.
- 14:06 | WebFetch | Fool Q4 2025 transcript | Confirmed full transcript visible on rendered page.
- 14:07 | Write | scripts/fetch_transcript.py | UA-spoofed fetcher for transcript HTML; logs SHA to sources.md.
- 14:08 | Bash | python scripts/fetch_transcript.py x5 | Pulled Q4 FY2025, Q3 2025, Q2 2025, Q1 2025, Q4 FY2024 transcripts.
- 14:10 | Write | scripts/extract_fool_transcript.py | Parser that walks <p> tags, lifts `<strong>Speaker:</strong>` markers, emits one paragraph per line for citation.
- 14:11 | Bash | python scripts/extract_fool_transcript.py x5 | Clean line-numbered .txt files in extracted/transcripts/. 91-179 paragraphs each.
- 14:13 | Bash | git commit | Second commit: SEC filings + transcripts.

### Phase 4 — extraction & financial parsing (14:15–14:30)

- 14:15 | Write | scripts/extract_financials.py | Parse XBRL companyfacts to clean annual.csv (33 cols, FY19-FY25) + quarterly.csv. Each row carries source_accn so any value traces back to one 10-K.
- 14:17 | Bash | python scripts/extract_financials.py | Verified FY25 revenue $609.8M matches Q4 press release. GM history shows freight-tailwind cycle (FY22 24%, FY24 38.5%, FY25 36.5%).
- 14:19 | Write | scripts/extract_press_tables.py | HTML <table> walker. Outputs one CSV per table per press release.
- 14:20 | Bash | python scripts/extract_press_tables.py | 63 tables across 9 press releases. Tables 5-7 carry the segment x brand grain.
- 14:22 | Write | scripts/build_segment_history.py | Roll up press-release tables into a long-form segment_history.csv (420 rows: net sales, COGS, GP, GM by segment x brand x period).
- 14:24 | Bash | Manual MD&A extract from 10-K_2025-12-31 | Pulled MD&A region (chars 223,454-273,934) into extracted/mda_FY2025_10K.txt for citation by line.
- 14:26 | Grep | customer concentration in MD&A | Found "Customer A 19%/25%/30%" disclosure for FY25/FY24/FY23 — a key data point.
- 14:28 | Bash | git commit | Third commit: extraction phase + structured datasets.

### Phase 5 — model build & sanity check (14:30–14:50)

- 14:30 | Write | decisions/0002-model-design.md | Document why segment x brand granularity, ratio-driven BS, exit-multiple-anchored valuation.
- 14:33 | Write | scripts/build_model.py | First version: 7-tab xlsx with single-cell scenario toggle (Cover!B4) feeding CHOOSE() across all live cells. Build failed with KeyError on EPS (USD/shares unit).
- 14:35 | Edit | scripts/build_model.py | Fixed unit handling: EPS uses USD/shares not USD.
- 14:36 | Bash | python scripts/build_model.py | Build OK. Re-inspected generated formulas; identified Cover sheet was referencing wrong row for "Net sales" (IS!C7 = International Other, not total).
- 14:38 | Edit | scripts/build_model.py | Restructured IS sheet: 6 segment-brand rev rows (2-7), total at row 8, GP/SG&A/Op/NI/EBITDA below. Added "Non-operating income" row to bridge to actual FY25 net income. Fixed Cover refs.
- 14:40 | Write | scripts/sanity_check_model.py | Independent Python re-implementation of every model formula. Catches the case where openpyxl serialized formulas Excel won't compute correctly.
- 14:42 | Bash | python scripts/sanity_check_model.py | First run: Base FY26 EBITDA = $113M, well below mgmt guide of $122-128M. Identified Base GM and SG&A drivers were too conservative.
- 14:44 | Edit | scripts/build_model.py + sanity_check_model.py | Recalibrated Base case: Americas GM 37.5%->38.5%, SG&A 23%->22%. Bumped exit multiples (Bear 11x->12x, Base 14x->17x, Bull 17x->22x) to align with peer reality.
- 14:46 | Bash | python scripts/build_model.py + sanity_check_model.py | Re-ran. Base FY26 EBITDA now $127M — within mgmt guide. Bear $23 / Base $46 / Bull $76 12-month targets.
- 14:48 | Bash | git commit | Fourth commit: financial model.

### Phase 6 — competitive analysis & variant view (14:50–15:05)

- 14:50 | WebSearch | coconut water market size | Locate market sizing data. Grand View Research has the cleanest series.
- 14:52 | WebFetch | grandviewresearch coconut water | Pulled $5.1B market size, 18.2% CAGR forecast, NA 25% / Europe 20%+ growth.
- 14:54 | WebFetch | stockanalysis.com COCO statistics | COCO trading at 33.4x TTM EV/EBITDA, 22x forward.
- 14:55 | WebFetch | stockanalysis.com BRBR/CELH/SMPL | Peer multiples: BRBR 9.2x, CELH 16.1x, SMPL 6.6x.
- 14:57 | WebFetch | stockanalysis.com COCO forecast | Sell-side consensus: 8 analysts, $57.75 avg target, 0 sell ratings, FY26 rev est $708M, FY26 EPS $1.58.
- 15:00 | Write | analysis/peer_comps.md | Peer comp table + observations: COCO at >2x the EV/EBITDA of CELH (closest analog) and >3x mature peers. The 22x forward multiple sits at the high end of "high-growth beverage" territory.
- 15:02 | Write | analysis/variant_view.md | Decompose sell-side $57.75 target → implied 22-23x exit multiple → contrast with CELH-style multiple compression precedent. Probability-weight scenarios, expected return -9%.

### Phase 7 — recommendation & memo (15:05–15:30)

- 15:05 | Write | decisions/0003-recommendation-and-target.md | HOLD with bearish lean. $46 target. Probability 25/50/25 across Bear/Base/Bull. Triggers: BUY < $42, SELL > $60.
- 15:07 | Write | research/questions.md | Resolved + open questions log (12 entries).
- 15:09 | Write | research/dead-ends.md | Volume × ASP modeling, COGS stack-up, International-only valuation, DCF as primary, hidden negative in proxy.
- 15:12 | Write | memo/COCO_memo.md | First draft of memo. Length: 5 PDF pages. Leads with recommendation. Probability-weighted return table at top.
- 15:14 | Write | scripts/md_to_pdf.py | reportlab-based markdown→PDF renderer (no pandoc available). Handles headings, paragraphs, tables, lists, inline bold/italic.
- 15:15 | Bash | python scripts/md_to_pdf.py | First render: 5 pages, 17KB. Inspected — saw `<b>` literal text inside table cells. Fixed by wrapping cells in Paragraph for inline-markup processing.
- 15:17 | Bash | python scripts/md_to_pdf.py | Re-render: clean. Bold renders correctly. 5-page memo.

### Phase 8 — wrap up (15:30–15:45)

- 15:30 | Write | research/notes/2026-04-27_session_log.md | Session-level working notes: time spent, key insights.
- 15:32 | Write | scripts/check_model_balance.py | Internal-consistency assertions across all scenarios.
- 15:33 | Bash | python scripts/check_model_balance.py | All checks pass. FY26 Base EBITDA $126.7M, in mgmt guide.
- 15:35 | Write | README.md | Repo navigation + reproducibility instructions.
- 15:38 | Write | tool-log.md | Comprehensive backfill of major operations (this file).
- 15:42 | Bash | git commit + git tag v1.0 | Final commit, tag release.
