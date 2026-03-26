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

1. **Requirements** — Hand-written regulatory requirements with traceability
2. **First scan** — Intentional findings across all rule types
3. **Fix loop** — Auto-remediation + manual fixes + suppressions
4. **Gate pass** — Clean CI run with PR decoration
5. **Compliance artifacts** — Reports, trust center, evidence export

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
| [04](docs/walkthrough/04-fix-findings.md) | Fix Loop | `apply-patches`, `compare`, suppressions |
| [05](docs/walkthrough/05-supply-chain.md) | Supply Chain | `sbom`, `vulns`, `licenses` |
| [06](docs/walkthrough/06-ci-gate.md) | CI/CD | GitHub Actions, PR decoration, SARIF |
| [07](docs/walkthrough/07-dashboard.md) | Dashboard | All 15 tabs, REST API, ASPM |
| [08](docs/walkthrough/08-compliance-reports.md) | Compliance | Reports, trust center, evidence |
| [09](docs/walkthrough/09-devops-integration.md) | DevOps | `reconcile`, `trace`, work items |
| [10](docs/walkthrough/10-advanced-features.md) | Advanced | MCP, C/C++, governance, custom packs |

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

## License

MIT
