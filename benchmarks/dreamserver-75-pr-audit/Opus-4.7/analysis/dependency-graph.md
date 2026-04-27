# Dependency Graph

The single highest-value artifact in this audit. With 63 of 75 PRs from a
single contributor (Yasin) doing a methodical sweep, the question is no
longer "should we merge each PR" — it's "in what order, and which can be
collapsed?".

This file maps three relationships:

- **Hard dependency**: A requires B's change to be live first
- **Soft conflict**: A and B touch overlapping lines; merge order matters
- **Supersession / collapse**: A and B are essentially the same work
- **Logical chain**: A and B together form a coherent unit and should land as a stack

Notation: `A → B` means "merge A first, then B will rebase cleanly".
File-level overlaps are listed in `analysis/file_overlaps.json`.

## Cluster 1 — `dream-cli` (15 PRs)

The 45K-line Bash CLI gets touched by 15 different PRs. The right framing for
the maintainer is:

> **Recommendation: ask Yasin to consolidate these into a single
> `cli-cleanup-q2-2026` stack with explicit ordering.** Merging
> 15 individual PRs against the same monolithic file creates 14 conflict
> resolutions, all of them his to redo. He's already doing the work; what's
> missing is a stack discipline.

If consolidation isn't possible, the suggested merge order based on logical
dependency:

```
#1006 (log → stderr)         # foundation; downstream PRs assume log() to stderr
   ↓
#1007 (quote tmpdir in trap) # narrow bugfix
   ↓
#1008 (pipefail grep guard)  # narrow bugfix
   ↓
#993  (color / NO_COLOR)     # UX, depends on log output channel
   ↓
#994  (secret masking + bash 4 macOS) # security touching
   ↓
#997  (preflight 'dream shell')
   ↓
#1000 (--json flag on list/status)
   ↓
#999  (Apple Silicon gpu/doctor)
   ↓
#998  [DRAFT] (pipefail + LLM failure surfacing + exit codes)
   ↓
#1002 [DRAFT] (set -u + guards)
   ↓
#1011 [DRAFT] (bash 3.2 declare -A guards)
   ↓
#1016 [DRAFT] (Apple GPU output polish)
   ↓
#1018 [DRAFT] (BATS regression shield)
   ↓
#1020 [DRAFT] (Apple Silicon GPU mock coverage)
```

`#750` (AMD Multi-GPU) also touches `dream-cli` but is a separate scope; it
wants to land before or after the cleanup sweep, not interleaved.

**Why this order:**
- `#1006` first because it changes log channels — every downstream PR
  inherits that behavior.
- Bug fixes (`#1007`, `#1008`) before features (`#1000`, `#999`) because
  features can be regressed by the bugs.
- Drafts last; they're not maintainer-ready signal yet.
- `#1018` and `#1020` are test additions — they should be the *last* thing
  merged, after the behavior they assert is final.

## Cluster 2 — `bin/dream-host-agent.py` (10 PRs)

Suggested merge order:

```
#988  (loopback bind: llama-server + host agent)   # SECURITY, lands first
   ↓
#1021 (start extension sidecars during install)    # install flow
   ↓
#1030 (install flow: hooks + bind anchor + verify) # install flow polish
   ↓
#1050 (block non-POSIX INSTALL_DIR + Docker share) # install flow preflight
   ↓
#1057 (runtime hygiene — narrow pull, etc.)        # runtime
   ↓
#1035 (openclaw recreate on install)               # runtime
   ↓
#1040 [DRAFT] (langfuse chown)                     # runtime, when ready
   ↓
#1045 (route extension config sync through agent)  # NEW capability
   ↓
#1039 [DRAFT] (retry install failure through hook) # depends on #1030
   ↓
#1017 [DRAFT] (docs: Linux fallback post-#988)     # docs, lands when #988 is in
```

**Hard dependencies in this cluster:**
- `#1017` is **literally** documented as "post-#988" — the title says it.
  Cannot merge #1017 before #988.
- `#1039` (retry-install) requires the install flow refactor in `#1030`; the
  retry path the draft adds calls into the post-#1030 hook structure.
- `#1045` (config sync route) introduces a new agent capability; merging it
  before the install flow stabilizes (`#1021`–`#1030`–`#1050`) means
  rebasing #1045 against three sets of changes.

## Cluster 3 — `dashboard-api/routers/extensions.py` (8 PRs)

```
#1022 (async hygiene)                              # foundation, no conflicts
   ↓
#1054 (require deployable compose.yaml)            # schema tightening
   ↓
#1044 (accept ${VAR:-127.0.0.1} in scan)           # scan logic
   ↓
#1056 (catalog timeout + GPU passthrough scan)     # feature batch
   ↓
#1038 (honor pre_start return)                     # behavior
   ↓
#1045 (route extension config sync via host-agent) # cross-cluster
   ↓
#1037 [DRAFT] (UI: expandable error + poll)        # UI, when ready
   ↓
#1039 [DRAFT] (retry through hook)                 # cross-cluster
```

`#1045` and `#1039` appear in both Cluster 2 and Cluster 3 — they're the
cross-cluster bridges between host-agent and dashboard-api work.

## Cluster 4 — Setup-wizard (4 PRs, all touch the same 6 files)

