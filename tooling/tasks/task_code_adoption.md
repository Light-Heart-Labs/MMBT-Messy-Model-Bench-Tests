You have access to an unmaintained Python codebase, mounted read-only at `/input/repo/`. It's a small CLI tool called **logalyzer** for analyzing web server access logs. The previous maintainer left it in a state that "mostly works" but has accumulated issues across multiple categories — bugs that surface as failing tests, deprecated patterns that will break on modern Python, performance problems, dead code, security smells, documentation that lies about features, and gaps in test coverage.

You have a fresh Linux VM with internet, a Python 3.11 environment, standard CLI tools, git, and the toolchain for testing and quality checks (pytest, pytest-cov, ruff). No time limit, no tool call limit, no output length limit.

Your task: **adopt this codebase and stabilize it.** Understand what's there, fix what's broken, modernize what's deprecated, document what isn't, decide what to keep and what to delete. The repo at the end should be what you'd be proud to hand to a new engineer joining the team.

Everything you produce must live in a new git repository at `/workspace/`. Commit early, commit often, write real commit messages explaining *why* not *what*. The repo is the deliverable.

## Required repo structure

```
/audit/
  triage.md             Every issue you found, ranked by severity × category, with disposition
  before-after.md       Hard metrics: test pass rate, line coverage %, ruff issue count, benchmark seconds — all measured before you started and after you finished
/fixes/                 (Optional dir for any throw-away repro scripts you used while debugging)
/logalyzer/             The actual package, with your fixes applied
/tests/                 Test suite. Augmented from the starter — should cover any new claims you make and any modules that had 0% coverage
/benchmarks/            Benchmark harness. Augment if helpful; preserve the starter's bench.py interface so before/after numbers compare cleanly
/architecture/          ADRs (Architecture Decision Records) for non-obvious structural choices: what to delete, what to keep, naming, module boundaries
/research/
  notes/                Working notes, dated, one file per investigation session
  questions.md          Things you weren't sure about and how you resolved them (or that you didn't, and why)
  dead-ends.md          Fixes you attempted and reverted, with why. Bonus for non-trivial dead-ends — boards trust analysts who show their work.
/decisions/             Numbered ADR-style records for individual choices that don't rise to architectural scope (e.g. "replaced eval() with X — alternatives considered, why X")
CHANGELOG.md            User-facing summary of what changed
README.md               Updated. Including a "what was wrong, what got fixed" section. Lies in the original README must be removed or made true.
```

## Rules of the road

- **Every claim ("this was a bug because…") must be backed by a failing test or a measurement.** No vibes. If you say "this was an O(n²) bottleneck", you must show the benchmark number that proves it.
- **Every fix is its own atomic commit** with a real "why" message. "Switch IP allowlist from list to set after profiling showed 80% of `pred()` time was spent in linear search" is good. "Fix performance" is bad.
- **Triage must be ranked.** Not all issues need fixing. Document what you deferred and why. A focused diff that fixes the important things is better than a sprawling diff that touches everything.
- **Dead-ends matter.** If you spent time on a fix that didn't pan out, write it up. The reasoning that didn't make the final commit is often the most informative artifact.
- **The benchmark numbers must be reproducible from a script.** A board member should be able to clone the repo, run `python benchmarks/bench.py`, and reproduce your "after" number within ~10%.
- **Test pass rate must go up, never down.** Coverage % must go up. Ruff issue count must go down. If you make a change that worsens any of these, you need a documented justification in `/decisions/`.
- **Commit messages explain why.** "Replace `from collections import Iterable` with `collections.abc.Iterable` (the former was removed in Python 3.10; this prevented module import on modern interpreters)" is good. "Fix import" is bad.
- **The starter's git history matters too.** Use `git log --git-dir=/input/repo/.git` to see what came before. Read the previous maintainer's commit messages — they may explain why decisions were made the way they were.

## Concrete deliverables (must be present)

- `/audit/triage.md` — all issues catalogued, with severity (low/medium/high/critical) × category × disposition (fixed / deferred / wontfix). Bonus for finding issues that aren't surfaced by failing tests (e.g. silent data corruption, security smells, deprecated APIs).
- `/audit/before-after.md` — a numeric table: pytest passed/total, coverage %, ruff issues, benchmark seconds — measured against the *starter* baseline AND your *final* repo. Show your working: how you measured each, with the exact commands.
- `/CHANGELOG.md` — what changed, in user-facing terms. One section per release-worthy change.
- `/README.md` — updated. Old lies must be either removed or made true (if you implemented a missing feature, document it; if you didn't, delete the false claim).
- At least one ADR in `/architecture/` — for any non-trivial structural choice (e.g. deleting an unused module, splitting/merging files, renaming the package).
- At least 2 entries in `/research/dead-ends.md` — fixes attempted and reverted. If you genuinely had no dead ends, that's worth noting but is unusual.
- A `/research/questions.md` log with at least 5 entries — things you investigated and resolved (or couldn't resolve).
- The fixed package at `/logalyzer/`. Test suite at `/tests/` — augmented from the starter where coverage was 0%.

## Hints (read once, then forget)

- The starter has a deliberate mix of: real bugs (failing tests will surface them), deprecated patterns, performance issues, dead code, doc lies, and a security smell. Don't assume the failing tests are the *only* problems — some issues won't have any test pinning them, and a good triage finds those too.
- The benchmark on a 50 MB log is a strong signal of one of the issues. On the starter it's measurably slow. After a streaming-style fix, it should be at least 5× faster.
- The original maintainer left some functions and a whole module that may not be used anywhere. Decide what to do with them. Either decision is fine if documented.
- Modern Python (3.10+) has moved some abstract base classes from `collections` to `collections.abc`. The starter doesn't reflect this.

When you're done, the final commit should tag a release (e.g. `v0.3.0`). A new engineer with no context should be able to clone the repo, read the README, and within 15 minutes understand both what changed and how to verify any improvement claim.

Begin. Work autonomously in `/workspace/`. Use the `bash`, `write_file`, `read_file`, and `done` tools. Commit your progress frequently. Do not ask for clarification — make reasonable choices and document them in `/decisions/` and `/architecture/`.
