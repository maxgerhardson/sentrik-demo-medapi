# Walkthrough: Requirements-First Development

## The Approach

In regulated software development, you do not start with code. You start with
**requirements**. Every feature, security control, and compliance obligation
must be defined, traceable, and verifiable.

Sentrik treats requirements as first-class objects. They live in version
control alongside the code, trace to specific regulatory clauses, and are
verified automatically on every scan.

---

## Requirements Structure

The project defines 30 requirements in `requirements.yaml`, organized by
regulatory framework. Each requirement follows this structure:

```yaml
- id: REQ-IEC-001
  title: "Software development planning"
  description: >
    All software development activities shall be planned and documented.
    A software development plan shall define the processes, tools, and
    methods used for development, verification, and risk management.
  standard: "IEC 62304"
  clause: "5.1"
  status: active
  verification_method: code_review
  acceptance_criteria:
    - "Project has documented development plan (README, architecture docs)"
    - "CI/CD pipeline is defined and operational"
```

Key fields:

- **id** -- Unique identifier used in traceability comments (e.g., `# REQ-IEC-001`)
- **standard** -- Which regulatory framework this traces to
- **clause** -- The specific section of the standard
- **verification_method** -- How compliance is verified (code_review, automated_test, architecture_review, traceability_analysis, automated_scan, process_review)
- **acceptance_criteria** -- Concrete, verifiable conditions for compliance

---

## Requirements by Framework

### IEC 62304 -- Medical Device Software Lifecycle (8 requirements)

| ID | Title | Clause |
|----|-------|--------|
| REQ-IEC-001 | Software development planning | 5.1 |
| REQ-IEC-002 | Software architecture documentation | 5.3 |
| REQ-IEC-003 | Software unit verification | 5.5 |
| REQ-IEC-004 | Software integration and integration testing | 5.6 |
| REQ-IEC-005 | Traceability between requirements and code | 5.7 |
| REQ-IEC-006 | Risk management integration | 7.1 |
| REQ-IEC-007 | Configuration management | 8.1 |
| REQ-IEC-008 | Problem resolution and defect tracking | 9.1 |

These requirements enforce the software lifecycle processes that IEC 62304
mandates for Class B and Class C medical device software. Sentrik's
`fda-iec-62304` pack maps rules directly to these clauses.

### HIPAA -- Security Rule (8 requirements)

| ID | Title | Clause |
|----|-------|--------|
| REQ-HIPAA-001 | PHI encryption at rest | 164.312(a)(2)(iv) |
| REQ-HIPAA-002 | PHI encryption in transit | 164.312(e)(1) |
| REQ-HIPAA-003 | Access control and authentication | 164.312(a)(1) |
| REQ-HIPAA-004 | Audit trail for PHI access | 164.312(b) |
| REQ-HIPAA-005 | Minimum necessary standard | 164.502(b) |
| REQ-HIPAA-006 | Automatic session termination | 164.312(a)(2)(iii) |
| REQ-HIPAA-007 | Integrity controls | 164.312(c)(1) |
| REQ-HIPAA-008 | Contingency planning -- data backup | 164.308(a)(7)(ii)(A) |

These cover the HIPAA Security Rule's technical safeguards. Patient vital
signs are electronic Protected Health Information (ePHI), so every endpoint
that touches patient data must enforce these controls.

### OWASP Top 10 2021 -- Application Security (8 requirements)

| ID | Title | Clause |
|----|-------|--------|
| REQ-OWASP-001 | Input validation and injection prevention | A03:2021 |
| REQ-OWASP-002 | Authentication and session management | A07:2021 |
| REQ-OWASP-003 | Sensitive data exposure prevention | A02:2021 |
| REQ-OWASP-004 | Broken access control prevention | A01:2021 |
| REQ-OWASP-005 | Security misconfiguration prevention | A05:2021 |
| REQ-OWASP-006 | Rate limiting and DoS protection | A04:2021 |
| REQ-OWASP-007 | Dependency vulnerability management | A06:2021 |
| REQ-OWASP-008 | Security logging and monitoring | A09:2021 |

These map to the OWASP Top 10 2021 categories. Since VitalSync is an
internet-facing API handling sensitive medical data, all ten categories
are relevant.

### SOC2 -- Trust Services Criteria (6 requirements)

| ID | Title | Clause |
|----|-------|--------|
| REQ-SOC2-001 | Audit logging and accountability | CC7.2 |
| REQ-SOC2-002 | Change management controls | CC8.1 |
| REQ-SOC2-003 | Logical access controls | CC6.1 |
| REQ-SOC2-004 | System monitoring and alerting | CC7.1 |
| REQ-SOC2-005 | Incident response procedures | CC7.3 |
| REQ-SOC2-006 | Vendor and dependency risk management | CC9.2 |

These cover the SOC2 Trust Services Criteria relevant to a SaaS medical
data platform. They overlap with HIPAA in places (audit logging, access
controls) but add change management and vendor risk dimensions.

---

