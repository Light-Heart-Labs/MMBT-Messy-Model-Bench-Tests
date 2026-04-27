You have access to the DreamServer repository (Light-Heart-Labs/DreamServer). The repo is public, so you can read PRs, diffs, and comments without authentication — but the unauth GitHub API is rate-limited to 60 req/hr, so prefer cloning the repo and using `git fetch origin pull/<N>/head:refs/pull/<N>/head` over hammering the API. You have a fresh Linux VM with internet, a Python environment, standard CLI tools, git, the GitHub CLI (`gh`, unauthenticated), Docker (you can run sibling containers via the mounted host socket), GPU access on the host, and no time limit, no tool call limit, no output length limit.

Your task: audit **one open pull request** and produce a complete review with a merge/revise/reject recommendation. The audience is a project lead (Michael) who needs to decide whether this single PR is safe to merge into a project that has 400+ stars, active contributors with bounty incentives, and a partnership with AMD's developer program. Quality bar matters; speed of merge does not.

**The PR to audit: #1057** (https://github.com/Light-Heart-Labs/DreamServer/pull/1057)

Everything you do must live in a new git repository. Commit early, commit often, write real commit messages explaining why not what. The audit repo is the deliverable, not just the verdict.

Required repo structure:

```
/verdict.md              Merge / Revise / Reject + reasoning, traceable to specific lines
/summary.md              What the PR claims to do, in your words
/review.md               Line-by-line review notes
/diff-analysis.md        What the diff actually changes vs what it claims
/tests/                  Any tests you ran, with results
/trace.md                Pointers back to commits, files, lines reviewed
/research/
  /notes.md              Working notes from your investigation
  /questions.md          Questions you had and how you resolved them
  /dead-ends.md          Investigations that didn't pan out, with why
  /upstream-context.md   Relevant DreamServer architecture you needed to understand the PR
/decisions/              ADR-style records for any non-obvious choices (numbered sequentially, one file each)
/sources.md              External content fetched (docs, related issues, commits), URLs + SHAs
/tool-log.md             Every tool call, in order, with one-line justification
README.md                How to navigate the repo
```

Rules of the road:

- The verdict must be traceable. A reject must point to specific lines in the diff, specific test results, or specific architectural concerns documented in `/research/upstream-context.md`. "This looks wrong" is not a review; "this allocates a CUDA context per request which conflicts with the singleton pattern in `installer/gpu.py:142`" is.
- Run the code. If the PR changes code paths reachable by tests, you run those tests on the baseline (main) and on the PR branch, and you record both results in `/tests/`. If the PR touches installer logic, run the installer in a clean container. If the PR touches GPU code paths, note whether you tested on hardware, simulated, or skipped, and why. Skipping is allowed; skipping silently is not.
- Reproduce claimed bugs. If the PR claims to fix a bug, your job is to reproduce the bug on main first, then verify the PR fixes it. The reproduction script goes in `/tests/repro/`. If you can't reproduce the bug, the verdict reflects that.
- Risk scoring is explicit. Score the PR along documented axes — surface area touched, test coverage of affected code, reversibility, blast radius if wrong, contributor track record. The methodology is part of `/verdict.md` (no black-box scoring).
- Honor the bounty structure. PRs were submitted under a Small/Medium/Large bounty system ($40/$150/$400). The verdict should note which tier the PR claims and whether the actual change matches that tier.
- Distinguish the four reject reasons. Reject for correctness (the code is wrong), fit (the code is fine but doesn't belong in DreamServer), quality (the approach is salvageable but the execution isn't), or redundancy (another PR does this better). The verdict states which.
- Distinguish the three revise reasons. Revise for small fixes (clean it up and merge), missing tests (works but unverified), or architectural rework (right idea, wrong approach). The verdict states which and includes specific revision guidance.
- Surface AMD-relevant changes. If this PR touches ROCm, AMD GPU paths, or anything that could regress AMD compatibility, call that out explicitly in `/verdict.md`. Regressing AMD support is a different kind of cost than regressing some other path.
- Dead-ends matter. If you spent significant time chasing a thesis that didn't pan out, write it up in `/research/dead-ends.md`. The reasoning that didn't make the verdict is where you can see how the auditor actually thinks.
- The questions log. Every time you hit something you weren't sure about — "is this the intended behavior of the SearXNG container or a workaround?" — write the question down. Then write how you resolved it, or that you didn't and what assumption you made.
- ADRs for non-obvious choices. Why you chose to test installer logic in Ubuntu 22.04 instead of 24.04. Why you scored "blast radius" the way you did. Why you treated documentation-only changes as auto-approve or didn't. These choices are where audit value lives.
- Commit messages explain why. "Review PR #1057" is bad. "Mark PR #1057 stderr-truncation fix as MERGE after confirming the root cause is docker-compose putting actual error text at end of stream and the [-500:] slice correctly captures it" is good.
- Reproducibility. A maintainer should be able to clone the audit repo, read the verdict, and rerun any tests that produced it. Test scripts live in the repo, not just in your head.

When you're done, the final commit tags a release. A maintainer with 30 minutes should be able to clone the repo, read the verdict, and confidently decide whether to merge.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit progress frequently as you go. Do not ask for clarification — make reasonable choices and document them in `/decisions/`.
