# Walkthrough: Overview

## What Is VitalSync Medical API?

VitalSync is a **FastAPI service** that ingests patient vital signs from wearable
medical devices, stores them securely in a PostgreSQL database, and exposes a
REST API for clinicians. It handles six vital-sign types:

- Heart rate (BPM)
- Blood pressure (systolic / diastolic mmHg)
- Blood oxygen saturation (SpO2 %)
- Body temperature
- Respiratory rate
- Blood glucose

The application follows a clean layered architecture:

```
src/
  api/routes/       -> FastAPI endpoints (patients, vitals, devices, alerts, reports)
  api/middleware/    -> Auth, audit, encryption, rate limiting
  services/         -> Business logic (vitals processing, alerts, encryption, audit)
  db/repositories/  -> Data access layer
  models/           -> SQLAlchemy + Pydantic models
  utils/            -> Validators, PHI filtering, traceability
```

---

## Why Is This Regulated?

A patient vitals system sits at the intersection of **four regulatory
frameworks**, each with different concerns:

| Framework | Scope | Why It Applies |
|-----------|-------|----------------|
| **IEC 62304** | Medical Device Software Lifecycle | Software that processes clinical data from medical devices must follow a defined lifecycle with traceability, risk management, and verified releases. |
| **HIPAA** | Protected Health Information | Patient vital signs are ePHI. Encryption at rest and in transit, access controls, audit trails, and minimum-necessary data handling are mandatory. |
| **OWASP Top 10** | Web Application Security | The API is internet-facing. Injection prevention, authentication, secrets management, rate limiting, and dependency scanning all apply. |
| **SOC2** | Trust Services Criteria | Operating as a SaaS service requires demonstrable security controls, change management, audit logging, and incident response. |

Complying with all four simultaneously -- across every commit -- is the hard
part. That is what Sentrik automates.

---

## What This Walkthrough Demonstrates

This walkthrough follows the **full Sentrik lifecycle** from requirements
definition through compliant, gated production code:

1. **Requirements** -- Define 30 regulatory requirements across 4 frameworks
2. **Init & Config** -- Auto-detect the project, add standards packs, configure gates
3. **First Scan** -- See 1,589 findings, a failed gate, and 3 leaked secrets
4. **Fix Loop** -- Auto-patches, manual fixes, suppressions, and severity rescoring
5. **Supply Chain** -- SBOM generation, CVE scanning, license auditing
6. **CI/CD Gate** -- GitHub Actions, PR decoration, SARIF upload
7. **Dashboard** -- All 15 tabs, REST API, ASPM posture score
8. **Compliance Reports** -- Per-framework reports, trust center, evidence export
9. **DevOps Integration** -- Work-item reconciliation, traceability, sync
10. **Advanced Features** -- MCP server, governance policies, custom packs

---

## Feature Checklist

Every Sentrik feature exercised in this demo:

### Core Scanning & Gating

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Static analysis scan | `sentrik scan` | [03 - First Scan](03-first-scan.md) |
| Quality gate | `sentrik gate` | [03 - First Scan](03-first-scan.md) |
| Project initialization | `sentrik init` | [02 - Init & Config](02-init-and-config.md) |
| List available packs | `sentrik list-packs` | [02 - Init & Config](02-init-and-config.md) |
| Add standards pack | `sentrik add-pack` | [02 - Init & Config](02-init-and-config.md) |
| Validate configuration | `sentrik validate-config` | [02 - Init & Config](02-init-and-config.md) |
| License status | `sentrik license` | [02 - Init & Config](02-init-and-config.md) |

### Metrics, Secrets & Reporting

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Code metrics | `sentrik metrics` | [03 - First Scan](03-first-scan.md) |
| Secrets scanning | `sentrik secrets` | [03 - First Scan](03-first-scan.md) |
| HTML report | `sentrik report --format html` | [03 - First Scan](03-first-scan.md) |
| SARIF report | `sentrik report --format sarif` | [03 - First Scan](03-first-scan.md) |
| JUnit XML report | `sentrik report --format junit` | [03 - First Scan](03-first-scan.md) |
| CSV export | `sentrik report --format csv` | [03 - First Scan](03-first-scan.md) |

