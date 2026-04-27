# Dead Ends

## Investigation 1: GitHub CLI Authentication

**Hypothesis:** The `gh` CLI would work for fetching PR data without authentication.
**Result:** Failed — `gh auth login` required. The unauthenticated GitHub API (via curl) works but is rate-limited to 60 req/hr.
**Resolution:** Used curl to fetch PR list once, then used `git fetch` with individual PR SHAs to get diffs locally.

## Investigation 2: Bulk PR Fetch via Git

**Hypothesis:** `git fetch origin 'pull/*/head'` would fetch all PRs in one command.
**Result:** Failed — git doesn't support wildcard refspecs in fetch.
**Resolution:** Fetched each PR individually using its SHA: `git fetch origin <sha>:refs/remotes/pull/<num>`.

## Investigation 3: PR #351 vs #364 Distinction

**Hypothesis:** PRs #351 and #364 might have different scopes despite similar file counts.
**Result:** After examining both diffs, they are near-duplicates — both add the same extensions library services, tests, and documentation. PR #364 has slightly broader scope (dashboard API settings, voice runtime, diagnostics).
**Resolution:** #351 is superseded by #364.

## Investigation 4: Mobile Support Feasibility

**Hypothesis:** PR #961's mobile support (Termux/a-Shell) might be feasible as a CPU-only mode.
**Result:** The project's architecture requires GPU acceleration for llama-server, ComfyUI, and other services. CPU-only mode exists but is not the primary use case. Mobile devices lack the GPU resources for meaningful inference.
**Resolution:** Rejected for fit — mobile support is out of scope for the current roadmap.

## Investigation 5: AMD Multi-GPU Dependencies

**Hypothesis:** PR #750 (AMD Multi-GPU) might depend on other open PRs.
**Result:** No dependencies found. PR #750 is standalone. PR #1032 (depends_on mirror) is compatible but not a dependency.
**Resolution:** #750 can be merged independently, but needs AMD partnership sign-off.