PRs **#1003 #1015 #1018 #1019** all touch `Extensions.jsx`, `SetupWizard.jsx`,
`TemplatePicker.jsx`, `templates.js`, `setup.py`, and `dream-test-functional.sh`.

Reading the titles, this is a **single intentional stack**:

```
#1003 (sentinel-based success detection)           # the substantive change
   ↓
#1015 [DRAFT] (defensive picker fixes)             # depth, depends on #1003
   ↓
#1019 [DRAFT] (sentinel exception path + tests)    # depth, depends on #1003
   ↓
#1018 [DRAFT] (BATS regression shield)             # last, locks the contract
```

These should ship as one merge train. `#1003` is verdict-eligible now;
the three drafts should land *together* once Yasin marks them ready.

## Cluster 5 — `.env.schema.json` / `.env.example` (6 PRs each)

Different PRs add different env keys. Verifying disjointness:

| PR | Schema keys touched | Example keys touched |
|----|---------------------|----------------------|
| #750 | AMD multi-GPU vars | AMD multi-GPU vars |
| #973 | — | post-merge sync (50+ keys) |
| #988 | loopback bind | loopback bind |
| #992 | — | OPENCLAW_TOKEN placeholder |
| #994 | secret-marking | — |
| #1010 | provider API keys → secret | — |
| #1013 | — | DREAM_AGENT_KEY |
| #1017 | docs only | docs only |
| #1018 | test additions | — |

All six PRs touching `.env.schema.json` add disjoint keys (different
features). Same with `.env.example`. **No semantic conflict** — only
textual conflicts that resolve trivially.

`#1010` (mark provider API keys as secret) is a metadata flip on existing
keys; if `#994` or `#988` add new secret keys, they should follow `#1010`'s
pattern. Otherwise these merge cleanly in any order.

## Cluster 6 — Cross-platform installer entry points (5 PRs)

PRs that touch `installers/macos/install-macos.sh` AND
`installers/windows/install-windows.ps1`:

| PR | Concern |
|----|---------|
| #988 | Bind addresses (security) — **must land first** |
| #1005 | macOS install-time polish |
| #1017 | Docs sync |
| #1026 | Pre-mark setup-wizard complete |
| #1050 | INSTALL_DIR POSIX + Docker sharing |

These PRs don't all touch the same lines, but they all change the install
flow. Merge order: #988 first (security), then #1005, #1026, #1050 in any
order, then #1017 (docs).

## Hard dependency: `#1017` → `#988`

PR #1017 (Yasin) is titled "docs(security): Linux host-agent fallback is
127.0.0.1 post-#988". The PR is **explicitly written assuming #988 is
merged**. If you merge #1017 before #988, the docs claim a behavior that
the code doesn't yet have.

**Recommendation:** Block #1017 until #988 lands. Encode this in the
merge-order plan in `report/backlog-strategy.md`.

## Soft supersession / consolidation candidates

| Group | PRs | Reason |
|-------|-----|--------|
| Voice/Apple-silicon dream-cli polish | #999, #1016 | Same author, same area, both Apple-silicon CLI polish — could collapse |
| Setup wizard | #1003 + 3 drafts | Should ship as one train |
| Lang fuse install | #1040 + #1052 (draft tests) | Test-and-fix pair |
| Extension manifest mirror | #1032 + #1033 + #1034 | All "fix(extensions): X" small fixes — could batch into a single sweep PR |

## CONFLICTING (mergeable=false) PRs

| PR | Author | Why it's stuck |
|----|--------|----------------|
| #351 | reo0603 | Last update 2026-03-17. Branch is 40+ commits behind main; rebase needed. CI also red on 4 jobs. |
| #364 | championVisionAI | Same — March-era PR, drifted significantly. |

These are the **two oldest open PRs** in the queue. They've been sitting
since mid-March while ~70 newer PRs landed adjacent to their files.
Rebasing both is non-trivial. Recommend: ask the authors if they still
want the work in; if yes, give a deadline; if no, close.

## Cross-PR conflict matrix (concise summary)

The following pairs textually conflict (both touch the same file), but
**don't semantically conflict** (changes are local enough to merge by hand):

| File | Pairs |
|------|-------|
| `dream-cli` | every (#993,#994,#997,#998,#999,#1000,#1002,#1006,#1007,#1008,#1011,#1016,#1018,#1020) — 14 pairwise pairs that would textually conflict |
| `dream-host-agent.py` | #988-vs-others, then sequential through #1057 |
| `routers/extensions.py` | #1022-vs-#1037-vs-#1038-vs-#1044-vs-#1045-vs-#1054-vs-#1056 |
| `tests/test_extensions.py` | mirrors the routers/extensions.py pattern |

The maintainer should expect to resolve textual conflicts when merging in
the order recommended in `report/backlog-strategy.md` — they will be
mostly mechanical (insertion order in Python dicts, append-or-prepend in
Bash arrays).

## What's NOT in this graph (deliberately)

- Cross-PR conflicts where the second PR is a draft and won't merge soon —
  drafts can be re-stacked after the non-draft set lands.
- Conflicts mediated by CI (e.g., two PRs both adding to a manifest catalog
  — the catalog-checker auto-detects). These auto-resolve.
- "Aesthetic" overlaps (two PRs both adding a comment to the same file).
  Trivial to resolve; not worth the diagram space.
