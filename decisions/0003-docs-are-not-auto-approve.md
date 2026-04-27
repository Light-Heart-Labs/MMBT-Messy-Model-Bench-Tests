# ADR 0003: Documentation PRs Are Not Auto-Approved

## Decision

Documentation-only PRs are reviewed against actual runtime behavior and security posture.

## Why

DreamServer's install and host-agent behavior changes quickly. Wrong docs can lead contributors or users into broken or insecure workflows.

## Consequence

#1055 and #973 were not treated as automatically safe merely because they are docs. #959 remained mergeable because it reduced mismatch risk without overclaiming.
