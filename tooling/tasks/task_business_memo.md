You have access to an internal acquisition diligence pack at `/input/repo/deal_pack.md`. The pack was prepared by the Corp Dev team and recommends PROCEEDING to LOI on the acquisition of Borealis Analytics for $84M.

You are an executive committee member who has been asked to review this pack independently. Your job is **not** to ratify the recommendation — it is to assess the recommendation critically and give the executive committee your own view.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit. No internet — work from the diligence pack only.

## Your task

Produce **a 1-page memo** (≤700 words) for the executive committee with:

1. **Your recommendation** — proceed, hold, or pass — and the conditions under which you'd change your stance.
2. **The strongest concerns** with the deal pack as presented. Where does the pack overclaim, underexplain, or omit relevant context? You should expect to find issues; deal packs are advocacy documents, not balanced analysis.
3. **Specific diligence asks** for the next 2 weeks if the committee wants to keep the deal alive.

## Constraints

- The pack is your only source. Don't invent customer names, financial figures, or any other facts not present.
- The Corp Dev team's recommendation may or may not be right. Treat it as one input among several to assess, not a conclusion.
- You don't need to find every issue — but a memo that ratifies the pack's recommendation without pushback should set off alarm bells. The pack was written to advocate; your job is to balance.
- Cite the pack inline (e.g., "Per the financials table…") when you're naming a specific number or claim. Be specific.

## Output structure

```
/workspace/memo.md             The 1-page review memo (your primary deliverable)
/workspace/concerns.md         A longer enumeration of every concern you considered, including ones you ranked lower
/workspace/asks.md             The diligence-ask list for the next 2 weeks (specific questions, owners, deadlines)
/workspace/decisions/          ADRs for any judgment calls
README.md                      How to read this output
```

The memo (`memo.md`) is the primary deliverable. Concerns and asks support it.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
