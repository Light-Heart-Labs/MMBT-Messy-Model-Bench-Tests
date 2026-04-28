# ADR-001: Selection of 5 Password Managers for Evaluation

## Status
Accepted

## Context
We need to evaluate password managers for a 50-person engineering team at a Series-B SaaS company. The team currently uses shadow-IT password storage (browser, sticky notes, Slack DMs). The CTO wants this fixed in 90 days.

## Decision
We will evaluate the following 5 password managers:

1. **1Password** — Leading enterprise password manager with strong security posture
2. **Bitwarden** — Open-source, self-hostable option with growing enterprise features
3. **LastPass** — Well-known brand, though with recent security incidents
4. **Dashlane** — Consumer-friendly with enterprise features
5. **Keeper** — Long-standing enterprise security vendor

## Rationale
These 5 represent the major players in the team/enterprise password manager space:
- **1Password**: Widely regarded as the gold standard for security and UX
- **Bitwarden**: Open-source alternative that appeals to engineering teams; self-hostable
- **LastPass**: Market leader by user count, but with notable security history
- **Dashlane**: Strong consumer brand with enterprise tier
- **Keeper**: Enterprise-focused with compliance emphasis

We excluded:
- **Keeper** alternatives like RoboForm (niche, declining)
- **SSO products** (Okta, Auth0) — these are adjacent but not password managers
- **Secrets management** (HashiCorp Vault, AWS Secrets Manager) — different use case
- **Browser-native** (Chrome Password Manager) — not a team solution
- **NordPass, Passbolt** — smaller players with less enterprise maturity

## Criteria for Evaluation
1. **Security**: Zero-knowledge architecture, audit history, compliance certifications
2. **Team features**: Admin console, audit logs, shared vaults, SSO integration
3. **Pricing**: Per-seat cost for 50 users, annual billing
4. **Developer integration**: CLI tools, API access, CI/CD compatibility
5. **Platform coverage**: Desktop (macOS, Windows, Linux), mobile (iOS, Android), browser extensions
6. **SOC 2 compliance**: Required for a SaaS company pursuing SOC 2
