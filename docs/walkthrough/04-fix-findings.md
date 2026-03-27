# Step 4: Fix Findings and Reach Compliance

> **Goal:** Resolve all critical and high findings, suppress false positives, and achieve a passing gate.

The initial scan in [Step 3](03-scan-analyze.md) found **1,589 findings** across 4 standards packs. This step walks through the fix loop: scan, fix, rescan, repeat until the gate passes.

---

## The Fix Loop

Sentrik's `next_actions.md` report (generated during scan) prioritizes what to fix first. Rather than guessing, the team followed the guided remediation plan.

### Round 1: Traceability Headers

The largest category of findings was **IEC62304-TRACE-001** (requirement traceability). IEC 62304 requires every source file to trace back to a software requirement.

**The fix:** Add `# REQUIREMENT: REQ-XXX` headers to all 41 source files, mapping each module to its governing requirement:

```python
# REQUIREMENT: REQ-AUTH-001 — OAuth2 authentication and token management
# REQUIREMENT: REQ-SEC-003 — Role-based access control enforcement

"""
auth/oauth.py — OAuth2 token exchange and validation.
"""
```

Each header references a requirement ID from the project's requirements document, creating a bidirectional trace from code to specification.

### Suppressing Non-Source Files

Not every file needs a traceability header. Configuration files, documentation, and infrastructure files are not medical device software. Rather than adding meaningless headers, the team created a suppressions file.

**`.sentrik/suppressions.yaml`:**

```yaml
suppressions:
  # Configuration files don't need traceability headers
  - rule_id: "IEC62304-TRACE-001"
    file_glob: "*.yaml"
    reason: "YAML configuration files are not source code — traceability is tracked via git history"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: "*.yml"
    reason: "YAML configuration files are not source code"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: "*.toml"
    reason: "TOML configuration files are not source code"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: "*.md"
    reason: "Markdown documentation files are not source code"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: "Dockerfile"
    reason: "Container build files are infrastructure, not medical device software"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: ".env.example"
    reason: "Environment template is not source code"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: ".gitignore"
    reason: "Git configuration is not source code"
    approved_by: "engineering@vitalsync.example.com"

  - rule_id: "IEC62304-TRACE-001"
    file_glob: ".sentrik/**"
    reason: "Sentrik configuration files are tooling, not medical device software"
    approved_by: "engineering@vitalsync.example.com"
```

Every suppression requires:

| Field | Purpose |
|---|---|
| `rule_id` | Which rule to suppress |
| `file_glob` | Which files the suppression applies to |
| `reason` | Auditor-facing justification |
| `approved_by` | Who authorized the suppression |

This creates an auditable record. Regulators can see exactly what was suppressed and why.

---

## Measuring Progress with `sentrik compare`

After making fixes, `sentrik compare` shows what changed:

```
$ sentrik compare

  Sentrik Compare — Baseline vs Current
  ======================================

  Resolved:  1,558
  New:           0
  Unchanged:    31

  Net change: -1,558 findings
```

This is the key metric: **1,558 findings resolved, 0 new findings introduced**. The 31 unchanged findings are all `info`-severity informational items that do not block the gate.

---

## Gate Check

With all critical and high findings resolved:

```
$ sentrik gate

  Sentrik Gate — VitalSync Medical API
  =====================================

  Standards:  fda-iec-62304, owasp-top-10, hipaa, soc2
  Profile:    standard
  Threshold:  critical, high

  Critical:   0
  High:       0
  Medium:     0
  Low:        0
  Info:       31

  ┌──────────────────────────┐
  │   ✅  GATE PASSED        │
  │   100% compliance        │
  └──────────────────────────┘
```

The gate evaluates against the configured thresholds in `.sentrik/config.yaml`:

```yaml
gate_fail_on:
  - critical
  - high
```

Since zero critical or high findings remain, the gate passes.

---

## Remaining Info Findings

The 31 remaining findings are all `info` severity — advisory items that do not indicate compliance violations:

```
$ sentrik scan

  Sentrik Scan — VitalSync Medical API
  =====================================

  Findings: 31
  Severity: info (31)

  All findings are informational. No action required for compliance.
```

These might include documentation suggestions, optional best practices, or style recommendations. They remain visible in the dashboard for continuous improvement but do not block the gate.

---

## Inline Suppressions

For one-off cases where a file-level suppression is too broad, Sentrik supports inline suppression comments:

```python
password_hash = bcrypt.hashpw(pwd, salt)  # SENTRIK-SUPPRESS: HIPAA-SEC-002 — bcrypt is NIST-approved, not a weak hash
```

The format is:

```
# SENTRIK-SUPPRESS: <rule-id> — <justification>
```

Inline suppressions are useful when:
- A specific line triggers a rule but the code is actually correct
- The fix would introduce a worse problem
- A compensating control exists elsewhere

Like file-level suppressions, these appear in the audit log and are visible to reviewers.

---

## Pull Request

All fixes were committed to a feature branch and submitted as **PR #13**:

- **Title:** fix: resolve 1,558 compliance findings across all standards packs
- **Contents:** traceability headers on 41 source files + suppressions.yaml
- **Gate status:** PASSED (posted as a PR status check)
- **Compliance summary:** 0 critical, 0 high, 0 medium, 0 low, 31 info

The CI pipeline (covered in [Step 6](06-ci-gate.md)) ran `sentrik gate --decorate-pr` automatically, posting the compliance summary directly on the PR.

---

## What Sentrik Did

| Capability | How it helped |
|---|---|
| `next_actions.md` | Prioritized remediation — fix the highest-impact items first |
| `sentrik compare` | Quantified progress: 1,558 resolved, 0 new, 31 unchanged |
| `sentrik gate` | Binary pass/fail against configured thresholds |
| Suppressions file | Auditable record of accepted risks with justification |
| Inline suppressions | Fine-grained control for individual lines |
| PR decoration | Compliance summary posted directly on the pull request |

## Without Sentrik

- No way to measure remediation progress — you fix things and hope
- No structured suppression mechanism — findings get ignored informally with no audit trail
- No gate to confirm you are actually done — compliance is a guess until the auditor arrives
- Traceability is a spreadsheet exercise done months after the code is written

---

**Next:** [Step 5 — Supply Chain Security](05-supply-chain.md)
