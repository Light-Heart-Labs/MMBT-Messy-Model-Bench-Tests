# Backlog Strategy

The recommended merge sequence to clear the 75-PR backlog with minimum
maintainer time and maximum signal reliability. Pairs with
[`analysis/dependency-graph.md`](../analysis/dependency-graph.md) — the
graph identifies dependencies; this file is the prescribed order.

The structure is in **waves**. A wave can be merged in one sitting; the
next wave assumes the previous wave is in.

## Wave 0 — unblock CI (~5 minutes)

| Step | Action |
|------|--------|
| 1 | Cherry-pick `tests/bats-tests/docker-phase.bats:100` fix from PR #750 to a separate trivial PR. Merge to `main`. |
| 2 | Re-run CI on every open PR (or wait 24h for the cron). 72 of 75 PRs become CI-green-ish for `integration-smoke`. |

This is the highest-ROI move in the entire audit. It costs nothing and
makes every subsequent merge readable.

## Wave 1 — security and stability foundations (~30 minutes review + merge)

In order:

| # | PR | Why this position |
|---|----|-------------------|
| 1 | **#988** (loopback bind) | Hard dependency for #1017. Closes default-permissive bind in line with `SECURITY_AUDIT.md` H3 policy. |
| 2 | **#1050** (FS preflight) | Same security class as #988. Blocks installs that would silently leak `.env` secrets via FAT/exFAT/NTFS. |

After Wave 1, you can credibly claim "DreamServer's default install is
secure-by-default" without an asterisk.

## Wave 2 — high-leverage features (~45 minutes)

| # | PR | Why this position |
|---|----|-------------------|
| 3 | **#1042** (support bundle generator, Dmytro) | High-leverage diagnostic tool. Pays back on every future bug report. No cross-PR conflicts. |
| 4 | **#1003** (setup-wizard sentinel, Yasin) | Fixes a real first-time-user UX bug — wizard greenlit users on failed diagnostic. Substantive Python + JSX + shell layer. |
| 5 | **#1043** (custom-menu opt-out fix, Y) | Two-bug fix: Custom-mode "n" answers were silently no-ops; compose-disable sync only handled 3 of 8 services. |

Wave 2 ships three user-facing improvements that don't conflict with
anything else.

## Wave 3 — host-agent stack (Yasin) (~1 hour, review-heavy)

PR cluster all touching `bin/dream-host-agent.py`. Merge in this order
(per [`analysis/dependency-graph.md`](../analysis/dependency-graph.md)
Cluster 2):

| # | PR | What it does |
|---|----|--------------|
| 6 | **#1021** | Start extension sidecars during install |
| 7 | **#1030** | Install flow: built-in hooks, bind-mount anchor, post-up state verify |
| 8 | **#1057** | Runtime hygiene: narrow pull, surface failures, normalize bind volumes |
| 9 | **#1035** | Trigger open-webui recreate on openclaw install; simplify volume layout |
| 10 | **#1045** | Route extension config sync through host agent |
| 11 | **#1017** | Docs sync — explicitly post-#988 |

Wave-3 PRs that are still in **draft** at the time you're merging:
**#1039** (retry through hook), **#1040** (langfuse chown). Hold these
until Yasin marks ready, then they fold into the same train order.

## Wave 4 — dream-cli stack (Yasin) (~1.5 hours, **stack consolidation strongly recommended**)

This is the cluster where the maintainer-level conversation about stack
discipline pays off. **Two paths**:

### Path A: ask Yasin to consolidate

> "Yasin — 14 of your open PRs touch dream-cli. Could you re-stack
> these as `cli-cleanup-q2-2026` parent + dependent children, in the
> order suggested in this audit? It's one merge train for me, one
> rebase for you, instead of 14 individual ones."

If yes, you merge **one stack** end-to-end. Time: ~30 minutes review
of the consolidated PR.

### Path B: merge individually in dependency-graph order

If Yasin can't consolidate, the order from
[`analysis/dependency-graph.md`](../analysis/dependency-graph.md)
Cluster 1:

| # | PR | What it does | Tier |
|---|----|--------------|------|
| 12 | **#750** | AMD Multi-GPU (after CHANGES_REQUESTED resolved + hardware test) | Medium-Big |
| 13 | **#1006** | Route log() and warn() to stderr | Trivial |
| 14 | **#1007** | Double-quote tmpdir in gpu_reassign RETURN trap | Trivial |
| 15 | **#1008** | Guard .env grep pipelines against pipefail kill | Trivial |
| 16 | **#993** | Color/escape + table-separator + NO_COLOR | Trivial |
| 17 | **#994** | Schema-driven secret masking + macOS Bash 4 | Trivial |
| 18 | **#997** | Pre-validate `dream shell` service | Trivial |
| 19 | **#1000** | --json flag on list/status | Trivial |
| 20 | **#999** | Apple Silicon coverage for `gpu`/`doctor` | Low |

