You have access to the DreamServer repository (Light-Heart-Labs/DreamServer) and 75 open pull requests against it. The repo is public, so you can read PRs, diffs, and comments without authentication — but the unauth GitHub API is rate-limited to 60 req/hr, so prefer cloning the repo with `git fetch origin pull/*/head` and doing diff analysis locally over hammering the API per PR. You have a fresh Linux VM with internet, a Python environment, standard CLI tools, git, the GitHub CLI (`gh`, unauthenticated), Docker (you can run sibling containers via the mounted host socket), GPU access on the host, and no time limit, no tool call limit, no output length limit.

Your task: audit all 75 open PRs and produce a complete triage report with a merge/revise/reject recommendation for each, plus a strategic synthesis for the maintainer. The audience is the project lead, who needs to clear a backlog without breaking a project that has 400+ stars, active contributors with bounty incentives, and a partnership with AMD's developer program. Quality bar matters; speed of merge does not.

Everything you do must live in a new git repository. Commit early, commit often, write real commit messages explaining why not what. The audit repo is the deliverable, not just the final report.

Required repo structure:
```
/report/
  /executive-summary.md       2-3 page synthesis for the maintainer
  /backlog-strategy.md        Recommended merge order and rationale
  /contributor-notes.md       Per-contributor patterns and feedback themes
  /project-health.md          What the PR backlog reveals about the project
/prs/
  /pr-{number}/
    /verdict.md               Merge / revise / reject + reasoning
    /summary.md               What the PR claims to do, in your words
    /review.md                Line-by-line review notes
    /tests/                   Any tests you ran, with results
    /diff-analysis.md         What the diff actually changes vs what it claims
    /interactions.md          Conflicts/dependencies with other open PRs
    /trace.md                 Pointers back to commits, files, lines reviewed
/testing/
  /environments/              Dockerfiles or scripts for each test environment used
  /hardware/                  Notes on GPU/hardware tests, what was tested where
  /reproductions/             Scripts that reproduce any bug or behavior claimed
  /baseline.md                The pre-PR baseline state you tested against
/analysis/
  /dependency-graph.md        Which PRs depend on, conflict with, or duplicate which
  /risk-matrix.md             Risk scoring methodology and per-PR scores
  /surface-area.md            What subsystems each PR touches
  /scripts/                   Any analysis scripts (PR clustering, diff stats, etc.)
/research/
  /notes/                     Working notes, dated, one file per session
  /questions.md               Questions you had and how you resolved them
  /dead-ends.md               Investigations that didn't pan out, with why
  /upstream-context.md        Relevant DreamServer architecture, pulled from main
/decisions/                   ADR-style records for non-obvious choices
/sources.md                   External content fetched (docs, issues, related repos), URLs + SHAs
/tool-log.md                  Every tool call in order, with one-line justification
README.md                     How to navigate the repo, in what order to read it
```

Rules of the road:

- Every verdict must be traceable. A reject verdict on PR #47 must point to specific lines in the diff, specific test results, or specific architectural concerns documented in /research/upstream-context.md. "This looks wrong" is not a review; "this allocates a CUDA context per request which conflicts with the singleton pattern established in installer/gpu.py:142" is.
- Run the code. For every PR that changes code paths reachable by tests, you run those tests on the baseline and on the PR branch, and you record both results in /prs/pr-{number}/tests/. For PRs that touch installer logic, you run the installer in a clean container. For PRs that touch GPU code paths, you note whether you tested on hardware, simulated, or skipped, and why. Skipping is allowed; skipping silently is not.
- Reproduce claimed bugs. If a PR claims to fix a bug, your job is to reproduce the bug on main first, then verify the PR fixes it. The reproduction script goes in /testing/reproductions/. If you can't reproduce the bug, the verdict reflects that.
- Cross-PR analysis is mandatory. With 75 open PRs there will be conflicts, duplicates, and dependencies. The dependency graph in /analysis/dependency-graph.md must identify every pair of PRs that touch overlapping code, every PR that supersedes another, and every chain where merging A enables or breaks B. This is the single highest-value artifact for the maintainer.
- Risk scoring is explicit. Every PR gets a risk score along documented axes — surface area touched, test coverage of affected code, reversibility, blast radius if wrong, contributor track record. The methodology lives in /analysis/risk-matrix.md as an ADR. No black-box scoring.
- Contributor context matters. Bounty PRs from Upwork/Freelancer applicants have different signal than PRs from established contributors (Youness on multi-GPU, Glexy on installer hardening, Yasin on Mac/full stack). Track this in /report/contributor-notes.md. A first-PR contributor doing something subtle in installer code warrants more scrutiny than a known contributor extending their own subsystem.
- Honor the bounty structure. PRs were submitted under a Small/Medium/Large bounty system ($40/$150/$400). The verdict file should note which tier the PR claims and whether the actual change matches that tier. A "Large" bounty PR that only touches three lines is a flag; a "Small" bounty PR that refactors core installer logic is a different kind of flag.
- Distinguish the four reject reasons. Reject for correctness (the code is wrong), fit (the code is fine but doesn't belong in DreamServer), quality (the approach is salvageable but the execution isn't), or redundancy (another open PR does this better). The verdict file states which.
- Distinguish the three revise reasons. Revise for small fixes (clean it up and merge), missing tests (works but unverified), or architectural rework (right idea, wrong approach). The verdict states which and includes specific revision guidance.
- Surface AMD-relevant changes. Given the AMD developer program partnership, any PR touching ROCm, AMD GPU paths, or anything that could regress AMD compatibility gets called out explicitly in /report/executive-summary.md. Regressing AMD support is a different kind of cost than regressing some other path.
- Dead-ends matter. If you spent two hours convinced PR #23 had a subtle race condition and turned out to be wrong, write it up in dead-ends.md. The reasoning that didn't make the verdict is where you can see how the auditor actually thinks.
- The questions log. Every time you hit something you weren't sure about — "is this the intended behavior of the SearXNG container or a workaround?" — write the question down. Then write how you resolved it, or that you didn't and what assumption you made.
- ADRs for non-obvious choices. Why you chose to test installer PRs in Ubuntu 22.04 instead of 24.04. Why you scored "blast radius" the way you did. Why you treated documentation-only PRs as auto-approve or didn't. These choices are where audit value lives.
- The executive summary. Maximum 3 pages. Lead with the headline: how many merge-now, how many revise, how many reject, how many need maintainer judgment. Then the three highest-priority merges, the three highest-risk situations, the dependency hot spots, and any cross-PR patterns worth a strategic decision (e.g., "12 PRs are touching the installer entry point; before merging any of them, decide on the entry-point refactor that 4 of them are independently proposing").
- Commit messages explain why. "Review PR #34" is bad. "Mark PR #34 as superseded by #51 after confirming both implement Strix Halo detection but #51 also handles the USB4 fallback path #34 misses" is good.
- Reproducibility. A maintainer should be able to clone the audit repo, pick any verdict, and rerun the exact tests that produced it. Test scripts live in the repo, not just in your head.

When you're done, the final commit tags a release. A maintainer with 90 minutes should be able to clone the repo, read the executive summary, scan the dependency graph, and confidently start merging the recommended set in the recommended order.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit progress frequently as you go. Do not ask for clarification — make reasonable choices and document them in /decisions/.
