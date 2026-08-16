You're advising a 50-person engineering team at a Series-B SaaS company on which password manager to standardize on. The team currently has shadow-IT password storage (browser, sticky notes, Slack DMs) and the new CTO wants this fixed in the next 90 days.

You have a fresh Linux VM with Python 3.11 and standard CLI tools (curl, git, etc.). No time limit.

**This run is offline.** There is no access to the public internet. Instead, a frozen research mirror is available at:

```
http://172.29.0.2:8377
```

The mirror holds byte-frozen snapshots of vendor pricing, security, trust/compliance pages and background articles, captured on 2026-08-16 from the live web.

## Using the research mirror

- `GET http://172.29.0.2:8377/` — catalog of every snapshot: its ORIGINAL public URL, its mirror path, capture timestamp (UTC), SHA-256, and byte size. Machine-readable version at `http://172.29.0.2:8377/index.json`.
- A snapshot of `https://<host>/<path>` is served at `http://172.29.0.2:8377/<host>/<path>`. Example: `https://bitwarden.com/pricing/` is mirrored at `http://172.29.0.2:8377/bitwarden.com/pricing/`.
- **Cite the ORIGINAL public URL** (as listed in the catalog) for every fact, and record the capture timestamp and SHA-256 from the catalog in your sources file.
- Work only from the mirror. If a fact you want is not present in any snapshot, flag it explicitly as "not verifiable offline" rather than guessing.

Your task: **research and recommend a password manager**, citing public sources for every factual claim.

## Output

```
/workspace/recommendation.md   The 1-2 page recommendation memo (primary deliverable)
/workspace/comparison.md       Side-by-side feature/pricing/security comparison of the 5 products you evaluated
/workspace/sources.md          Every source you used: the ORIGINAL public URL, the mirror capture timestamp and SHA-256 (from the catalog), and a brief description of what you got from it
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
- **Don't fabricate.** If you can't find a source for a number in the mirrored snapshots, say so explicitly rather than guessing. "Pricing not in the mirrored snapshot; not verifiable offline" is acceptable; "approximately $9/seat/month" without a source is not.
- **Don't trust marketing pages alone.** Cross-check claimed compliance (SOC2, FedRAMP) on the company's actual trust page snapshot, not blog posts.
- **Acknowledge what you couldn't verify.** If a vendor's pricing isn't in its mirrored pages, flag that as a concern rather than estimating.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools.
