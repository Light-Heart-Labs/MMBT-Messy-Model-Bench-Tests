# ADR-003: Recommendation — 1Password Business

## Status
Accepted

## Context
After evaluating 5 password managers (1Password, Bitwarden, LastPass, Dashlane, Keeper) against the criteria defined in ADR-002, we need to select a single product to standardize on.

## Decision
**1Password Business** is recommended as the primary choice, with **Bitwarden Enterprise** as the runner-up.

## Rationale

### Why 1Password Business Won
1. **Best security track record** — No public security incidents. Dual-key encryption architecture. Regular third-party audits.
2. **Full compliance suite** — SOC 2 Type 2, ISO 27001:2022, ISO 27017:2015, ISO 27018:2019, ISO 27701, PCI DSS, GDPR.
3. **Superior developer tooling** — Native `op` CLI widely adopted in developer community, excellent CI/CD integration documentation.
4. **Full platform coverage** — macOS, Windows, Linux, iOS, Android, browser extensions, CLI.
5. **Transparent pricing** — $7.99/user/month (annual billing), publicly listed.
6. **SSO integration** — SAML SSO with Google Workspace, Okta, Azure AD.

### Why Bitwarden Enterprise is the Runner-Up
1. **Lower cost** — $6.00/user/month (annual billing), ~25% cheaper than 1Password.
2. **Open source** — Codebase publicly auditable on GitHub.
3. **Self-hostable** — Can be deployed on our own infrastructure.
4. **SOC 2 Type II + ISO 27001 + HIPAA** — Meets our compliance requirements.

### Why Other Products Were Rejected
- **LastPass** — Disqualified due to 2022 security breaches and 2025 $24.5M class action settlement. Also, pricing not publicly listed.
- **Dashlane** — Disqualified due to no native Linux desktop app (hard requirement for engineering team). Also, pricing not publicly listed.
- **Keeper** — Strong contender but less mature developer tooling. CLI less widely adopted, CI/CD integration less documented.

## Consequences
- Annual cost: $4,794 for 50 seats (1Password Business at $7.99/user/month).
- If budget is the primary constraint, Bitwarden Enterprise at $3,600/year is the alternative.
- If self-hosting is required, Bitwarden is the only option among the 5 evaluated.