### Remediation & Comparison

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Auto-patching | `sentrik apply-patches` | [04 - Fix Loop](04-fix-findings.md) |
| Before/after comparison | `sentrik compare` | [04 - Fix Loop](04-fix-findings.md) |
| File-based suppressions | `.sentrik/suppressions.yaml` | [04 - Fix Loop](04-fix-findings.md) |
| Inline suppressions | `# sentrik:suppress` comments | [04 - Fix Loop](04-fix-findings.md) |
| Severity rescoring | `severity_rescoring_enabled` | [04 - Fix Loop](04-fix-findings.md) |
| Confidence scoring | `confidence_scoring_enabled` | [04 - Fix Loop](04-fix-findings.md) |
| False positive rate | `false_positive_rate` in metrics | [04 - Fix Loop](04-fix-findings.md) |

### Supply Chain Security

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Software Bill of Materials | `sentrik sbom` | [05 - Supply Chain](05-supply-chain.md) |
| Vulnerability scanning | `sentrik vulns` | [05 - Supply Chain](05-supply-chain.md) |
| Auto-fix vulnerabilities | `sentrik vulns --fix` | [05 - Supply Chain](05-supply-chain.md) |
| License auditing | `sentrik licenses` | [05 - Supply Chain](05-supply-chain.md) |

### Compliance & Evidence

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| IEC 62304 compliance report | `sentrik compliance-report --standard iec-62304` | [08 - Compliance](08-compliance-reports.md) |
| HIPAA compliance report | `sentrik compliance-report --standard hipaa` | [08 - Compliance](08-compliance-reports.md) |
| OWASP compliance report | `sentrik compliance-report --standard owasp-top-10` | [08 - Compliance](08-compliance-reports.md) |
| SOC2 compliance report | `sentrik compliance-report --standard soc2` | [08 - Compliance](08-compliance-reports.md) |
| Trust center page | `sentrik trust-center` | [08 - Compliance](08-compliance-reports.md) |
| Evidence export | `sentrik evidence-export` | [08 - Compliance](08-compliance-reports.md) |
| Audit log export | `sentrik export-audit` | [08 - Compliance](08-compliance-reports.md) |

### DevOps & Traceability

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Work-item reconciliation | `sentrik reconcile` | [09 - DevOps](09-devops-integration.md) |
| Dry-run reconciliation | `sentrik reconcile --dry-run` | [09 - DevOps](09-devops-integration.md) |
| DevOps sync | `sentrik sync` | [09 - DevOps](09-devops-integration.md) |
| Import requirements as issues | `sentrik pull-reqs` | [01 - Requirements](01-requirements.md) |
| Requirements traceability | `sentrik trace` | [09 - DevOps](09-devops-integration.md) |
| Coverage check | `sentrik check-coverage` | [09 - DevOps](09-devops-integration.md) |
| Requirements verification | `sentrik verify-reqs` | [09 - DevOps](09-devops-integration.md) |
| Requirements generation | `sentrik generate-reqs` | [09 - DevOps](09-devops-integration.md) |

### Architecture & Governance

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Architecture validation | `sentrik check-arch` | [09 - DevOps](09-devops-integration.md) |
| Policy-as-code checks | `sentrik check-policies` | [10 - Advanced](10-advanced-features.md) |
| Governance profiles | `governance.yaml` | [10 - Advanced](10-advanced-features.md) |

### Dashboard & API

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Interactive dashboard (15 tabs) | `sentrik dashboard` | [07 - Dashboard](07-dashboard.md) |
| REST API | `http://localhost:9100/api/...` | [07 - Dashboard](07-dashboard.md) |
| ASPM posture endpoint | `/api/posture` | [07 - Dashboard](07-dashboard.md) |

