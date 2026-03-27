# Step 8 — Compliance Reports & Evidence

> One-click compliance evidence generation for IEC 62304, HIPAA, OWASP Top 10,
> and SOC2 — ready for auditors and regulators.

---

## Per-Framework Compliance Reports

Sentrik generates HTML compliance reports scoped to a single regulatory
framework. Each report maps every control to the findings and evidence in your
codebase, giving auditors a control-by-control view of coverage.

### IEC 62304 (Medical Device Software Lifecycle)

```bash
sentrik compliance-report --framework "IEC 62304"
```

Produces a report covering clauses 5.x through 8.x — software development
planning, requirements, architecture, detailed design, maintenance, risk
management, and configuration management. Each control shows pass/fail status,
linked findings, and remediation evidence.

### HIPAA (Health Insurance Portability and Accountability Act)

```bash
sentrik compliance-report --framework "HIPAA"
```

Covers the Security Rule (164.308 Administrative, 164.310 Physical,
164.312 Technical, 164.314 Organizational, 164.316 Documentation). Maps
ePHI handling patterns, encryption enforcement, access controls, and audit
logging to the corresponding HIPAA clauses.

### OWASP Top 10

```bash
sentrik compliance-report --framework "OWASP Top 10"
```

Maps scan findings to OWASP 2021 categories (A01 Broken Access Control through
A10 SSRF). Shows which categories have active findings, which are fully
mitigated, and which have documented threat models and design reviews.

### SOC2 (Trust Services Criteria)

```bash
sentrik compliance-report --framework "SOC2"
```

Covers Common Criteria (CC1 through CC9) plus Availability, Confidentiality,
and Privacy criteria. Links code-level controls (encryption at rest, audit
logging, access management) to the relevant trust services criteria.

### Report Output

Each report is written as a self-contained HTML file:

```
out/compliance-report-iec62304.html
out/compliance-report-hipaa.html
out/compliance-report-owasp.html
out/compliance-report-soc2.html
```

Reports include:
- Overall framework compliance percentage
- Control-by-control status (pass / fail / not applicable)
- Linked findings with severity and remediation status
- Evidence references (file paths, line numbers, suppression justifications)
- Timestamp and scan metadata

---

## Trust Center

Generate a public-safe compliance summary page suitable for sharing with
customers, partners, or prospects:

```bash
sentrik trust-center --org "VitalSync Medical"
```

The trust center page shows:
- Which frameworks are tracked and their compliance status
- High-level posture score
- Last scan timestamp
- No sensitive findings or internal code details are exposed

Output: `out/trust-center.html`

---

## Evidence Export

Bundle all compliance evidence for a specific audit or review:

```bash
sentrik evidence-export --all
```

This generates evidence bundles for all four frameworks in a single command.
Each bundle includes:
- The compliance report (HTML)
- Finding details with remediation evidence
- Suppression records with justifications and approver metadata
- Scan configuration and rule versions used

---

## Audit Bundle

Package everything into a single ZIP archive for regulatory submission:

```bash
sentrik export-audit
```

Creates `out/audit-bundle.zip` containing:
- All four compliance reports
- Evidence bundles for each framework
- SBOM (CycloneDX)
- Vulnerability scan results
- License compliance report
- Suppression log with HMAC-signed integrity
- Scan history and configuration snapshot

This is the file you hand to your auditor or upload to a regulatory portal.

---

## Historical Reports

Sentrik stores scan results so you can generate reports from any past run.

### List past scans

```bash
sentrik history-report --list
```

Shows scan IDs, timestamps, branch names, and finding counts for all stored
runs.

### Generate a report from a past scan

```bash
sentrik history-report --run-id <ID>
```

Produces the same compliance report using the findings from that specific scan
run — useful for showing compliance at a point in time (e.g., at release,
before/after a remediation sprint).

---

## Total Artifacts

After running the full compliance workflow, you have:

| Artifact | Command | Output |
|----------|---------|--------|
| IEC 62304 report | `compliance-report --framework "IEC 62304"` | HTML |
| HIPAA report | `compliance-report --framework "HIPAA"` | HTML |
| OWASP report | `compliance-report --framework "OWASP Top 10"` | HTML |
| SOC2 report | `compliance-report --framework "SOC2"` | HTML |
| Trust center | `trust-center --org "VitalSync Medical"` | HTML |
| Evidence bundles | `evidence-export --all` | per-framework bundles |
| Audit bundle | `export-audit` | ZIP archive |
| Historical reports | `history-report --run-id <ID>` | HTML |

---

## What Sentrik Did

One-click compliance evidence generation. Four framework reports, a trust center
page, evidence bundles, and a ready-to-submit audit archive — all generated
from the same scan data that drives your CI gate. No separate compliance tool,
no manual mapping of findings to controls, no copy-pasting into spreadsheets.

## Without Sentrik

Weeks of manual evidence collection. An engineer (or a consultant) maps each
finding to the relevant regulatory control by hand, formats the evidence into
the auditor's preferred template, and assembles the package manually. Every
scan cycle restarts the process. Historical point-in-time reports require
digging through old CI logs or version control history.

---

Next: [Step 9 — DevOps Integration](09-devops-integration.md)
