You have access to the git repository produced by the investment memo task, mounted read-only at `/input/repo/`. You have a fresh Linux VM with internet, a Python environment, standard CLI tools, git, and presentation-building libraries (python-pptx, matplotlib, plotly, etc.). No time limit, no tool call limit, no output length limit.

Your task: build a board-of-advisors presentation that walks the board through both what the agent recommended and how it got there. The audience is technical and skeptical — they want to evaluate the agent system's reasoning, not just rubber-stamp a stock pick. Treat this as a capability demonstration where the reasoning trail is as important as the conclusion.

Everything you produce must live in a new git repository. Commit early, commit often, write real commit messages explaining why not what. The repo is the deliverable, not just the deck.

Required repo structure:
```
/deck/                  Final presentation (pptx + PDF export)
/deck/source/           Source files used to build the deck (any markdown, scripts, templates)
/assets/
  /charts/              Every chart in the deck, as standalone files, with the script that built each one
  /diagrams/            Process diagrams, dependency graphs, decision trees
  /images/              Any photography, icons, or imagery used
  /tables/              Source data for every table, as CSV
/audit/
  /traces/              For every claim in the deck, a trace file pointing back to /input/repo/
  /numbers.md           Every number in the deck, with its source path in the input repo
  /quotes.md            Every quote in the deck, with file + line number in the input repo
  /reconciliation.md    Spot-check: pick 5 random numbers from the deck, fully reconcile each
/narrative/
  /storyboard.md        The full narrative arc before any slides were built
  /alternatives.md      Other narrative structures considered and rejected
  /audience-analysis.md Who's on the board, what they care about, how the deck addresses each
/research/
  /notes/               Working notes, dated, one file per session
  /questions.md         Questions you had about the input repo and how you resolved them
  /dead-ends.md         Slide concepts and visualizations that didn't make the cut, with why
/decisions/             ADR-style records for every non-obvious choice
/sources.md             Any external content fetched (icons, fonts, reference imagery), URLs + SHAs
/tool-log.md            Every tool call in order, with one-line justification
README.md               How to navigate the repo, in what order to read it
```

Rules of the road:

- Every claim in the deck must trace back to the input repo. If a slide says "revenue grew 14% in FY2024," there must be a trace file in `/audit/traces/` that points to the specific commit, file, and line in `/input/repo/` where that number was established. A board member should be able to click any number on any slide, follow the trace, and land on a 10-K page in under two minutes.
- Show the reasoning, not just the conclusion. At least one slide must visualize the agent's actual decision process — the dependency graph between filings read, decisions made, and conclusions drawn. Use the input repo's `/decisions/` and commit history as source material.
- Surface the dead-ends honestly. Include a slide on hypotheses the agent investigated and rejected, drawn from the input repo's `dead-ends.md`. Boards trust analysts who show their work; they don't trust analysts who only show wins.
- Confidence visualization. The bear/base/bull scenarios from the memo must appear as a real visualization — probability-weighted, not three bullet points. Show the price target as a distribution, not a number.
- One slide audits itself. Include a "how to verify this deck" slide showing the audit trail mechanism: how a board member can clone this repo, pick any claim, and reconstruct the reasoning. This is the single most important slide for a skeptical technical board.
- Design choices are documented. Color palette, typography, chart conventions — every non-obvious aesthetic decision gets an ADR. "Used red for downside scenarios" is fine to skip; "chose a sequential colormap over diverging because the data has a natural zero point at current price" is an ADR.
- Charts are reproducible. Every chart in the deck has a script in `/assets/charts/` that regenerates it from data in `/input/repo/`. A board member should be able to run any script and get back the exact chart they're looking at.
- Quotes preserve context. Any management quote pulled into the deck must include in `/audit/quotes.md` not just the source line but the surrounding paragraph, so a board member can verify the quote isn't ripped out of context.
- The deck itself: 15-25 slides, designed for a 30-minute presentation with 15 minutes of Q&A. Lead with the recommendation. End with the limitations and confidence section from the original memo, but as a visual — not a wall of text. Assume the board has read the memo; this deck is for discussion, not redelivery.
- Visual design is colorful and distinctive but earns it. No clip-art, no generic stock imagery, no AI-generated faces. Charts should be the visual centerpiece. If you use color decoratively, it should reinforce the data — sector colors consistent across slides, scenario colors consistent between the model and the deck, etc.
- The narrative storyboard comes before any slide is built. `storyboard.md` must be committed before the first slide file. Commit history will be checked.
- Commit messages explain why. "Add competitive landscape slide" is bad. "Restructure competitive slide from market-share pie to growth-vs-margin scatter after realizing pie obscures the actual thesis (margin compression at scale)" is good.

Required slide content (you decide order and exact framing):
- Recommendation and price target, up front, with confidence
- The thesis in one slide, in the agent's own words
- The 2-3 things that would change the recommendation
- Financial trajectory: historical and projected, with the inflection points called out
- Competitive position, with the comp set and why these comps
- The mispricing thesis (or the efficient-pricing argument, if that's what the memo concluded)
- Risk assessment, prioritized, with what would have to be true for each risk to materialize
- Bear/base/bull scenarios as a probability-weighted visualization
- The reasoning trail: a visualization of how the agent moved from filings → analysis → conclusion
- Dead ends: hypotheses investigated and rejected
- Confidence and limitations, as a visual
- How to audit this deck (the self-audit slide)

When you're done, the final commit should tag a release. A board member with no context should be able to clone the repo, read the README, and within 10 minutes understand both the recommendation and how to verify any part of it.

Begin. Work autonomously in `/workspace`. Use the `bash`, `write_file`, `read_file`, and `done` tools. The input repo is at `/input/repo/` (read-only). Commit your work in your own repo at `/workspace/` frequently. Do not ask for clarification — make reasonable choices and document them in `/decisions/`.