### CI/CD Integration

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| GitHub Actions workflow | `.github/workflows/sentrik.yml` | [06 - CI Gate](06-ci-gate.md) |
| PR comment decoration | `--decorate-pr` | [06 - CI Gate](06-ci-gate.md) |
| Commit status check | `--status-check` | [06 - CI Gate](06-ci-gate.md) |
| SARIF upload to GitHub | SARIF artifact upload | [06 - CI Gate](06-ci-gate.md) |

### AI & Advanced

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| MCP server | `sentrik mcp-server` | [10 - Advanced](10-advanced-features.md) |
| MCP audit | `sentrik audit-mcp` | [10 - Advanced](10-advanced-features.md) |
| Context for LLMs | `sentrik context` | [10 - Advanced](10-advanced-features.md) |
| Inline compliance check | `sentrik check-inline` | [10 - Advanced](10-advanced-features.md) |

### Custom Packs & Extensibility

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| Custom pack authoring | `.sentrik/rules/medapi-custom.yaml` | [10 - Advanced](10-advanced-features.md) |
| Import pack | `sentrik import-pack` | [10 - Advanced](10-advanced-features.md) |
| Export pack | `sentrik export-pack` | [10 - Advanced](10-advanced-features.md) |

### Specialized & Enterprise

| Feature | Command / Capability | Walkthrough Step |
|---------|---------------------|------------------|
| C/C++ analysis | `sentrik analyze-cpp` | [10 - Advanced](10-advanced-features.md) |
| File watcher mode | `sentrik watch` | [10 - Advanced](10-advanced-features.md) |
| Impact analysis | `sentrik impact` | [10 - Advanced](10-advanced-features.md) |
| Organization dashboard | `sentrik org-dashboard` | [10 - Advanced](10-advanced-features.md) |
| Historical reporting | `sentrik history-report` | [10 - Advanced](10-advanced-features.md) |
| Auditor portal | Auditor read-only view | [10 - Advanced](10-advanced-features.md) |
| Role-based access control | RBAC configuration | [10 - Advanced](10-advanced-features.md) |
| Config migration | `sentrik migrate` | [10 - Advanced](10-advanced-features.md) |

---

## Without Sentrik

To achieve what Sentrik provides in a single tool, you would need to stitch
together:

| Concern | Tool(s) Required | Annual Cost (approx.) |
|---------|------------------|-----------------------|
| Static analysis | SonarQube Enterprise or Semgrep Pro | $15,000--40,000 |
| Secrets scanning | GitLeaks or TruffleHog + CI config | Free--$5,000 |
| Dependency vulnerabilities | Snyk or Dependabot + dashboard | $5,000--25,000 |
| SBOM generation | Syft or CycloneDX CLI + scripts | Free (manual effort) |
| License compliance | FOSSA or WhiteSource | $10,000--30,000 |
| IEC 62304 traceability | Manual spreadsheet + Jama Connect | $20,000--80,000 |
| HIPAA compliance evidence | Manual checklists + auditor meetings | $15,000--50,000 |
| SOC2 audit preparation | Vanta or Drata | $10,000--30,000 |
| Architecture enforcement | ArchUnit or manual review | Free (manual effort) |
| Policy-as-code | Open Policy Agent + custom rules | Free (engineering time) |
| PR decoration & gating | Custom CI scripts per tool | Free (engineering time) |
| Unified dashboard | Custom build or multiple dashboards | Engineering time |
| **Total** | **8--12 tools + glue** | **$75,000--260,000+** |

With Sentrik, all of this is a single `sentrik scan` command, a single
dashboard, and a single CI step. The configuration is one YAML file. The
learning curve is one afternoon.

---

**Next:** [01 - Requirements](01-requirements.md) -- Defining regulatory
requirements before writing a line of code.
