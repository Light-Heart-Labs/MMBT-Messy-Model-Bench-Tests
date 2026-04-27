# PR #983 — Verdict

> **Title:** feat(resources): add p2p-gpu deploy toolkit for Vast.ai GPU instances
> **Author:** [Arifuzzamanjoy](https://github.com/Arifuzzamanjoy) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/p2p-gpu-hints-vastai-guard`
> **Diff:** +5,054 / -165 across 33 file(s) · **Risk tier: Medium (score 11/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/983

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 4 | 33 files, ~5K added lines, full pipeline of phases + libs + subcommands |
| B — Test coverage | 4 | Auditor found no test files in the diff for the new pipeline |
| C — Reversibility | 0 | Lives entirely under `resources/p2p-gpu/`; `rm -rf resources/p2p-gpu/` reverts |
| D — Blast radius | 0 | Changes nothing in the core install path. `resources/` is documented as cookbooks/extras (per `research/upstream-context.md` §1) |
| E — Contributor | 3 | Arifuzzamanjoy: bounty contributor, prior small PR (#716). 5K-line PR is a step up |
| **Total** | **11** | **Medium** |

## Verdict

**HOLD — needs maintainer judgment on positioning.**

This is the cleanest "fit" question in the queue. The code is **structurally
isolated** — every file lives under `resources/p2p-gpu/`, the directory
documented as cookbooks/recipes/dev tools, not core. It cannot regress
any user's install. Even the `.github/workflows/p2p-gpu.yml` is new and
gated to its own paths.

But the **positioning question is real**:

> DreamServer's tagline (README + `dreamserver.ai`):
> "**Local AI anywhere, for everyone — LLM inference, chat UI, voice,
> agents, workflows, RAG, and image generation. No cloud, no
> subscriptions.**"

PR #983 adds tooling to deploy DreamServer onto **Vast.ai cloud GPU
instances**. That is, by definition, cloud. A user following the
`resources/p2p-gpu/` recipe ends up running DreamServer's stack on a
GPU they're renting from a third party with their data passing through
Vast.ai infrastructure.

There are reasonable readings on both sides:

- **Pro-merge ("recipes ≠ product")**: `resources/` is the recipe
  directory. Recipes can target *any* deployment target. A
  cookbook-quality "here's how to deploy DreamServer on a Vast.ai box"
  is no different from "here's how to deploy on a 7900-XTX desktop."
  The product remains "no cloud" — the recipe is just one of many ways
  to run the product.
- **Pro-reject ("the messaging matters")**: The website headline
  promises "no cloud." A first-time visitor seeing a Vast.ai recipe in
  the official repo will reasonably conclude the product *is* cloud-
  capable. The brand loses one of its sharpest selling points.

The auditor is **not** the right person to make this call. It's a
maintainer-level marketing/positioning decision.

## What to do once a position is taken

### If the maintainer says YES (merge):

- **Add a positioning note** to `resources/p2p-gpu/README.md`:
  *"This is a recipe for running DreamServer on Vast.ai GPU rentals.
  DreamServer itself runs entirely on the host you control. Use this
  recipe at your own discretion; the privacy properties of your stack
  are bounded by the trust model of your GPU provider."*
- **Audit secrets handling** in the recipe: a Vast.ai instance is
  short-lived; anything written to `.env` goes away with it, but
  anything *exfiltrated* over the network is gone permanently. This
  audit didn't review the 5K lines for `curl | bash` patterns, plain-
  text token logs, or telemetry.
- **Consider revising title from `feat(resources)` to something
  cookbook-flavored** like `cookbook: Vast.ai deployment recipe` —
  framing matters.

### If the maintainer says NO (reject — fit):

- The PR is well-structured. The reject conversation should
  acknowledge the work and explain the positioning constraint:
  *"Thanks for the substantial work. We're keeping the
  positioning crisp on 'local-only' and don't want a cloud-deploy
  recipe in the official repo. Please consider publishing this as a
  separate companion repo — happy to link to it from the docs."*
- This is the right shape because the contributor invested time and
  the work is salvageable; it just doesn't fit the brand.

## Findings (if direction is merge)

The auditor did not exhaustively review the 5K-line diff. Spot-checks:

### ★★ — Phase pipeline mirrors the main installer's structure

`resources/p2p-gpu/phases/00..12-*` follows the same numeric-ordered
sequential phase pattern as `dream-server/installers/phases/01..13-*`.
Good architectural mirroring; eases reviewer cognitive load.

### ★★ — `lib/` directory under `resources/p2p-gpu/lib/`

`compatibility.sh, constants.sh, environment.sh, gpu-topology.sh,
logging.sh, models.sh, networking.sh, permissions.sh, services.sh`.
This mirrors the `installers/lib/` purity convention. The auditor did
not verify each lib is actually pure (no I/O at top level). Recommend a
sample inspection before merge.

### ★ — Dedicated CI workflow `.github/workflows/p2p-gpu.yml`

Doesn't run on every commit (presumably scoped to `paths: resources/p2p-gpu/**`).
Sane.

### ★ — No tests in the diff

Auditor grep'd for `test/` and `_test.sh` patterns in the file list and
found nothing under `resources/p2p-gpu/`. For a 5K-line bash pipeline
that runs on cloud GPUs, this is a real gap. **REVISE — missing tests**
would be the secondary verdict if the maintainer says merge.

### Convention adherence

Cannot be fully assessed without reading more lines. The structural
shape (phases + lib) suggests Arifuzzamanjoy modeled it on the project's
existing patterns.

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #716 (Arifuzzamanjoy) | Same author. Tiny PR against `resources/dev`. Different scope. |
| Everything else | No overlap — `resources/p2p-gpu/` is a new directory tree |

No conflicts, no dependencies. The merge decision rests entirely on
maintainer judgment about positioning.

## Trace

- 33 files, all under `resources/p2p-gpu/` (32) and `.github/workflows/` (1)
- Pipeline structure: 13 phases + 5 subcommands + 9 lib files
- Open: 2026-04-18; one push since
- The "no cloud" positioning lives in: `README.md` (root), `dream-server/README.md`, marketing on `dreamserver.ai`
