# Tool Log

| # | Tool | Command/Action | Justification |
|---|------|---------------|---------------|
| 1 | bash | find /input/repo/ -type f | Explore input repo structure |
| 2 | read_file | memo/gitlab_investment_memo.md | Read the primary source document |
| 3 | read_file | analysis/analysis_summary.md | Read analysis summary |
| 4 | read_file | decisions/001-003.md | Read ADRs from input repo |
| 5 | read_file | research/dead-ends.md | Read dead ends from input repo |
| 6 | read_file | research/questions.md | Read questions from input repo |
| 7 | read_file | research/notes/*.md | Read research notes |
| 8 | read_file | extracted/*.json,*.csv | Read all financial data files |
| 9 | read_file | tool-log.md, sources.md, README.md | Read input repo metadata |
| 10 | bash | git init, mkdir structure | Initialize workspace repo |
| 11 | write_file | narrative/storyboard.md | Create narrative arc (committed before slides) |
| 12 | write_file | narrative/alternatives.md | Document rejected structures |
| 13 | write_file | narrative/audience-analysis.md | Analyze board audience |
| 14 | bash | git commit (narrative) | Commit narrative before any visual work |
| 15 | write_file | assets/tables/*.csv | Create data tables for charts |
| 16 | write_file | assets/charts/01-07.py | Create chart generation scripts |
| 17 | bash | pip install scipy | Install scipy for distributions |
| 18 | bash | python3 assets/charts/*.py | Generate all chart PNGs |
| 19 | write_file | decisions/004-005.md | Create ADRs for design decisions |
| 20 | write_file | audit/numbers.md | Document every number with source |
| 21 | write_file | audit/quotes.md | Document every quote with context |
| 22 | write_file | audit/reconciliation.md | Spot-check 5 random numbers |
| 23 | write_file | audit/traces/*.md | Create trace files for key claims |
| 24 | write_file | research/notes/*.md | Create working notes |
| 25 | write_file | research/questions.md | Document questions and resolutions |
| 26 | write_file | research/dead-ends.md | Document rejected presentation concepts |
| 27 | bash | pip install python-pptx | Install PowerPoint library |
| 28 | write_file | deck/source/build_presentation.py | Build 16-slide presentation |
| 29 | bash | python3 deck/source/build_presentation.py | Generate PPTX file |
| 30 | write_file | sources.md | Document all external sources |
| 31 | write_file | tool-log.md | This file |
| 32 | write_file | README.md | Repository navigation guide |
| 33 | bash | git add -A && git commit | Final commit with release tag |
