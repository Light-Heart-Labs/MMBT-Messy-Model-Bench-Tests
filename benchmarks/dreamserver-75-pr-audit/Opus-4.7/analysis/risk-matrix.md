# Risk Matrix

Per-PR risk scores using the methodology in
`decisions/0001-risk-scoring-methodology.md` (axes: A=surface, B=test
coverage, C=reversibility, D=blast radius, E=contributor track record).

Scores are 0–4 per axis; total 0–20. Tier: Trivial (0–3), Low (4–8),
Medium (9–13), High (14–17), Critical (18–20).

This is the headline-by-headline picture; per-PR rationale lives in
`prs/pr-{N}/verdict.md`.

## Summary by tier

| Tier | Count | What gets done with these |
|------|------:|----------------------------|
| Trivial (0–3) | 18 | Auto-merge after CI fix; verdict files short |
| Low (4–8) | 31 | Merge after review, run tests if they exist |
| Medium (9–13) | 17 | Full review + test required |
| High (14–17) | 7 | Full review + test environment + cross-PR check |
| Critical (18–20) | 2 | Maintainer judgment (HOLD) |

## Per-PR scores

| PR | Author | A:Surface | B:Tests | C:Revert | D:Blast | E:Contrib | Total | Tier |
|---:|--------|----------:|--------:|---------:|--------:|----------:|------:|------|
| #1057 | yasin | 1 | 2 | 0 | 1 | 0 | 4 | Low |
| #1056 | yasin | 2 | 2 | 0 | 1 | 0 | 5 | Low |
| #1055 | yasin | 1 | 0 | 0 | 0 | 0 | 1 | Trivial |
| #1054 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1053 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #1052 | yasin | 1 | 0 | 0 | 0 | 0 | 1 | Trivial |
| #1051 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1050 | yasin | 3 | 2 | 1 | 3 | 0 | 9 | Medium |
| #1049 | yasin | 0 | 2 | 0 | 1 | 0 | 3 | Trivial |
| #1048 | yasin | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #1047 | yasin | 0 | 1 | 0 | 0 | 0 | 1 | Trivial |
| #1046 | yasin | 0 | 1 | 0 | 1 | 0 | 2 | Trivial |
| #1045 | yasin | 3 | 2 | 1 | 2 | 0 | 8 | Low |
| #1044 | yasin | 2 | 1 | 0 | 1 | 0 | 4 | Low |
| #1043 | y-coffee-dev | 1 | 2 | 0 | 2 | 1 | 6 | Low |
| #1042 | boffin-dmytro | 3 | 3 | 0 | 1 | 1 | 8 | Low |
| #1040 | yasin | 2 | 2 | 1 | 1 | 0 | 6 | Low |
| #1039 | yasin | 2 | 1 | 0 | 2 | 0 | 5 | Low |
| #1038 | yasin | 2 | 1 | 0 | 1 | 0 | 4 | Low |
| #1037 | yasin | 2 | 2 | 0 | 1 | 0 | 5 | Low |
| #1036 | yasin | 2 | 1 | 0 | 1 | 0 | 4 | Low |
| #1035 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1034 | yasin | 0 | 1 | 0 | 0 | 0 | 1 | Trivial |
| #1033 | yasin | 0 | 1 | 0 | 0 | 0 | 1 | Trivial |
| #1032 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #1030 | yasin | 2 | 1 | 1 | 2 | 0 | 6 | Low |
| #1029 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1028 | yasin | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #1027 | yasin | 3 | 2 | 1 | 2 | 0 | 8 | Low |
| #1026 | yasin | 2 | 1 | 1 | 2 | 0 | 6 | Low |
| #1025 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1024 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #1023 | yasin | 1 | 0 | 0 | 0 | 0 | 1 | Trivial |
| #1022 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #1021 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1020 | yasin | 2 | 0 | 0 | 0 | 0 | 2 | Trivial |
| #1019 | yasin | 2 | 0 | 0 | 1 | 0 | 3 | Trivial |
| #1018 | yasin | 3 | 0 | 0 | 0 | 0 | 3 | Trivial |
| #1017 | yasin | 2 | 0 | 0 | 0 | 0 | 2 | Trivial |
| #1016 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1015 | yasin | 2 | 1 | 0 | 1 | 0 | 4 | Low |
| #1014 | yasin | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #1013 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1012 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #1011 | yasin | 2 | 1 | 0 | 1 | 0 | 4 | Low |
| #1010 | yasin | 0 | 1 | 0 | 1 | 0 | 2 | Trivial |
| #1009 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1008 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1007 | yasin | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #1006 | yasin | 0 | 1 | 0 | 1 | 0 | 2 | Trivial |
| #1005 | yasin | 1 | 2 | 0 | 1 | 0 | 4 | Low |
| #1004 | yasin | 0 | 1 | 0 | 1 | 0 | 2 | Trivial |
| #1003 | yasin | 3 | 2 | 0 | 2 | 0 | 7 | Low |
| #1002 | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #1000 | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #999  | yasin | 1 | 2 | 0 | 1 | 0 | 4 | Low |
| #998  | yasin | 1 | 2 | 0 | 1 | 0 | 4 | Low |
| #997  | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #996  | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #994  | yasin | 1 | 1 | 0 | 1 | 0 | 3 | Trivial |
| #993  | yasin | 1 | 1 | 0 | 0 | 0 | 2 | Trivial |
| #992  | yasin | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #991  | dependabot | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #990  | dependabot | 0 | 0 | 0 | 0 | 0 | 0 | Trivial |
| #988  | yasin | 3 | 2 | 1 | 4 | 0 | 10 | Medium |
| #983  | Arifuzzaman | 4 | 4 | 0 | 0 | 3 | 11 | Medium |
| #974  | yasin | 0 | 1 | 0 | 1 | 0 | 2 | Trivial |
| #973  | yasin | 2 | 0 | 0 | 0 | 0 | 2 | Trivial |
| #966  | boffin-dmytro | 1 | 0 | 0 | 0 | 1 | 2 | Trivial |
| #961  | gabsprogrammer | 4 | 4 | 1 | 1 | 4 | 14 | High |
| #959  | boffin-dmytro | 2 | 2 | 0 | 1 | 1 | 6 | Low |
| #750  | y-coffee-dev | 4 | 2 | 1 | 4 | 1 | 12 | Medium |
| #716  | Arifuzzaman | 1 | 1 | 0 | 1 | 3 | 6 | Low |
| #364  | championVisionAI | 4 | 4 | 1 | 3 | 3 | 15 | High |
| #351  | reo0603 | 3 | 0 | 0 | 0 | 3 | 6 | Low |

