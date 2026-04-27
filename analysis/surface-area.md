# Surface Area

## Subsystem Clusters

| Subsystem | PRs | Notes |
|---|---|---|
| Installer / platform | #1050, #1048, #1043, #1026, #1013, #1012, #1005, #996, #988, #974, #750 | Highest operational blast radius. |
| Host agent / extension install | #1057, #1054, #1045, #1030, #1039, #1040, #1032, #1021, #1035 | Many direct API vs UI-path gaps. |
| Extension compose/library | #1049, #1047, #1046, #1036, #1034, #1033, #1028, #1027, #716 | Compose config must be tested as merged stacks. |
| Resolver / CLI Bash | #1051, #1029, #1024, #1023, #1018, #1016, #1011, #1008, #1007, #1006, #1002, #1000, #998, #997, #994 | Strict-mode work needs ordered merge. |
| Dashboard/API/setup | #1025, #1022, #1020, #1019, #1015, #1014, #1010, #1009, #1003, #364, #351 | Frontend/backend test mocks and stale routers are recurring issues. |
| CI/docs/support | #1055, #1053, #1052, #1042, #1017, #973, #966, #959, #991, #990 | Docs must trail behavior, not lead it. |
| GPU/AMD/mobile | #750, #983, #961, #1009, #999, #1025, #1020 | Hardware/platform proof must be explicit. |

## Blast-Radius Guidance

- A docs-only PR can still be high-impact if it documents insecure or broken operational guidance (#1055, #973).
- Compose changes should be validated with all required dependency fragments, not standalone files only.
- GPU changes need a hardware/simulation label in the verdict.
- Host-agent changes need both happy-path and bypass-path review.
