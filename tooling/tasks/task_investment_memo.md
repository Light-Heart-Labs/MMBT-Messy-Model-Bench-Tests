You have a fresh Linux VM with internet, a Python environment, standard CLI tools, and git. No time limit, no tool call limit, no output length limit. Take as long as you need and produce as much as the work requires.

Pick any publicly traded US company with a market cap between $1B and $10B. Build a complete investment memo on it: thesis, financial model, competitive analysis, risk assessment, buy/hold/sell recommendation with a 12-month price target.

Everything you do must live in a git repository. Commit early, commit often, write real commit messages. The repo is the deliverable, not just the memo.

Required repo structure:
```
/memo/                  Final memo (PDF + source markdown)
/model/                 Three-statement financial model (xlsx)
/raw/
  /filings/             Every SEC filing you downloaded, original format
  /transcripts/         Every earnings call transcript, original source
  /other/               Any other primary source (press releases, etc.)
/extracted/             Parsed/cleaned data from /raw/, with extraction scripts
/analysis/              Notebooks and scripts for any analysis you ran
/research/
  /notes/               Working notes, dated, one file per research session
  /questions.md         Running list of questions you had and how you resolved them
  /dead-ends.md         Things you investigated that didn't pan out, with why
/decisions/             ADR-style decision records for every non-obvious choice
/sources.md             Every URL you fetched, with timestamp and SHA of content
/tool-log.md            Every tool call, in order, with a one-line justification
README.md               How to navigate the repo, in what order to read it
```

Rules of the road:

- Every number in the memo must be traceable. If the memo says "revenue grew 14% in FY2024," there must be a path from that claim back to the 10-K in /raw/filings/, through an extraction step in /extracted/, into a cell in the model, into the memo. A human should be able to follow that path in under two minutes.
- Every quote from management must link to the specific transcript file and line number.
- Every external claim ("the industry is growing 8% per year") must cite a source in sources.md with the URL and the SHA of the content as you fetched it. No uncited claims, even ones that "everyone knows."
- Decision records: any time you make a non-obvious choice — which company, which competitors, which multiples, what discount rate, what terminal growth — write a short ADR explaining the alternatives you considered and why you chose what you chose. These go in /decisions/ numbered sequentially.
- Dead ends matter. If you spent an hour chasing a thesis that didn't pan out, write it up in dead-ends.md. The reasoning that didn't make the final memo is often where you can see how the agent actually thinks.
- The questions log: every time you hit something you weren't sure about, write the question down. Then write how you resolved it (or that you didn't). This is the single highest-signal artifact for auditing.
- Commit messages should explain why, not what. "Add Q3 2024 revenue to model" is bad. "Switch revenue driver from units × ASP to subscription cohorts after finding cohort disclosure in 10-K p. 47" is good.
- The memo itself: max 8 pages, lead with the recommendation, suitable for a PM who will spend 15 minutes on it. Bear/base/bull scenarios with explicit probabilities. A "confidence and limitations" section at the end covering what you're sure about, what you're guessing, what a human analyst would do that you didn't.
- Find at least one thing the sell-side appears to be missing or mispricing. If you can't, say so and explain why the stock is efficiently priced — and put the analysis that led to that conclusion in /analysis/ so it can be audited.

When you're done, the final commit should tag a release. The repo should be self-contained: a stranger should be able to clone it and reconstruct your entire reasoning process from the files alone.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit progress frequently as you go. Do not ask for clarification — make reasonable choices and document them in /decisions/.
