# Questions Log

| Date | Question | Resolution | Evidence |
| --- | --- | --- | --- |
| 2026-04-27 | Is `/input/repo/` mounted in this runtime? | No. The equivalent input repository is available locally at the prior memo repo path and is tagged `v1.0-yeti-memo`; traces will use logical `/input/repo/...` paths plus input commit `8bb17db`. | `README.md`; initial repo inspection. |
| 2026-04-27 | Should the deck re-present the memo or demonstrate the reasoning system? | Demonstrate the reasoning system while leading with the recommendation. | `narrative/storyboard.md`; ADR 0001. |
| 2026-04-27 | Should visuals use screenshots from the input repo? | No. Rebuild charts and diagrams from extracted/model data so they are readable and reproducible. | ADR 0003. |
| 2026-04-27 | What charting stack is available? | System Python has `python-pptx` and Pillow but not matplotlib/plotly; use Pillow scripts for deterministic chart images. | ADR 0004; package probe. |
| 2026-04-27 | Can the host render native PPTX for QA? | No PowerPoint or LibreOffice renderer was available. The deck is therefore generated from deterministic slide PNGs that are inserted into PPTX and reused for PDF/previews. | ADR 0005; validation commands. |
| 2026-04-27 | Why did the competitive scatter initially show an empty plot? | The peer table stored operating margins as whole percentages, while the chart expected decimals. The chart renderer now divides those values by 100 before plotting. | `assets/charts/build_charts.py`; slide 09 preview. |
| 2026-04-27 | How should visual QA be preserved? | Generate a contact sheet from the same slide previews so reviewers can inspect every slide surface without relying on a private tool view. | `deck/previews/contact-sheet.png`; `deck/source/build_deck.py`. |
