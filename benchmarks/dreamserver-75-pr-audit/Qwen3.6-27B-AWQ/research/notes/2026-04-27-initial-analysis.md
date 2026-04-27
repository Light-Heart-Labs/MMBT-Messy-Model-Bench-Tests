# Research Notes

## Session 2026-04-27: Initial Analysis

### Questions Resolved

1. **Q: How many open PRs?**
   A: 75 open PRs, confirmed via GitHub API.

2. **Q: Who are the contributors?**
   A: 8 unique contributors. yasinBursali dominates with 63/75 PRs (84%).

3. **Q: What's the size distribution?**
   A: Three PRs (#351, #364, #716) are 150k+ lines each. The rest range from 500 to 14k lines.

4. **Q: Are there file conflicts?**
   A: Yes. Major conflict clusters in extensions-library (351/364/716/1027), host-agent (1057/1050/1039/1038/1035/1030/988), and dream-cli (12 PRs).

5. **Q: What's the AMD impact?**
   A: PR #750 is the primary AMD feature. No PRs regress AMD compatibility.

6. **Q: What's the security posture?**
   A: Four PRs (#988, #994, #1010, #1050) address security. PR #988 is the most important (loopback binding).

### Dead Ends

1. **Attempted to use `gh` CLI for PR data** — failed because `gh` is unauthenticated. Switched to curl + GitHub API.
2. **Attempted `git fetch origin pull/*/head`** — failed because the refspec syntax doesn't work with git fetch. Switched to fetching individual PR SHAs.

### Key Architectural Insights

1. **Layered Compose Model:** DreamServer uses a layered compose model — base compose + GPU overlays + extension fragments. This means changes to the resolver (#1051, #1029, #1004) affect how all services are discovered and started.

2. **Host Agent as Dispatcher:** The host agent (`dream-host-agent.py`) is the dispatcher between the dashboard API and Docker. Changes here affect all extension installs, starts, and stops.

3. **Platform-Specific Paths:** macOS runs llama-server natively (not in Docker), which creates different dependency chains. PRs like #1004 (skip compose.local.yaml on Apple Silicon) address this.

4. **Extensions Library Structure:** Each extension has a `manifest.yaml`, `compose.yaml`, and optional GPU overlays. The resolver discovers extensions by scanning directories and reading manifests.

### Assumptions Made

1. **yasinBursali is the primary maintainer** — assumed based on 63/75 PRs and the quality/consistency of contributions.
2. **The bounty system encourages large PRs** — assumed based on the three 150k-line PRs from first-time contributors.
3. **AMD partnership is active** — assumed based on PR #750 and the AMD overlay files in the codebase.