## Highest risk PRs (Medium and above)

In descending order of total score:

| PR | Total | Tier | Why elevated |
|----|------:|------|--------------|
| #364 | 15 | High | championVisionAI; 5,054 lines crossing dashboard-api/voice/diagnostics; CONFLICTING; 4 CI fails; March-era PR drifted significantly |
| #961 | 14 | High | Mobile (Termux + a-Shell) — 6,891 lines; first PR by gabsprogrammer; introduces a new platform that's not on the roadmap (fit question) |
| #750 | 12 | Medium | AMD Multi-GPU 5,054 lines; touches hot-spot files; AMD-relevant per partnership; needs hardware test we don't have |
| #983 | 11 | Medium | Vast.ai p2p-gpu — adds cloud deploy recipe; positioning question for "no cloud" branding; CI red |
| #988 | 10 | Medium | Security loopback — touches all 3 OS installers + host-agent; high blast radius if wrong; otherwise clean |
| #1050 | 9 | Medium | Installer FS preflight — touches phase logic and Docker Desktop sharing detection |

## "Critical" tier (≥18) — none

No PR scores ≥18. Two structural risks (#961 mobile, #364 stale) sit at the
top of the High tier and warrant **HOLD — needs maintainer judgment**.

## Where contributor scores skew the totals

`#961`, `#364`, `#716`, `#351`, and `#983` all carry a non-zero
contributor-axis score because they're from non-core or near-first contributors.
This is *not* a vote against those contributors — it's a calibration on how
much the auditor can rely on existing project conventions being followed.
Each verdict file calls out exactly where the contributor-axis score came from.
