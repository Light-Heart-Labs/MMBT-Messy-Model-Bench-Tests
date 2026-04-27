# Dead Ends

## Native PPTX Rendering QA

I checked for PowerPoint/LibreOffice command-line renderers so the PPTX could be exported and screenshot-tested through the host presentation engine. Neither `soffice` nor `libreoffice` was available in this environment, so the deck uses deterministic slide PNGs as the common source for PPTX, PDF, and preview QA.

## Market-Share Pie For Competitive Position

A market-share-style comp slide would have looked familiar, but the input repo did not establish comparable market-share numbers. It also would have obscured the actual point: YETI's valuation and operating-margin context look reasonable rather than obviously mispriced.

## Stock Imagery And Decorative Icons

I considered using outdoor product photography or generic boardroom imagery. I rejected it because the deck is a reasoning audit, and the prompt explicitly makes charts and process evidence the centerpiece.

## Screenshotting The Memo Workbook

Screenshots from the model workbook would have been fast, but they are hard to read in a board deck and less reproducible than chart scripts. The final deck rebuilds charts from CSV tables extracted from the input repo.
