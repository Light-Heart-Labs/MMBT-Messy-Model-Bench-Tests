# Sources

## External Content Fetched

### GitHub API
- **URL:** `https://api.github.com/repos/Light-Heart-Labs/DreamServer/pulls?state=open&per_page=100`
- **SHA:** N/A (API response, not versioned)
- **Content:** Full PR metadata for all 75 open PRs (titles, authors, bodies, labels, files)
- **Used for:** PR list, author attribution, PR descriptions, label analysis

### DreamServer Repository
- **URL:** `https://github.com/Light-Heart-Labs/DreamServer.git`
- **Branch:** `main`
- **HEAD SHA:** `d5154c3` (Merge pull request #987)
- **Content:** Full repository including ARCHITECTURE.md, CLAUDE.md, SECURITY_AUDIT.md
- **Used for:** Architecture context, baseline code, diff analysis

### PR Branches (Fetched via git)
All 75 PR branches fetched individually:
- Format: `git fetch origin <sha>:refs/remotes/pull/<num>`
- Used for: Local diff analysis, file-level comparison

## Internal References

### Key Files Reviewed
- `ARCHITECTURE.md` — System architecture, GPU backends, service topology
- `CLAUDE.md` — Development guidelines, contributing standards
- `SECURITY_AUDIT.md` — Security posture, known vulnerabilities
- `dream-server/bin/dream-host-agent.py` — Host agent dispatcher (7 PRs)
- `dream-server/dream-cli` — CLI tool (12 PRs)
- `dream-server/scripts/resolve-compose-stack.sh` — Compose resolver (4 PRs)
- `dream-server/extensions/services/dashboard-api/routers/extensions.py` — Extensions router (6 PRs)

### PR Bodies Analyzed
All 75 PR bodies were analyzed for:
- Claimed functionality
- Testing claims
- Platform impact statements
- Known considerations
- Bounty tier claims

## Tools Used
- `curl` — GitHub API access
- `git` — Repository cloning, PR fetching, diff analysis
- `python3` — PR stats computation, conflict detection, verdict generation
- `bash` — Shell scripting, file operations
