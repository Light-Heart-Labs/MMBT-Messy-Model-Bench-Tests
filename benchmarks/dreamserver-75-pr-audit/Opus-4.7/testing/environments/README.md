# Test Environments

Each Dockerfile here corresponds to one of the OS targets DreamServer
supports. They're minimal — just the toolchain the installer expects —
so a maintainer reproducing any audit test can build the container in
under 5 minutes.

## Dockerfile.installer-smoke

Ubuntu 22.04 with bash, BATS, shellcheck, jq, ripgrep, Docker CLI (no
daemon — mount `/var/run/docker.sock`).

**Why 22.04 and not 24.04:** matrix-smoke runs on both; 22.04 has older
bash and util-linux which catches portability issues 24.04 wouldn't.

### Common usage

```bash
docker build -f testing/environments/Dockerfile.installer-smoke \
    -t dream-installer-smoke .

# Sanity-check a phase script
docker run --rm -v "$PWD/../dreamserver-src:/src:ro" dream-installer-smoke \
    bash -c 'cd /src/dream-server && bash -n installers/phases/06-directories.sh'

# Run BATS suite
docker run --rm -v "$PWD/../dreamserver-src:/src:ro" dream-installer-smoke \
    bash -c 'cd /src/dream-server/tests && bats bats-tests/'

# Run a specific BATS test
docker run --rm -v "$PWD/../dreamserver-src:/src:ro" dream-installer-smoke \
    bash -c 'cd /src/dream-server/tests && bats bats-tests/docker-phase.bats'

# shellcheck a single script
docker run --rm -v "$PWD/../dreamserver-src:/src:ro" dream-installer-smoke \
    shellcheck /src/dream-server/installers/phases/03-features.sh

# docker-compose validate (host daemon required)
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD/../dreamserver-src:/src:ro" \
    dream-installer-smoke \
    bash -c 'cd /src/dream-server && docker compose -f docker-compose.base.yml config --quiet'
```

## What this audit actually used these environments for

The audit was conducted on Windows / Git Bash with Docker Desktop
available. The container was built once for sanity-checking BATS
output (the `repro-bats-docker-cmd-arr.sh` script that documents the
CI-poisoning bug on main) and inspecting installer scripts in their
expected execution environment.

The audit did **not** run a full `make gate` against every PR — that
would take ~20 minutes per PR ×75 PRs ≈ 25 hours. Instead, the audit
relied on the project's own CI green/red signals (filtered for the
known-broken integration-smoke job — see
`research/questions.md` Q1) plus targeted spot-checks of installer
phase logic for the High and Medium PRs.

For PRs whose verdict was MERGE based on diff inspection alone, the
maintainer should run `make gate` on the post-merge state of `main`
before each non-trivial wave (per
`report/backlog-strategy.md`).
