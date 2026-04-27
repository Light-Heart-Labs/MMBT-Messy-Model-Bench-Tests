# YETI Board-Of-Advisors Presentation Repository

This repository contains a board-facing presentation that explains both the YETI investment recommendation and the reasoning trail behind it. The deck is designed as a capability demonstration for a technical, skeptical board: it leads with the stock call, then shows how the agent system gathered evidence, made decisions, rejected tempting hypotheses, and made the output auditable.

Read order:

1. `deck/yeti_board_advisors_presentation.pdf` for the fastest review.
2. `deck/yeti_board_advisors_presentation.pptx` for the board presentation file.
3. `deck/previews/contact-sheet.png` to scan every slide surface quickly.
4. `audit/traces/` to verify any slide claim back to the input repo.
5. `audit/numbers.md`, `audit/quotes.md`, and `audit/reconciliation.md` for number, quote, and spot-check audit trails.
6. `assets/charts/` and `assets/diagrams/` for every reproducible visual and the scripts that generated it.
7. `assets/tables/` for every table used in the deck.
8. `narrative/storyboard.md` to confirm the narrative was committed before slide files.
9. `decisions/` for ADRs covering narrative, design, charting, and deck-rendering choices.
10. `research/` for working notes, questions, and slide dead ends.
11. `sources.md` and `tool-log.md` for external-source and tool-call audit trails.

Status: complete.

## Input Repo

The prompt specifies a read-only input repo at `/input/repo/`. In this execution environment that mount is not present; the equivalent completed input repository is available locally at:

`C:\Users\conta\Documents\Codex\2026-04-27\you-have-a-fresh-linux-vm`

When this presentation package is read inside the MMBT benchmark repository, the equivalent input repository is the parent model-entry directory:

`benchmarks/wallstreet-intern-test/GPT-5.5/`

Input commit/tag:

`8bb17db` / `v1.0-yeti-memo`

Audit traces use the logical `/input/repo/...` path required by the prompt and record the input commit. `deck/source/extract_input_data.py` resolves evidence in this order: `INPUT_REPO`, `/input/repo`, the original local sibling memo repo, then the parent MMBT model-entry directory.

## Rebuild

Run from the repository root:

```powershell
python deck\source\extract_input_data.py
python assets\charts\build_charts.py
python assets\diagrams\build_diagrams.py
python deck\source\build_deck.py
```

The final command regenerates:

- `deck/yeti_board_advisors_presentation.pptx`
- `deck/yeti_board_advisors_presentation.pdf`
- `deck/previews/slide-01.png` through `deck/previews/slide-20.png`
- `deck/previews/contact-sheet.png`
- `deck/source/slide_inventory.csv`

## Verification

To verify the deck mechanically:

```powershell
python -c "from pptx import Presentation; from pathlib import Path; p=Presentation('deck/yeti_board_advisors_presentation.pptx'); print(len(p.slides)); print(Path('deck/yeti_board_advisors_presentation.pdf').stat().st_size); print(len(list(Path('deck/previews').glob('slide-*.png'))))"
```

Expected output: 20 slides, a non-empty PDF, and 20 preview PNGs.
