# Audience Analysis

## Board Profile

The board audience is technical and skeptical. They are evaluating the agent system's reasoning, not just whether `YETI` is a good stock. Assume they have read the investment memo and now want to pressure-test:

- evidence quality,
- traceability,
- numerical provenance,
- judgment calls,
- rejected hypotheses,
- uncertainty handling,
- reproducibility,
- whether the agent knows when not to overclaim.

## What They Care About

| Board concern | Deck response |
| --- | --- |
| Did the agent anchor on a conclusion too early? | Show the source-to-decision graph, commit history, and dead-end slide. |
| Can numbers be audited quickly? | Use trace IDs on slides and include a self-audit slide with the exact trace workflow. |
| Is the stock recommendation defensible? | Lead with the HOLD / $41 target and then show valuation triangulation, scenarios, and what would change the call. |
| Did the agent fabricate a sell-side miss because the prompt asked for one? | Make the efficient-pricing conclusion explicit and show why consensus already embeds the obvious upside angles. |
| Did the agent handle model risk honestly? | End with a visual confidence/limitations matrix, not a boilerplate disclaimer. |
| Is the deck itself reproducible? | Save every chart's data and script, include audit traces, and preserve source paths back to the input repo. |

## Design Implications

This should feel like a technical board walkthrough: sharp, colorful, and evidence-led, but not decorative. Charts and diagrams should carry the story. Trace IDs should be visible but quiet. The deck should avoid generic consulting card grids because that would make the audit trail feel cosmetic rather than operational.
