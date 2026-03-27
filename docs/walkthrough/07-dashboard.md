# Step 7: Dashboard and API

> **Goal:** Use the Sentrik dashboard for real-time compliance visibility and the REST API for integrations.

CLI output is great for CI pipelines and developer workflows. But compliance managers, QA leads, and auditors need a visual interface. Sentrik ships a built-in web dashboard that runs locally — no SaaS account required.

---

## Starting the Dashboard

```
$ sentrik dashboard

  Sentrik Dashboard — VitalSync Medical API
  ===========================================

  Server running at http://localhost:8000
  Press Ctrl+C to stop.
```

Open `http://localhost:8000` in any browser. The dashboard reads scan results from the `out/` directory and the `.sentrik/` configuration — no database required.

---

## Dashboard Tabs

The dashboard provides 14 tabs, each focused on a specific compliance concern:

### 1. Overview

The landing page shows the compliance posture at a glance:

- **Severity distribution** — donut chart of findings by critical/high/medium/low/info
- **Compliance score** — percentage of rules passing across all enabled standards packs
- **Top files** — files with the most findings, ranked by severity
- **Trend chart** — compliance score over time (populated after multiple scans)

This is the page you show auditors first.

### 2. Findings

Searchable, filterable table of all findings:

- Filter by severity, standard, rule, file, or status (open/suppressed/resolved)
- Each finding shows the code snippet with the flagged line highlighted
- Click a finding to see the full rule description, remediation guidance, and related standard references
- Export filtered results to CSV

### 3. Reports

Generate compliance reports without touching the CLI:

- **HTML report** — formatted document suitable for audit submissions
- **JUnit XML** — for CI systems that consume test results
- **SARIF** — for GitHub Code Scanning and other SARIF-compatible tools
- **CSV** — for spreadsheet analysis

Reports are generated on demand from the current scan data.

### 4. Policies

Governance profile selector:

- **Standard** — gate fails on critical and high findings
- **Strict** — gate fails on medium and above
- **Permissive** — gate fails on critical only
- **Custom** — define your own thresholds

The active profile determines how `sentrik gate` evaluates findings. Changing the profile here updates `.sentrik/config.yaml`.

### 5. Packs

Enable or disable standards packs:

- Toggle individual packs on/off (e.g., enable `hipaa`, disable `soc2`)
- See rule count and coverage for each pack
- Preview which rules a pack contains before enabling it

This project has 4 packs enabled: `fda-iec-62304`, `owasp-top-10`, `hipaa`, and `soc2`.

### 6. Rules

Browse all rules across all enabled packs:

- Filter by severity, type (security, traceability, documentation, configuration), or standard
- Each rule shows its ID, description, severity, and the standard it comes from
- View the rule's detection pattern and remediation guidance
- See how many findings each rule has generated in the current scan

### 7. Work Items

Synced GitHub Issues:

- Sentrik can create GitHub Issues for findings that need tracking
- Issues link back to the specific finding, file, and line
- Status syncs bidirectionally — closing the issue marks the finding as addressed
- Bulk operations: create issues for all high findings, close resolved issues

### 8. Integration

Connect to DevOps platforms:

- **GitHub** — repository connection for PR decoration, status checks, and issue sync
- **Azure DevOps** — work item sync and pipeline integration
- **Jira** — issue creation and status sync

This project uses GitHub integration, configured in `.sentrik/config.yaml`:

```yaml
devops_provider: github
github_owner: maxgerhardson
github_repo: sentrik-demo-medapi
```

### 9. Audit Log

Every significant action is logged:

- Scan runs with timestamps, finding counts, and duration
- Gate evaluations with pass/fail result and threshold applied
- Suppression changes with who approved them
- Configuration changes

Each audit log entry includes an HMAC-SHA256 integrity signature, making tampered entries detectable. This is critical for regulated environments where audit trail integrity is a requirement.

### 10. Approvals (Enterprise)

Async gate approval workflow:

- When a gate check requires human review (e.g., critical finding override), an approval request is created
- Designated approvers receive notifications
- Approval or rejection is recorded in the audit log
- Useful for change advisory boards in regulated environments

