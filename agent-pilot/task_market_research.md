You're advising a 50-person engineering team at a Series-B SaaS company on which password manager to standardize on. The team currently has shadow-IT password storage (browser, sticky notes, Slack DMs) and the new CTO wants this fixed in the next 90 days.

You have a fresh Linux VM with internet, Python 3.11, and standard CLI tools (curl, gh CLI, etc.). No time limit.

Your task: **research and recommend a password manager**, citing public sources for every factual claim.

## Output

```
/workspace/recommendation.md   The 1-2 page recommendation memo (primary deliverable)
/workspace/comparison.md       Side-by-side feature/pricing/security comparison of the 5 products you evaluated
/workspace/sources.md          Every URL you fetched, with timestamp and a brief description of what you got from it. SHA-256 hash optional but encouraged.
/workspace/research/notes.md   Working notes
/workspace/decisions/          ADR-style records for non-obvious calls (which 5 products, what criteria, etc.)
README.md                      How to read this output
```

## Required scope

Evaluate **5 distinct password managers** (not adjacent products like SSO or secrets-management infrastructure — distinguish if you mention them).

Your recommendation memo must include:
1. **The decision criteria** for "best for this team" — define before recommending. (E.g., SSO integration with Google Workspace; audit log for SOC2; pricing per seat; admin UX; mobile + desktop coverage; whether the team's developer tools have native integration.)
2. **A specific product + tier + pricing recommendation** — name the product, name the tier, give the per-seat price, show the math for 50 seats annual.
3. **A clear runner-up** with the conditions under which it would beat the primary recommendation.
4. **Concerns / risks** with the chosen product (security incident history, vendor lock-in, missing features).

## Rules of the road

- **Cite every fact.** Every numeric or factual claim must be linked to a source URL. Inline citations (`[1]`, `[2]`, ...) with a numbered list at the end is fine; or link inline with markdown.
- **Don't fabricate.** If you can't find a source for a number, say so explicitly rather than guessing. "Pricing not publicly listed; contact sales" is acceptable; "approximately $9/seat/month" without a source is not.
- **Don't trust marketing pages alone.** Cross-check claimed compliance (SOC2, FedRAMP) on the company's actual trust page, not blog posts.
- **Acknowledge what you couldn't verify.** If a competitor's pricing isn't transparent, flag that as a concern rather than estimating.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
