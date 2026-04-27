# PR #983 — Diff analysis

What the diff actually changes, vs what the title/body claim.

## Files touched (33)

| File | + | - |
|------|--:|--:|
| `.github/workflows/p2p-gpu.yml` | 187 | 0 |
| `.gitignore` | 7 | 0 |
| `resources/README.md` | 168 | 165 |
| `resources/p2p-gpu/README.md` | 173 | 0 |
| `resources/p2p-gpu/config/service-hints.yaml` | 23 | 0 |
| `resources/p2p-gpu/lib/compatibility.sh` | 385 | 0 |
| `resources/p2p-gpu/lib/constants.sh` | 48 | 0 |
| `resources/p2p-gpu/lib/environment.sh` | 472 | 0 |
| `resources/p2p-gpu/lib/gpu-topology.sh` | 326 | 0 |
| `resources/p2p-gpu/lib/logging.sh` | 76 | 0 |
| `resources/p2p-gpu/lib/models.sh` | 418 | 0 |
| `resources/p2p-gpu/lib/networking.sh` | 556 | 0 |
| `resources/p2p-gpu/lib/permissions.sh` | 293 | 0 |
| `resources/p2p-gpu/lib/services.sh` | 487 | 0 |
| `resources/p2p-gpu/phases/00-preflight.sh` | 184 | 0 |
| `resources/p2p-gpu/phases/01-dependencies.sh` | 36 | 0 |
| `resources/p2p-gpu/phases/02-user-setup.sh` | 47 | 0 |
| `resources/p2p-gpu/phases/03-repository.sh` | 46 | 0 |
| `resources/p2p-gpu/phases/04-installer.sh` | 61 | 0 |
| `resources/p2p-gpu/phases/05-post-install.sh` | 45 | 0 |
| `resources/p2p-gpu/phases/06-bootstrap-model.sh` | 187 | 0 |
| `resources/p2p-gpu/phases/07-model-optimize.sh` | 21 | 0 |
| `resources/p2p-gpu/phases/08-vastai-quirks.sh` | 55 | 0 |
| `resources/p2p-gpu/phases/09-services.sh` | 251 | 0 |
| `resources/p2p-gpu/phases/10-voice-stack.sh` | 19 | 0 |
| `resources/p2p-gpu/phases/11-access-layer.sh` | 32 | 0 |
| `resources/p2p-gpu/phases/12-summary.sh` | 21 | 0 |
| `resources/p2p-gpu/setup.sh` | 192 | 0 |
| `resources/p2p-gpu/subcommands/fix.sh` | 68 | 0 |
| `resources/p2p-gpu/subcommands/info.sh` | 20 | 0 |
| `resources/p2p-gpu/subcommands/resume.sh` | 36 | 0 |
| `resources/p2p-gpu/subcommands/status.sh` | 70 | 0 |
| `resources/p2p-gpu/subcommands/teardown.sh` | 44 | 0 |

## Auditor's read of the diff

_TBD — auditor reads `raw/diff.patch` and writes the gap-vs-claim here.
For Trivial-tier PRs this is often "matches the title; no surprises"._
