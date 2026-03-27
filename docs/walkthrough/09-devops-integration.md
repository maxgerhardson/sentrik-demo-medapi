# Step 9 — DevOps Integration & Traceability

> Automated bidirectional traceability from requirements through code, tests,
> and work items — no spreadsheets required.

---

## Issue Reconciliation

Sentrik can create work items in your issue tracker directly from scan
findings. Every documentation obligation and unresolved finding becomes a
trackable issue.

### Preview

```bash
sentrik reconcile --dry-run
```

```
Dry run — 20 issues would be created:
  IEC62304-5.1.1  software-development-plan          (obligation)
  IEC62304-5.1.6  software-verification-plan          (obligation)
  HIPAA-164.308-a1  risk-analysis                     (obligation)
  OWASP-A04-001  threat-model                         (obligation)
  SOC2-CC6-003  access-control-policy                  (obligation)
  ...
No changes made.
```

### Create Issues

```bash
sentrik reconcile
```

```
Created 20 GitHub Issues from documentation obligations.
```

Each created issue includes:
- **Title:** Rule ID and short description
- **Body:** Full rule description, remediation guidance, severity, and
  framework reference
- **Labels:** `guard` label plus rule-specific labels (e.g., `iec62304`,
  `hipaa`, `owasp`, `soc2`)
- **Severity tag:** Critical / High / Medium / Low mapped from the rule

Issues are idempotent — running `reconcile` again will not create duplicates.
Sentrik tracks which findings already have open issues.

---

## Requirements Generation

Sentrik can reverse-engineer requirements from your codebase by scanning for
`REQUIREMENT:` comments and structured patterns:

```bash
sentrik generate-reqs
```

```
Scanned codebase — found 10 requirements:
  REQ-AUTH-001   JWT authentication on all API endpoints
  REQ-ENC-001    AES-256 encryption for PHI at rest
  REQ-ENC-002    TLS 1.2+ for data in transit
  REQ-AUDIT-001  Immutable audit log for PHI access
  REQ-VAL-001    Input validation on all vital sign values
  ...
Written to requirements.yaml
```

This supplements hand-written requirements with discovered implementation
requirements, ensuring nothing is missed.

---

## Requirements Verification

Detect drift between your documented requirements and the actual code:

```bash
sentrik verify-reqs
```

Checks that:
- Every requirement in `requirements.yaml` has at least one implementing file
  (via `REQUIREMENT:` code comments)
- Every implementing file links back to a valid requirement ID
- Every requirement has at least one associated test
- No orphaned requirements exist (documented but not implemented)
- No orphaned implementations exist (code claiming a requirement that
  does not exist)

---

## Traceability Chain

Sentrik maintains a full traceability chain across the development lifecycle:

```
requirement (requirements.yaml)
    |
    v
code file (REQUIREMENT: REQ-AUTH-001 comment)
    |
    v
test (test file covering that code path)
    |
    v
GitHub Issue (created by reconcile)
```

Every link is verifiable. The `verify-reqs` command checks the chain end to end
and reports any broken links.

---

## DevOps Connection

Sentrik integrates with GitHub, Azure DevOps, and Jira via OAuth.

### Test the connection

```bash
sentrik test-connection
```

Verifies that:
- OAuth tokens are valid and not expired
- The target repository or project is accessible
- Issue creation permissions are available
- Label management permissions are available

### Supported platforms

| Platform | Auth | Work Items |
|----------|------|------------|
| GitHub | OAuth (PKCE) | Issues |
| Azure DevOps | OAuth / PAT | Work Items |
| Jira | OAuth | Issues |

---

## Work Item Lifecycle

The full lifecycle of a finding through your issue tracker:

1. **Finding detected** — `sentrik scan` identifies a rule violation or
   documentation obligation
2. **Issue created** — `sentrik reconcile` creates a GitHub Issue (or ADO Work
   Item / Jira Issue) with full context
3. **Developer fixes** — the code change addresses the finding, includes a
   `REQUIREMENT:` comment linking back to the rule
4. **Issue resolved** — next `sentrik reconcile` run detects the finding is
   resolved and can close the issue (or mark it for review)
5. **Verified** — `sentrik verify-reqs` confirms the traceability chain is
   intact

---

## What Sentrik Did

Automated bidirectional traceability. Requirements flow into code via
`REQUIREMENT:` comments, code flows into tests, and findings flow into tracked
work items — all verified by a single tool. Twenty GitHub Issues created in
seconds, each with full context and remediation guidance. Requirements
verification catches drift before it reaches production.

## Without Sentrik

Manual issue creation from scan results — copy-pasting findings into GitHub
Issues one at a time. Traceability tracked in spreadsheets or Word documents
that go stale within days. Requirements drift discovered during audits, not
during development. No automated verification that every requirement is
implemented, tested, and tracked.

---

Next: [Step 10 — Advanced Features](10-advanced-features.md)