### 11. History

Historical scan runs:

- Table of all previous scan runs with date, finding count, and compliance score
- Trend chart showing compliance score over time
- Click any run to see its full findings and compare against the current state
- Useful for demonstrating continuous improvement to auditors

### 12. Vulnerabilities

CVE viewer for supply chain findings:

- All vulnerabilities from `sentrik vulns` displayed with CVE IDs, severity, and affected packages
- Links to NVD and vendor advisories
- Shows which vulnerabilities have been fixed and which remain
- CVSS scores and exploitability metrics

### 13. Licenses

Dependency license compliance:

- All packages with their detected licenses
- Risk classification (none, low, medium, high) based on license type
- Policy violations highlighted (e.g., GPL in a proprietary project)
- Export license inventory for procurement review

### 14. Settings

Configuration viewer:

- Current `.sentrik/config.yaml` contents
- Active standards packs and their rule counts
- Gate thresholds and governance profile
- Output directory and reporter configuration
- Integration status

---

## REST API

The dashboard exposes a REST API for programmatic access:

### Key Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check — returns `{"status": "ok"}` |
| `/api/posture` | GET | ASPM security posture score (0-100) with breakdown |
| `/api/findings` | GET | All findings with filtering (`?severity=high&standard=hipaa`) |
| `/api/findings/{id}` | GET | Single finding detail |
| `/api/metrics` | GET | Scan metrics: duration, finding counts, false positive rate |
| `/api/sbom` | GET | Current SBOM in CycloneDX format |
| `/api/vulns` | GET | Vulnerability scan results |
| `/api/licenses` | GET | License compliance results |
| `/api/audit` | GET | Audit log entries |
| `/api/history` | GET | Historical scan runs |

### Example: Security Posture Score

```bash
$ curl http://localhost:8000/api/posture | jq

{
  "score": 96,
  "grade": "A",
  "breakdown": {
    "code_compliance": 100,
    "supply_chain": 92,
    "secrets": 100,
    "license_compliance": 100
  },
  "findings_summary": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 31
  },
  "timestamp": "2026-03-26T14:30:00Z"
}
```

The posture score is an ASPM (Application Security Posture Management) metric that aggregates code compliance, supply chain risk, secrets exposure, and license compliance into a single number. Useful for executive reporting and trend tracking.

### Example: Filtered Findings

```bash
$ curl "http://localhost:8000/api/findings?severity=info&standard=hipaa" | jq '.count'

8
```

---

## Dark Mode and Keyboard Shortcuts

The dashboard supports dark mode (toggle in the top-right corner) and keyboard navigation:

| Shortcut | Action |
|---|---|
| `Ctrl+K` | Open command palette / search |
| `1` through `9` | Jump to tabs 1-9 directly |
| `0` | Jump to tab 10 (Approvals) |
| `/` | Focus the search/filter input |
| `Esc` | Close modals and clear filters |
| `?` | Show keyboard shortcut help |

---

## What Sentrik Did

| Capability | How it helped |
|---|---|
| Single dashboard | All compliance data — findings, vulns, licenses, audit log — in one place |
| REST API | Programmatic access for custom integrations and reporting |
| Posture score | Single metric for executive reporting and trend tracking |
| Audit log with HMAC | Tamper-evident audit trail for regulatory compliance |
| No SaaS required | Runs locally, data stays on your machine |
| Dark mode + shortcuts | Developer-friendly UX for daily use |

## Without Sentrik

- **Multiple dashboards:** Snyk for vulnerabilities, SonarQube for code quality, GitHub Security for secrets — no unified view
- **No posture score:** Each tool has its own metrics, no single number to track
- **No audit trail:** Tool logs are scattered across services, no integrity verification
- **SaaS dependency:** Most tools require cloud accounts, sending your code and findings to third-party servers
- **No API:** Most compliance tools are designed for human consumption, not automation

---

**Previous:** [Step 6 — CI/CD Gate](06-ci-gate.md)