Then drafts (#998, #1002, #1011, #1016, #1018, #1020) once they
graduate from draft.

Time for Path B: 14 individual merges with 13 rebase-conflicts. ~3-4
hours of maintainer time.

**Recommendation:** Path A. The conversation is short, the savings are
huge, and Yasin will likely appreciate the workflow improvement.

## Wave 5 — extensions / dashboard-api stack (Yasin) (~1 hour)

Cluster touching `routers/extensions.py` and the React dashboard
extensions page. From
[`analysis/dependency-graph.md`](../analysis/dependency-graph.md)
Cluster 3:

| # | PR | What it does |
|---|----|--------------|
| 21 | **#1022** | Async hygiene in routers/extensions.py |
| 22 | **#1054** | Require deployable compose.yaml to mark extension installable |
| 23 | **#1044** | Accept `${VAR:-127.0.0.1}` in compose port-binding scan |
| 24 | **#1056** | Catalog timeout, orphaned whitelist, GPU passthrough scan, health_port |
| 25 | **#1038** | Honor pre_start return, surface post_start failure |
| 26 | **#1037** | Expandable error text + poll recovery on extensions page (when out of draft) |

## Wave 6 — extension-specific polish (~30 minutes)

Disjoint small fixes to specific extension manifests / compose files.
Merge in any order — they don't interact:

#1027, #1028, #1029, #1032, #1033, #1034, #1036, #1046, #1047, #1049, #1051, #1052, #1053.

Most are 1–10-line shellcheck/SIGPIPE/whitespace fixes. Some are tests.
Worth batching into a single review session.

## Wave 7 — Apple Silicon polish (~20 minutes)

PRs touching macOS / Apple Silicon paths. None regress AMD or NVIDIA:

#1004, #1005, #1013, #1016, #1025, #1048.

## Wave 8 — Windows polish (~10 minutes)

#996 (DREAM_AGENT_KEY in installer env-generator.ps1), #1012 (trim dead
fields from New-DreamEnv).

## Wave 9 — docs and chore (~10 minutes)

#973 (docs sync after 50+ merged PRs), #966 (Windows/macOS docs),
#1010 (mark provider API keys as secret in schema), #1014 (test repair),
#992 (OPENCLAW_TOKEN placeholder), #1024 (COMPOSE_FLAGS array
expansion), #1009 (image-gen default off on non-GPU), #974 (use
$DOCKER_CMD for DreamForge restart), #1023 (SIGPIPE-safe first-line),
#1055 (dashboard-api dev-workflow guide).

## Wave 10 — dependabot (~5 minutes)

#990 (actions/github-script bump), #991 (claude-code-action bump).
Auto-merge candidates after the BATS fix lands.

## Wave 11 — HOLDs (the conversations)

In parallel with the merge work above, three conversations:

| PR | Conversation |
|----|--------------|
| **#961** | gabsprogrammer (mobile). "Mobile isn't on our short-term roadmap…" or "we're interested, can you split into 3 stages?" |
| **#983** | Arifuzzaman (Vast.ai p2p-gpu). "Does cloud-deploy *recipe* fit our 'no cloud' positioning?" — answer one way or the other. |
| **#364** | championVisionAI (March-era stale). "Are you up for rebasing?" — give 2-week deadline; if no response, close politely. |
| **#351** | reo0603 (March-era input-validation tests). Same shape as #364. |

## What you should NOT do

- **Don't merge #1017 before #988.** It's literally titled "post-#988"
  and the docs claim a behavior #988 introduces.
- **Don't bundle the BATS fix into another large feature merge.** Pull
  it out as a tiny standalone PR — that one-line fix unblocks 72 PRs'
  CI signals. Bundling it into #750 (AMD) gates 72 PRs on AMD review.
- **Don't merge any of #1015 / #1018 / #1019 before #1003.** They all
  depend on the sentinel mechanism #1003 introduces.
- **Don't auto-merge #364 or #351** even if a rebase makes them
  technically mergeable. Their staleness is the signal — confirm with
  the contributor first.

## Total time budget

| Wave | Time | Cumulative |
|------|------|-----------|
| 0 (BATS fix) | 5 min | 5 min |
| 1 (security) | 30 min | 35 min |
| 2 (high-leverage) | 45 min | 1h 20min |
| 3 (host-agent) | 1h | 2h 20min |
| 4 (dream-cli, Path A) | 30 min | 2h 50min |
| 4 (dream-cli, Path B) | +3h | 5h 50min |
| 5 (extensions) | 1h | 3h 50min / 6h 50min |
| 6 (extension polish batch) | 30 min | 4h 20min / 7h 20min |
| 7 (macOS polish) | 20 min | 4h 40min / 7h 40min |
| 8 (Windows polish) | 10 min | 4h 50min / 7h 50min |
| 9 (docs/chore) | 10 min | 5h / 8h |
| 10 (dependabot) | 5 min | 5h 5min / 8h 5min |
| 11 (HOLD conversations) | parallel | — |

**~5 hours of focused work** if Wave 4 takes Path A (consolidated
stack). **~8 hours** if Wave 4 takes Path B (individual merges).
The difference is one conversation with Yasin about stack discipline.
