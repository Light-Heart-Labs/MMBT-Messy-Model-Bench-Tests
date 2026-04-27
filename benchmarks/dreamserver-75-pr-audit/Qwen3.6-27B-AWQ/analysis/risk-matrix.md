# Risk Scoring Methodology (ADR-001)

## Decision

Every PR receives a risk score on 5 axes, each scored 1-5:

| Axis | Definition | 1 (Low) | 5 (High) |
|------|-----------|---------|----------|
| **Surface Area** | Number of files/subsystems touched | 1 file, 1 subsystem | 50+ files, 5+ subsystems |
| **Test Coverage** | Existing test coverage of affected code | 100% covered, new tests added | No tests, no coverage |
| **Reversibility** | How easily the change can be reverted | Single commit, no data migration | Multi-commit, data migration, breaking API |
| **Blast Radius** | Impact if the change is wrong | Cosmetic, single user path | System-wide outage, data loss |
| **Contributor Track** | Contributor's history with the project | Established, 50+ merged PRs | First-time, no history |

**Composite Risk Score** = (Surface + Test + Reverse + Blast + Track) / 5

- **Low (≤2.0):** Merge without maintainer review
- **Medium (2.1-3.5):** Merge with maintainer awareness
- **High (3.6-4.5):** Requires maintainer judgment
- **Critical (>4.5):** Requires maintainer + community review

## Scoring Rationale

- **Surface Area:** Counted by unique files changed. PRs touching 100+ files (like #351, #364, #716) get 5 regardless of content quality.
- **Test Coverage:** Based on whether the PR includes tests AND whether existing tests cover the affected code paths. PRs that add tests get -1 on this axis.
- **Reversibility:** PRs that change data formats, add new config keys, or modify installer state get higher scores.
- **Blast Radius:** PRs touching `dream-host-agent.py`, `dream-cli`, or core compose files get higher scores because they affect all users.
- **Contributor Track:** yasinBursali (63 PRs, primary maintainer) gets 1. First-time contributors get 4-5.

## Per-PR Scores

| PR | Surface | Test | Reverse | Blast | Track | Composite | Risk Level |
|----|---------|------|---------|-------|-------|-----------|------------|
| #1057 | 1 | 2 | 1 | 2 | 1 | 1.4 | Low |
| #1056 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1055 | 1 | 5 | 1 | 1 | 1 | 1.8 | Low |
| #1054 | 1 | 3 | 1 | 1 | 1 | 1.4 | Low |
| #1053 | 1 | 3 | 1 | 1 | 1 | 1.4 | Low |
| #1052 | 1 | 1 | 1 | 1 | 1 | 1.0 | Low |
| #1051 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1050 | 3 | 2 | 1 | 3 | 1 | 2.0 | Low |
| #1049 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1048 | 1 | 5 | 1 | 1 | 1 | 1.8 | Low |
| #1047 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1046 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1045 | 3 | 2 | 1 | 3 | 1 | 2.0 | Low |
| #1044 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1043 | 3 | 2 | 1 | 3 | 4 | 2.6 | Medium |
| #1042 | 2 | 2 | 1 | 2 | 4 | 2.2 | Medium |
| #1040 | 3 | 2 | 1 | 2 | 1 | 1.8 | Low |
| #1039 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1038 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1037 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1036 | 3 | 3 | 1 | 2 | 1 | 2.0 | Low |
| #1035 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1034 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1033 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1032 | 2 | 4 | 1 | 1 | 1 | 1.8 | Low |
| #1030 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1029 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1028 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1027 | 4 | 1 | 1 | 3 | 1 | 2.0 | Low |
| #1026 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1025 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1024 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1023 | 2 | 4 | 1 | 2 | 1 | 2.0 | Low |
| #1022 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #1021 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1020 | 2 | 1 | 1 | 1 | 1 | 1.2 | Low |
| #1019 | 3 | 1 | 1 | 2 | 1 | 1.6 | Low |
| #1018 | 3 | 1 | 1 | 2 | 1 | 1.6 | Low |
| #1017 | 4 | 5 | 1 | 2 | 1 | 2.6 | Medium |
| #1016 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1015 | 3 | 2 | 1 | 2 | 1 | 1.8 | Low |
| #1014 | 1 | 1 | 1 | 1 | 1 | 1.0 | Low |
| #1013 | 2 | 4 | 1 | 2 | 1 | 2.0 | Low |
| #1012 | 2 | 4 | 1 | 2 | 1 | 2.0 | Low |
| #1011 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1010 | 2 | 1 | 1 | 1 | 1 | 1.2 | Low |
| #1009 | 2 | 4 | 1 | 2 | 1 | 2.0 | Low |
| #1008 | 1 | 3 | 1 | 2 | 1 | 1.6 | Low |
| #1007 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1006 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #1005 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #1004 | 1 | 4 | 1 | 2 | 1 | 1.8 | Low |
| #1003 | 3 | 2 | 1 | 2 | 1 | 1.8 | Low |
| #1002 | 1 | 3 | 1 | 2 | 1 | 1.6 | Low |
| #1000 | 1 | 3 | 1 | 1 | 1 | 1.4 | Low |
| #999 | 2 | 3 | 1 | 2 | 1 | 1.8 | Low |
| #998 | 1 | 3 | 1 | 2 | 1 | 1.6 | Low |
| #997 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #996 | 2 | 4 | 1 | 2 | 1 | 2.0 | Low |
| #994 | 2 | 2 | 1 | 2 | 1 | 1.6 | Low |
| #993 | 1 | 4 | 1 | 1 | 1 | 1.6 | Low |
| #992 | 1 | 5 | 1 | 1 | 1 | 1.8 | Low |
| #991 | 1 | 5 | 1 | 1 | 1 | 1.8 | Low |
| #990 | 1 | 5 | 1 | 1 | 1 | 1.8 | Low |
| #988 | 3 | 2 | 1 | 4 | 1 | 2.2 | Medium |
| #983 | 5 | 5 | 1 | 3 | 4 | 3.6 | High |
| #974 | 3 | 3 | 1 | 3 | 1 | 2.2 | Medium |
| #973 | 4 | 5 | 1 | 2 | 1 | 2.6 | Medium |
| #966 | 5 | 5 | 1 | 2 | 4 | 3.4 | High |
| #961 | 5 | 5 | 1 | 4 | 5 | 4.0 | Critical |
| #959 | 5 | 5 | 1 | 3 | 4 | 3.6 | High |
| #750 | 5 | 3 | 2 | 4 | 4 | 3.6 | High |
| #716 | 5 | 4 | 1 | 3 | 4 | 3.4 | High |
| #364 | 5 | 4 | 1 | 3 | 5 | 3.6 | High |
| #351 | 5 | 1 | 1 | 3 | 5 | 3.0 | High |

## Key Observations

1. **yasinBursali PRs (63/75):** All score Low-Medium risk due to established track record. The surface area is the main risk factor.
2. **Large PRs (#351, #364, #716, #961, #983):** All score High-Critical due to massive surface area (100k+ lines, 100+ files).
3. **AMD PR (#750):** Scores High due to surface area and contributor track, but is the highest-value PR for the AMD partnership.
4. **Mobile PR (#961):** Scores Critical — first-time contributor, 137 files, 12k lines, entirely new platform support.
