# Privacy Impact Assessment (Simulated Mini DPIA/RIPD)

## Disclaimer

This is a simulated, portfolio-grade privacy impact assessment inspired by LGPD practices.
It is not legal advice and not a legal compliance certification.

## Data Categories

- Personal data: customer-related identifiers and quasi-identifiers
- Sensitive personal data: flagged fields requiring stronger controls
- Indirect identifiers: fields that may re-identify when combined

## Simulated Legal/Governance Basis

- Purpose limitation: executive analytics and governance reporting
- Data minimization: published layer excludes or pseudonymizes risky fields
- Retention: documented as simulated policy for portfolio demonstration

## Controls

- Classification: heuristic + YAML contract rules
- Privacy risk scoring: explainable score with decision thresholds
- Actions: keep, mask, anonymize, remove, review
- Publication gate: Approved / Needs Review / Blocked

## Residual Risk

Residual risk is acknowledged when indirect identifiers remain for analytical value.
Publication decision should be blocked or reviewed when thresholds are not met.

## Decision Matrix (Simplified)

| Condition | Decision |
| --- | --- |
| Contract fail, critical quality fail, or unprotected sensitive data | Blocked |
| Elevated privacy risk or degraded quality/freshness | Needs Review |
| Controls within thresholds | Approved |
