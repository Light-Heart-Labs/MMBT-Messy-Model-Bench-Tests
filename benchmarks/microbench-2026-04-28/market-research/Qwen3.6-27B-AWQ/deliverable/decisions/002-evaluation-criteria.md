# ADR-002: Evaluation Criteria for Password Manager Selection

## Status
Accepted

## Context
We need to evaluate 5 password managers for a 50-person engineering team at a Series-B SaaS company. The team currently uses shadow-IT password storage (browser, sticky notes, Slack DMs). The CTO wants this fixed in 90 days.

## Decision
The following weighted criteria were established for evaluation:

| # | Criterion | Weight | Rationale |
|---|-----------|--------|-----------|
| 1 | Security posture & incident history | 25% | SaaS company; security posture is a competitive differentiator. Clean vendor record is non-negotiable. |
| 2 | SOC 2 compliance | 20% | Required for our own SOC 2 audit. Password manager must be SOC 2 Type 2 certified. |
| 3 | Developer experience (CLI, API, CI/CD) | 15% | Team uses Linux, CLI tools, CI/CD pipelines. Native CLI support is essential for adoption. |
| 4 | SSO integration with Google Workspace | 15% | We use Google Workspace for identity. SSO reduces rollout friction. |
| 5 | Pricing transparency & cost | 10% | Series-B company needs predictable costs. Opaque pricing creates budget uncertainty. |
| 6 | Platform coverage (Linux, mobile, desktop) | 10% | Must support macOS, Windows, Linux, iOS, Android, browser extensions. |
| 7 | Admin UX & audit capabilities | 5% | Admin console must support user management, shared vaults, audit logs, security policies. |

## Rationale
- **Security (25%)** is weighted highest because a vendor breach could compromise our own security posture and customer trust.
- **SOC 2 (20%)** is weighted second because it's a hard requirement for our own compliance audit.
- **Developer experience (15%)** is weighted third because our team's adoption depends on seamless integration with their workflow (CLI, CI/CD).
- **SSO (15%)** is weighted fourth because it's critical for rollout success — engineers won't adopt a tool that requires separate credentials.
- **Pricing (10%)** is weighted fifth because while cost matters, it's secondary to security and compliance.
- **Platform coverage (10%)** is weighted sixth because Linux support is a hard requirement for our engineering team.
- **Admin UX (5%)** is weighted lowest because it's important but not a deal-breaker.

## Consequences
- Products without SOC 2 Type 2 certification are disqualified.
- Products without Linux support are disqualified.
- Products with major security incidents are heavily penalized.
- Products with opaque pricing are penalized but not disqualified.
