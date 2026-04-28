You have access to:
- An internal draft memo at `/input/repo/draft_memo.md` — a meandering ~1500-word writeup of an outage from a senior engineering manager, written for "internal" eyes.
- A spec for three audience rewrites at `/input/repo/audience_briefs.json` — explaining who each rewrite is for, what it must include, what it must NOT include, the word limit, and the appropriate tone.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit. Source memo is your only material — no internet research; do not invent facts.

Your task: **produce three rewrites** of the same incident, each tailored to its target audience. Output filenames as specified in `audience_briefs.json`.

The three audiences are:
1. **CEO brief** — 5-minute board-prep read for the CEO. Concise, executive, direct stance.
2. **Customer email** — mass email to affected customers. Warm, accountable, no jargon, explicit SLA-credit offer.
3. **Legal summary** — for in-house counsel reviewing SLA-credit obligations. Precise, dispassionate, factual.

## Rules of the road

- **Each rewrite has its own constraints.** Read `audience_briefs.json` carefully. The customer email must NOT mention the named engineer or the "second outage in 90 days" framing. The legal summary must NOT include marketing language or speculation. The CEO brief must NOT include engineering-jargon.
- **Don't invent facts.** Every number, time, and customer count in your rewrites must be present in the source memo. Don't smooth over gaps with plausible-sounding interpolation.
- **Faithfulness over polish.** A rewrite that's beautifully written but contradicts the source memo is worse than a rougher one that's accurate.
- **Match the tone, not just the content.** A "CEO brief" written in customer-email tone is wrong. A "customer email" written in legal-summary tone is wrong.
- **Stay within word limits.** The max_words per audience is in `audience_briefs.json`. Use it as a hard ceiling.

## Output structure

```
/workspace/ceo_brief.md         CEO rewrite (≤250 words)
/workspace/customer_email.md    Customer rewrite (≤350 words)
/workspace/legal_summary.md     Legal rewrite (≤400 words)
/workspace/decisions/           ADR-style records for any non-obvious choices (e.g. how you decided what to omit per audience)
/workspace/research/notes.md    Working notes
README.md                       How to read this output (1-2 paragraphs)
```

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
