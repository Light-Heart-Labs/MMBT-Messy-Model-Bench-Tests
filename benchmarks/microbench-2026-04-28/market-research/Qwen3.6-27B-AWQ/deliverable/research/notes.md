# Research Notes — Password Manager Evaluation

## Date: 2025-01-XX
## Researcher: AI Assistant

## Products Evaluated
1. 1Password (Business tier)
2. Bitwarden (Teams & Enterprise tiers)
3. LastPass (Business tier)
4. Dashlane (Business tier)
5. Keeper (Business tier)

## Key Findings

### 1Password
- **Pricing**: Business tier at $7.99/user/month (annual billing), $9.99/user/month (monthly)
  - Source: 1Password pricing page JSON data (https://1password.com/pricing/)
- **Compliance**: SOC 2 Type 2, ISO 27001:2022, ISO 27017:2015, ISO 27018:2019, ISO 27701, PCI DSS, GDPR
  - Source: https://trust.1password.io/
- **Security**: No major public security incidents. Zero-knowledge architecture. Dual-key encryption.
  - Source: https://1password.com/security/
- **Platforms**: macOS, Windows, Linux, iOS, Android, browser extensions, CLI
  - Source: https://1password.com/downloads/
- **Developer features**: CLI tool, Secrets Manager (separate product), API access
- **SSO**: Google Workspace, Okta, Azure AD, and other SAML providers

### Bitwarden
- **Pricing**: Teams at $4/user/month (annual billing), Enterprise at $6/user/month (annual billing)
  - Source: https://bitwarden.com/pricing/
- **Compliance**: SOC 2 Type II, SOC 3, ISO 27001, HIPAA, GDPR, CCPA/CPRA
  - Source: https://bitwarden.com/compliance/
- **Security**: Open source, independently audited. No major public security incidents.
  - Source: https://bitwarden.com/security/
- **Platforms**: macOS, Windows, Linux, iOS, Android, browser extensions, CLI
- **Developer features**: CLI tool, self-hostable, Secrets Manager (separate product), open source
- **SSO**: SAML SSO, SCIM provisioning

### LastPass
- **Pricing**: Business pricing not publicly listed; must contact sales
  - Source: https://www.lastpass.com/pricing (no public pricing for Business tier)
- **Compliance**: SOC 2, HIPAA
  - Source: https://www.lastpass.com/compliance
- **Security**: MAJOR SECURITY INCIDENTS:
  - 2022: Two related breaches — development environment accessed, source code and encrypted backup keys stolen; DevOps engineer's computer compromised via keystroke logger
  - 2025: Settled class action lawsuit for $24.5 million
  - 2015: Hashed master passwords exposed
  - 2017: Android app security vulnerabilities
  - Source: https://en.wikipedia.org/wiki/LastPass
- **Platforms**: macOS, Windows, Linux, iOS, Android, browser extensions, CLI
- **SSO**: SAML SSO, directory integrations

### Dashlane
- **Pricing**: Business pricing not publicly listed; must contact sales
  - Personal: $2.71/month (annual billing), Family: $4.07/month (up to 10 members)
  - Source: https://www.dashlane.com/pricing, ZDNet comparison (https://www.zdnet.com/article/best-password-manager/)
- **Compliance**: SOC 2, ISO 27001
  - Source: https://www.dashlane.com/security
- **Security**: No major public security incidents
- **Platforms**: macOS, Windows, iOS, Android, browser extensions
  - Note: No native Linux desktop app
- **SSO**: SAML SSO available on business plans

### Keeper
- **Pricing**: Business at $7/user/month (minimum 5 seats)
  - Source: ZDNet comparison (https://www.zdnet.com/article/best-password-manager/)
- **Compliance**: SOC 2, ISO 27001, FedRAMP
  - Source: https://trust.keeper.io/
- **Security**: No major public security incidents
- **Platforms**: macOS, Windows, Linux, iOS, Android, browser extensions, CLI
- **SSO**: Okta, Azure AD, Ping Identity, Google Workspace
  - Source: ZDNet comparison

## Pricing Summary (Annual Billing, Per User Per Month)
| Product | Tier | Price |
|---------|------|-------|
| 1Password | Business | $7.99 |
| Bitwarden | Teams | $4.00 |
| Bitwarden | Enterprise | $6.00 |
| LastPass | Business | Not publicly listed |
| Dashlane | Business | Not publicly listed |
| Keeper | Business | $7.00 |

## 50-Seat Annual Cost
| Product | Tier | Annual Cost |
|---------|------|-------------|
| 1Password | Business | $4,794 (50 × $7.99 × 12) |
| Bitwarden | Teams | $2,400 (50 × $4.00 × 12) |
| Bitwarden | Enterprise | $3,600 (50 × $6.00 × 12) |
| LastPass | Business | Unknown (contact sales) |
| Dashlane | Business | Unknown (contact sales) |
| Keeper | Business | $4,200 (50 × $7.00 × 12) |

## Decision Criteria Weighting
1. Security posture & incident history (25%)
2. SOC 2 compliance (20%)
3. Developer experience (CLI, API, CI/CD) (15%)
4. SSO integration with Google Workspace (15%)
5. Pricing transparency & cost (10%)
6. Platform coverage (Linux, mobile, desktop) (10%)
7. Admin UX & audit capabilities (5%)
