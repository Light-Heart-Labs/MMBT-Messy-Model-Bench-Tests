# Surface Area Analysis

## Subsystem Distribution

| Subsystem | PRs Touching | Files | Key PRs |
|-----------|-------------|-------|---------|
| extensions-library | 33 | 700+ | #351, #364, #716, #1027, #1032, #1033, #1034 |
| scripts (resolve-compose) | 28 | 5 | #1051, #1029, #1004, #1024 |
| dream-cli | 22 | 1 | #998, #1002, #1008, #1006, #1007, #994, #993, #999, #1000, #997, #1016, #1011 |
| tests | 20 | 10+ | #1052, #1018, #1019, #1020, #1014 |
| host-agent | 17 | 1 | #1057, #1050, #1039, #1038, #1035, #1030, #988 |
| windows | 17 | 10+ | #1012, #996, #974, #959 |
| macos | 15 | 5+ | #1025, #1020, #1016, #1013, #1005, #1004, #999 |
| ci | 11 | 5+ | #1053, #991, #990, #983 |
| resources | 11 | 100+ | #983, #973, #966, #961, #959 |
| compose | 9 | 10+ | #1009, #1024, #1029, #1051 |
| installer | 8 | 10+ | #1050, #1043, #1026, #974 |
| docs | 6 | 20+ | #1055, #1017, #973, #966 |
| gpu | 5 | 5+ | #750, #1032, #1009, #1025, #999 |
| installer-windows | 4 | 5+ | #1012, #996, #974, #959 |
| installer-tests | 3 | 2 | #1018, #1014 |

## Hot Files (Most Contested)

| File | PRs Touching | Conflict Level |
|------|-------------|----------------|
| `dream-server/bin/dream-host-agent.py` | 7 | High |
| `dream-server/dream-cli` | 12 | High |
| `dream-server/scripts/resolve-compose-stack.sh` | 4 | Medium |
| `dream-server/extensions/services/dashboard-api/routers/extensions.py` | 6 | High |
| `dream-server/.env.schema.json` | 3 | Medium |
| `dream-server/.env.example` | 3 | Low |
| `resources/dev/extensions-library/services/*/compose.yaml` | 10+ | Very High |
| `resources/dev/extensions-library/services/*/manifest.yaml` | 8+ | Very High |

## AMD-Relevant Surface Area

| File | PR | Impact |
|------|-----|--------|
| `dream-server/docker-compose.amd.yml` | #1009 | Image-gen default off |
| `resources/dev/extensions-library/services/continue/compose.amd.yaml` | #1032 | New AMD overlay |
| `dream-server/scripts/resolve-compose-stack.sh` | #1029 | gpu_backends filter |
| `dream-server/bin/dream-host-agent.py` | #988 | Loopback binding (all backends) |
| `dream-server/installers/` | #750 | AMD Multi-GPU support |

## Risk by Subsystem

| Subsystem | Risk Level | Reason |
|-----------|-----------|--------|
| host-agent | Medium | Core dispatcher; changes affect all users |
| dream-cli | Medium | Primary user interface; changes affect all users |
| extensions-library | High | 700+ files; hard to review comprehensively |
| compose | Medium | Core deployment configuration |
| installer | Medium | First-run experience; changes affect new users |
| tests | Low | Test changes are low-risk |
| docs | Low | Documentation changes are low-risk |
| ci | Low | CI changes are low-risk |
| gpu | High | GPU changes affect hardware compatibility |