## GitHub Issues from Requirements

Sentrik can create GitHub Issues from requirements, turning each requirement
into a trackable work item. For this project, 12 issues were created
covering the implementation-focused requirements:

```
$ sentrik pull-reqs --provider github

Created 12 GitHub Issues from requirements:
  #1  REQ-IEC-002  Software architecture documentation
  #2  REQ-IEC-003  Software unit verification
  #3  REQ-IEC-005  Traceability between requirements and code
  #4  REQ-HIPAA-001  PHI encryption at rest
  #5  REQ-HIPAA-003  Access control and authentication
  #6  REQ-HIPAA-004  Audit trail for PHI access
  #7  REQ-OWASP-001  Input validation and injection prevention
  #8  REQ-OWASP-002  Authentication and session management
  #9  REQ-OWASP-003  Sensitive data exposure prevention
  #10 REQ-OWASP-006  Rate limiting and DoS protection
  #11 REQ-SOC2-001  Audit logging and accountability
  #12 REQ-SOC2-002  Change management controls
```

Each issue body includes the requirement description, regulatory clause,
acceptance criteria, and a link back to the requirements file. This
creates a bidirectional link: code traces to requirements, and issues
trace to regulatory clauses.

The `sentrik pull-reqs` command can also import existing issues back into
`requirements.yaml`, keeping the two in sync. When requirements change,
`sentrik reconcile` updates the corresponding issues.

---

## Architecture Rules

The project defines architectural boundaries in `architecture.yaml`:

```yaml
layers:
  - name: api
    paths: ["src/api/routes/**", "src/api/middleware/**"]
    allowed_imports: ["src/services/**", "src/models/**", "src/utils/**"]
    forbidden_imports: ["src/db/**"]

  - name: services
    paths: ["src/services/**"]
    allowed_imports: ["src/db/repositories/**", "src/models/**", "src/utils/**"]
    forbidden_imports: ["src/api/**"]

  - name: db
    paths: ["src/db/**"]
    allowed_imports: ["src/models/**", "src/utils/**"]
    forbidden_imports: ["src/api/**", "src/services/**"]

rules:
  - id: ARCH-001
    description: "API routes must not access the database directly"
    from: "src/api/routes/**"
    to: "src/db/**"
    severity: high

  - id: ARCH-002
    description: "Database layer must not depend on API layer"
    from: "src/db/**"
    to: "src/api/**"
    severity: high
```

This enforces the layered architecture: API -> Services -> Repositories.
Routes cannot bypass the service layer to access the database directly.
Sentrik validates these boundaries via `sentrik check-arch`.

---

## Governance Policies

The project also defines governance policies in `governance.yaml`:

```yaml
governance:
  profile: standard

  human_review_required:
    - trigger: on_critical_finding
      approvers: [{role: security_lead}, {role: tech_lead}]
    - trigger: on_requirement_change
      approvers: [{role: regulatory_affairs}]

  auto_patch:
    enabled: true
    max_severity: low
    require_review_above: medium

  gate:
    fail_on: [critical, high]
    require_clean_gate_for_release: true

  audit:
    enabled: true
    integrity_check: hmac-sha256

policies:
  - id: POL-001
    name: "No direct database access from API layer"
    enforcement: block

  - id: POL-002
    name: "All PHI endpoints require authentication"
    enforcement: warn

  - id: POL-003
    name: "Encryption required for PHI storage"
    enforcement: block

  - id: POL-005
    name: "No secrets in source code"
    enforcement: block

  - id: POL-006
    name: "Vital signs must be clinically validated"
    enforcement: block
```

These policies define:

- **When human review is required** -- Critical findings need security lead and tech lead sign-off. Requirements changes need regulatory affairs approval.
- **Auto-patch boundaries** -- Only low-severity issues can be auto-patched. Anything above medium requires human review.
- **Gate behavior** -- Critical and high findings block merge. A clean gate is required for releases.
- **Policy-as-code rules** -- Six custom policies checked by `sentrik check-policies`.

---

## What Sentrik Did

- Provided a structured format for regulatory requirements with clause-level traceability
- Created GitHub Issues from requirements, connecting development work to regulatory obligations
- Established architecture rules that are validated automatically, not just documented
- Defined governance policies that enforce human review gates and auto-patch boundaries
- Made requirements version-controlled and diffable alongside the code

## Without Sentrik

Without Sentrik, this phase typically involves:

- A **spreadsheet** (usually Excel) mapping requirements to regulatory clauses, maintained manually and quickly out of date
- **No automated enforcement** -- architecture rules exist in a wiki that nobody reads
- **No traceability** -- developers must remember to reference requirements in commit messages, and auditors must manually verify the links
- **Separate issue trackers** -- compliance requirements live in one tool, development tasks in another, with no automatic synchronization
- **Governance by email** -- review gates are enforced by process documents and meeting minutes, not by code

---

**Previous:** [00 - Overview](00-overview.md)
**Next:** [02 - Init & Config](02-init-and-config.md)
