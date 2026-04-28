You have access to a source pack at `/input/repo/sources.md` containing five public documents about a (fictional) Series-B logistics-tech startup, Nimbus Logistics, Inc. The five documents include the company's own press release, a TechCrunch news article, a former-employee blog post, a leaked internal memo, and an SEC Form D filing summary.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit. No internet research — use only the provided sources.

Your task: **produce a 1-page executive brief** for an investor evaluating whether to make a follow-on investment in Nimbus Logistics.

The brief must:
1. Be **at most 700 words** — this is for a partner who has 5 minutes.
2. Lead with a **clear stance** — should the investor make the follow-on or pass? (Or "more diligence needed" with specifics.)
3. Capture the **substantive facts** across all five sources, not just the press-release narrative.
4. Be **honest about source quality** — the press release is what the company wants you to think; the TechCrunch article and the leaked memo are what the company didn't want public; the blog post is one ex-employee's view.
5. **Cite sources inline** — use `[Source 1]`, `[Source 2]`, etc. when stating specific facts. Don't fabricate citations.
6. Avoid **invented numbers** — every metric in the brief must trace to one of the five sources.

Output structure:

```
/workspace/brief.md            The 1-page executive brief — your primary deliverable
/workspace/key-facts.md        A list of every material fact you incorporated, with source attribution
/workspace/research/notes.md   Working notes from your reading of the sources
/workspace/research/dead-ends.md   (optional) Ideas you considered and abandoned
/workspace/decisions/          ADR-style records for any non-obvious framing choices
README.md                      How to read this output
```

The brief itself (`brief.md`) is the deliverable. The supporting files exist so a reviewer can see how you reasoned to it.

## Rules of the road

- **Don't repeat the press release.** A brief that says "they raised $84M Series B led by Lightning Capital, doubled valuation, growth from $11M to $42M ARR" is just the press release with extra steps. The work is in synthesizing the press release with the contradictory signals from the other four sources.
- **Highlight tensions, not just facts.** "ARR is $42M (per company press release) but adjusted for December churn the run-rate is $36-37M" tells the reader something the press release alone doesn't.
- **Stay calibrated.** The leaked memo and the former-employee blog are real but not perfectly authoritative. Use language like "according to" rather than treating those as ground truth.
- **One clear recommendation.** A brief that says "on the one hand X, on the other hand Y, more diligence needed" is hedging. State a stance, with the caveats that would change it.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
