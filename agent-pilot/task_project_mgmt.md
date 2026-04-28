You have access to a meeting-notes log at `/input/repo/meeting_notes.md` — six weekly meetings of the Project Aurora team (a dashboard-refresh + embedded-SDK initiative at a fictional SaaS company). Notes are loosely-structured plain prose; the same workstreams come up across multiple weeks with status updates, scope changes, and discovered risks.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit. Source notes are your only material — no internet research; do not invent.

Your task: **produce a structured project status report** for a project sponsor (the CEO Brendan, who attends sporadically and needs a clear picture). Specifically:

1. A **workstream/roadmap section** listing each major workstream, its owner, its current status, and whether it's blocking V1.
2. A **risk register** listing each material risk with severity and a brief description.
3. A **decisions log** listing each material decision made over the 6 weeks, with who decided and when.
4. A **milestone list** with targets and owners.

## Output structure

```
/workspace/status_report.md   The structured status report (primary deliverable)
/workspace/research/notes.md  Working notes (your synthesis process)
/workspace/decisions/         (Optional) ADR-style records for non-obvious framing choices
README.md                     How to read this output
```

The status report should have these sections in this order, clearly labeled:
- **Headline** (1-2 sentence current state)
- **Workstreams** (table or bulleted list, one row per workstream)
- **Risks** (table or list, ordered by severity)
- **Decisions made** (chronological list with date + decision + decider)
- **Milestones** (target dates with owners)
- **Open questions / asks** (anything the CEO needs to weigh in on)

## Rules of the road

- **Read all 6 weeks before writing.** Status of each workstream evolves across weeks. Use the most recent status, not the first mention.
- **Don't invent owners or dates.** If the source says "owner TBD" or doesn't say, don't make one up.
- **Capture the decisions, not just the discussions.** "Discussed mobile strategy" is not a decision; "Mobile = web-responsive in V1, native in V2 (week 4)" is.
- **Don't pad.** A wall of text isn't a status report. Aim for ≤500 words across all sections combined.
- **Stay grounded.** Every claim in the report must trace to one of the 6 weekly notes. Cite the week (e.g., "week 4") next to each substantive claim.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
