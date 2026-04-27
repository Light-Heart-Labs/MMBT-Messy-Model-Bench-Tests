# Ubuntu 22.04 Container Environment

Use Ubuntu 22.04 as the baseline installer test environment because it remains a common Docker/WSL/server target and avoids conflating PR regressions with newer distribution defaults.

Recommended package set:

```bash
apt-get update
apt-get install -y git curl jq python3 python3-venv python3-pip docker.io docker-compose-plugin shellcheck
```

For PRs touching installer or compose logic, run:

```bash
git clone https://github.com/Light-Heart-Labs/DreamServer.git
cd DreamServer/dream-server
bash -n install.sh dream-cli scripts/*.sh
docker compose config
```

GPU PRs require hardware-specific runners and are documented separately under `testing/hardware/`.
