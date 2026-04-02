# VitalSync Medical API — Sentrik Demo

> A complete walkthrough of requirements-driven development with automated
> compliance governance using [Sentrik](https://sentrik.dev).

## The Application

**VitalSync** is a FastAPI service that ingests patient vital signs from
wearable medical devices, stores them securely, and exposes an API for
clinicians. It handles heart rate, blood pressure, SpO2, temperature,
respiratory rate, and blood glucose readings.

This is a regulated medical device data system, subject to:

- **IEC 62304** — Medical Device Software Lifecycle
- **HIPAA** — Protected Health Information security
- **OWASP Top 10** — Web application security
- **SOC2** — Trust Services Criteria

## The Story

This repo demonstrates the **full Sentrik lifecycle** — from requirements
to compliant, gated production code:

1. **Requirements first** — 30 regulatory requirements across 4 frameworks
2. **First scan** — 1,589 findings at 49.7% compliance (GATE FAILS)
3. **Fix loop** — Traceability headers + suppressions (1,558 findings resolved)
4. **Supply chain** — 19 CVEs found, 18 auto-fixed in one command
5. **Gate pass** — 100% compliance, GATE PASSES
6. **Compliance artifacts** — Reports, trust center, evidence export, audit bundle
7. **DevOps integration** — 20 GitHub Issues auto-created from findings

## Quick Start

```bash
# Clone
git clone https://github.com/maxgerhardson/sentrik-demo-medapi.git
cd sentrik-demo-medapi

# Run the API
docker-compose up

# In another terminal — scan with Sentrik
npm install -g sentrik
sentrik scan
sentrik gate
sentrik dashboard
```

## Walkthrough

Follow the step-by-step walkthrough in [`docs/walkthrough/`](docs/walkthrough/):

| Step | Topic | Key Sentrik Features |
|------|-------|---------------------|
| [00](docs/walkthrough/00-overview.md) | Overview | Feature checklist |
| [01](docs/walkthrough/01-requirements.md) | Requirements | `requirements.yaml`, `pull-reqs` |
| [02](docs/walkthrough/02-init-and-config.md) | Init & Config | `init`, `list-packs`, `add-pack` |
| [03](docs/walkthrough/03-first-scan.md) | First Scan | `scan`, `gate`, `metrics`, `secrets` |
| [04](docs/walkthrough/04-fix-findings.md) | Fix Loop | `compare`, suppressions, false positive mgmt |
| [05](docs/walkthrough/05-supply-chain.md) | Supply Chain | `sbom`, `vulns --fix`, `licenses` |
| [06](docs/walkthrough/06-ci-gate.md) | CI/CD | GitHub Actions, PR decoration, SARIF |
| [07](docs/walkthrough/07-dashboard.md) | Dashboard | All 14 tabs, REST API, ASPM |
| [08](docs/walkthrough/08-compliance-reports.md) | Compliance | Reports, trust center, evidence |
| [09](docs/walkthrough/09-devops-integration.md) | DevOps | `reconcile`, `trace`, work items |
| [10](docs/walkthrough/10-advanced-features.md) | Advanced | MCP, C/C++, governance, custom packs |

## Key Results

| Metric | Before | After |
|--------|--------|-------|
| Compliance Score | 49.7% | **100%** |
| Code Findings | 1,558 high | **0** |
| Gate Status | FAIL | **PASS** |
| Dependency CVEs | 19 | **1** (medium, no fix available) |
| Documentation Obligations | 31 info | 31 info (tracked as GitHub Issues) |
| GitHub Issues | 0 | **32** (12 requirements + 20 auto-reconciled) |

## Sentrik Features Demonstrated

### Core Scanning & Gating
- `sentrik scan` — Full code scan with 4 standards packs
- `sentrik gate` — Quality gate enforcement (FAIL → PASS)
- `sentrik metrics` — Per-file code complexity analysis
- `sentrik secrets` — Hardcoded credential detection
- `sentrik compare` — Delta analysis between scan runs
- `sentrik report` — HTML, SARIF, JUnit XML, CSV reports

### Standards & Rules
- 4 standards packs enabled: IEC 62304, OWASP Top 10, HIPAA, SOC2
- All rule types: regex, required_pattern, file_policy, AST, documentation_obligation
- Custom rules pack: 4 project-specific rules (MEDAPI-001 to MEDAPI-004)
- Inline suppressions + suppressions.yaml for false positive management

### Supply Chain Security
- `sentrik sbom` — CycloneDX SBOM (13 components)
- `sentrik vulns` — CVE scanning (19 found across 5 packages)
- `sentrik vulns --fix` — Auto-patch vulnerable dependencies
- `sentrik licenses` — License compliance audit

### Compliance & Reporting
- `sentrik compliance-report` — Per-framework reports (IEC 62304, HIPAA, OWASP, SOC2)
- `sentrik trust-center` — Public-safe compliance page
- `sentrik evidence-export` — Evidence bundles for auditors
- `sentrik export-audit` — Complete audit bundle (ZIP)
- `sentrik history-report` — Reports from historical scan runs

### DevOps Integration
- `sentrik reconcile` — Auto-create GitHub Issues from findings
- `sentrik generate-reqs` — Auto-generate requirements from code
- GitHub Actions CI/CD with PR decoration and status checks
- SARIF upload to GitHub Code Scanning

### Configuration & Setup
- `sentrik init` — Auto-detection of project type
- `sentrik list-packs` / `add-pack` — Standards pack management
- `sentrik validate-config` — Configuration validation
- `.sentrik/config.yaml` — Full project configuration
- `.sentrik/suppressions.yaml` — Suppression policies

### New: Spec-Driven Compliance
- `sentrik import-spec openapi.yaml` — Generate 9 security rules from OpenAPI spec
- Detects: unauthenticated endpoints, sensitive data in responses (SSN, DOB), HTTP servers, unbounded inputs

### New: Compliance Attestation & Trend
- `sentrik attest` — Signed compliance proof (HMAC-SHA256) with findings digest and git SHA
- `sentrik attest --verify` — Verify attestation integrity
- `sentrik compliance-trend` — Historical compliance score trend
- `sentrik risk-summary` — One-page executive HTML report with traffic light status

### New: Context-Aware Drift Detection
- `sentrik drift-scan` — Behavioral, structural, cross-file, and acceptance criteria drift analysis
- `sentrik next-action` — Top 3 fixable findings prioritized by severity

### New: Additional Standards Packs
- `supply-chain-security` — 21 rules (SLSA, NIST SSDF, CI/CD hardening)
- `nist-ai-rmf` — 15 rules (AI governance, bias, prompt injection, model security)
- `python-security` — 18 rules (eval, pickle, subprocess, Django/Flask, crypto)

### Advanced (Enterprise)
- Custom pack authoring (`.sentrik/rules/medapi-custom.yaml`)
- Architecture rules (`architecture.yaml`)
- Governance policies (`governance.yaml`)
- Multi-agent scanning (`agent_scan: true` — each pack runs in parallel)
- MCP integration for AI coding tools
- LSP server for real-time as-you-type scanning
- C/C++ analysis (`firmware/checksum.c`)
- Auditor portal, RBAC, async approval gates

## Architecture

```
src/
├── api/
│   ├── routes/          # FastAPI endpoints (patients, vitals, devices, alerts, reports)
│   └── middleware/       # Auth, audit, encryption, rate limiting
├── services/            # Business logic (vitals processing, alerts, encryption, audit)
├── db/
│   └── repositories/    # Data access layer
├── models/              # SQLAlchemy + Pydantic models
└── utils/               # Validators, PHI filtering, traceability
```

## Regulatory Context

| Framework | Domain | Key Controls |
|-----------|--------|-------------|
| IEC 62304 | Medical device software lifecycle | Traceability, architecture, testing, risk management |
| HIPAA | Protected health information | Encryption, access control, audit trail, minimum necessary |
| OWASP Top 10 | Web application security | Input validation, injection prevention, secrets management |
| SOC2 | Trust services criteria | Audit logging, change management, monitoring, vendor risk |

## Tags

- `v0.1-requirements` — Project skeleton + requirements + intentionally flawed code
- `v1.0-compliant` — All compliance findings resolved, gate passes
- `v1.1-hardened` — Supply chain vulnerabilities fixed

## License

MIT
