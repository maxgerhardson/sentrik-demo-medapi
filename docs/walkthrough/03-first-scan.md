# Walkthrough: First Scan -- The "Before" State

## Running the Scan

With configuration in place, run the first scan against the codebase in its
initial, intentionally non-compliant state:

```
$ sentrik scan

  Sentrik v1.1.0 — Scanning VitalSync Medical API

  Standards packs: fda-iec-62304, owasp-top-10, hipaa, soc2
  Rules loaded:    155 (across 4 packs)
  Files scanned:   50
  Duration:        2.7s

  ══════════════════════════════════════════════════════════
  FINDINGS: 1,589 total
  ══════════════════════════════════════════════════════════

  By severity:
    HIGH ............. 1,558
    INFO .............    31

  By category:
    IEC62304-TRACE-001 (traceability header missing) .... 1,558
    Documentation obligations ........................... 31
      IEC62304-5.1.1  Software Development Plan ........ 1
      IEC62304-5.1.6  Software Maintenance Plan ........ 1
      IEC62304-5.2.1  Software Requirements Spec ....... 1
      IEC62304-5.3.1  Software Architecture Doc ........ 1
      IEC62304-5.4.1  Detailed Design Doc .............. 1
      IEC62304-6.1    Software Maintenance Plan ........ 1
      IEC62304-7.1.1  Risk Management File ............. 1
      IEC62304-8.1.1  Configuration Management Plan .... 1
      OWASP-A04-001   Insecure Design Review ........... 1
      OWASP-A04-002   Threat Modeling .................. 1
      OWASP-A06-001   Security Hardening Guide ......... 1
      OWASP-A09-001   Logging Standard ................. 1
      OWASP-A09-002   Monitoring Runbook ............... 1
      HIPAA-164.308-a1  Security Management Process .... 1
      HIPAA-164.308-a3  Workforce Security ............. 1
      HIPAA-164.308-a4  Information Access Management .. 1
      HIPAA-164.308-a5  Security Awareness Training .... 1
      HIPAA-164.308-a6  Security Incident Procedures ... 1
      HIPAA-164.308-a7  Contingency Plan ............... 1
      HIPAA-164.310-a1  Facility Access Controls ....... 1
      HIPAA-164.314-a1  Business Associate Agreements .. 1
      HIPAA-164.316-b1  Documentation Requirements ..... 1
      SOC2-CC6-003    Encryption Policy ................ 1
      SOC2-CC6-004    Key Management Procedures ........ 1
      SOC2-CC7-003    Vulnerability Management ......... 1
      SOC2-CC7-004    Incident Response Plan ........... 1
      SOC2-CC8-001    Change Management Policy ......... 1
      SOC2-CC9-001    Risk Assessment .................. 1
      SOC2-A1-001     Availability Policy .............. 1
      SOC2-C1-002     Data Classification Policy ....... 1
      SOC2-C1-003     Data Retention Policy ............ 1

  Compliance score: 49.7%

  Reports generated:
    out/report.html
    out/report.sarif.json
    out/report.xml
    out/report.csv
```

### Understanding the Findings

The scan found **1,589 findings** in two categories:

1. **1,558 traceability violations (HIGH)** -- Every source file is missing a
   traceability header comment linking it to a requirement. IEC 62304 clause
   5.1.1 requires bidirectional traceability between requirements and code.
   Without these headers, an auditor cannot verify which requirement each
   file implements.

2. **31 documentation obligations (INFO)** -- These are not code bugs. They
   are reminders that certain documents (Software Development Plan, Risk
   Management File, Contingency Plan, etc.) must exist. Sentrik surfaces
   these as info-level findings so they appear in compliance reports but do
   not block the gate on their own.

---

## Gate Check

The gate evaluates whether the codebase meets the configured thresholds:

```
$ sentrik gate

  Sentrik Gate — VitalSync Medical API
  ══════════════════════════════════════════════════════════

  Thresholds:
    Fail on: critical, high

  Results:
    Critical findings: 0
    High findings:     1,558
    Info findings:     31

  ══════════════════════════════════════════════════════════
  GATE: FAILED
  ══════════════════════════════════════════════════════════

  Reason: 1,558 high-severity findings exceed threshold.

  Run `sentrik scan` for details or `sentrik apply-patches`
  to auto-fix eligible findings.
```

The gate fails because 1,558 high-severity traceability findings exceed the
threshold. This is exactly what should happen -- the gate is working. No
code should ship without traceability in a regulated environment.

---

## Code Metrics

Sentrik provides code-quality metrics alongside compliance findings:

```
$ sentrik metrics

  Code Metrics — VitalSync Medical API
  ══════════════════════════════════════════════════════════

  Files:           50
  Lines of code:   2,003
  Blank lines:     412
  Comment lines:   189

  Complexity:
    Max nesting depth:     14
    Avg nesting depth:     2.3
    Max function length:   87 lines
    Avg function length:   12.4 lines

  By language:
    Python ............. 48 files (1,891 LOC)
    YAML ...............  2 files (112 LOC)

  Quality indicators:
    Comment ratio:       9.4%
    Test file ratio:     18.0% (9/50)
```

The **max nesting depth of 14** is a red flag -- deeply nested code is hard
to test, hard to review, and a risk factor in regulated software. The metrics
give the team concrete targets for refactoring.

---

## Secrets Scanning

Sentrik scans for hardcoded secrets separately from compliance rules:

```
$ sentrik secrets

  Secrets Scan — VitalSync Medical API
  ══════════════════════════════════════════════════════════

  Files scanned: 66
  Secrets found: 3

  CRITICAL  src/config.py:7
    Rule:    SECRET-DB-URI
    Match:   post****sync
    Entropy: 4.83
    Detail:  Database connection string with credentials

  HIGH  src/config.py:6
    Rule:    SECRET-PASSWORD
    Match:   admi****
    Entropy: 3.0
    Detail:  Hardcoded password assignment

  HIGH  src/config.py:10
    Rule:    SECRET-GENERIC-KEY
    Match:   sk_t****FAKE
    Entropy: 4.8
    Detail:  Generic API key assignment

  ══════════════════════════════════════════════════════════
  3 secrets found (1 critical, 2 high)

  These secrets must be removed from source code and rotated.
  Use environment variables or a secrets manager instead.
```

Three secrets in `src/config.py`:

- A **database connection string** with embedded PostgreSQL credentials (critical)
- A **hardcoded password** (`admin****`) used for default configuration (high)
- A **generic API key** that looks like a Stripe test key (high)

All three violate HIPAA (164.312), OWASP A02 (Cryptographic Failures), and
SOC2 CC6 (Logical Access Controls). Sentrik found them instantly; a manual
code review might miss the connection string embedded in a URI.

---

## Report Generation

The scan automatically generates reports in all four configured formats:

```
$ ls out/

  report.html         Interactive HTML report with filtering and search
  report.sarif.json   SARIF for GitHub Code Scanning / IDE integration
  report.xml          JUnit XML for CI pipeline test results
  report.csv          CSV for spreadsheet analysis and auditor handoff
```

### HTML Report

The HTML report is a self-contained, interactive page with:

- Finding counts by severity, rule, and file
- Expandable finding details with code snippets
- Filtering by severity, standard, and rule ID
- Search across all findings
- Compliance score visualization

### SARIF Report

The SARIF (Static Analysis Results Interchange Format) file integrates with:

- GitHub Code Scanning (uploaded as a build artifact)
- VS Code SARIF Viewer extension
- Azure DevOps Advanced Security
- Any SARIF-compatible tool

### JUnit XML Report

The JUnit report maps each finding to a test case, so CI systems display
compliance results in their native test-results UI. Each rule becomes a
test suite, and each finding becomes a failed test case.

### CSV Report

The CSV export contains one row per finding with columns for rule ID,
severity, file, line, message, standard, clause, and remediation guidance.
This is the format auditors often request for import into their GRC tools.

---

## Summary: The Starting Point

| Metric | Value |
|--------|-------|
| Total findings | 1,589 |
| High severity | 1,558 |
| Info severity | 31 |
| Secrets found | 3 (1 critical, 2 high) |
| Compliance score | 49.7% |
| Gate status | FAILED |
| Files scanned | 50 |
| Lines of code | 2,003 |
| Max nesting depth | 14 |

This is the "before" picture. The codebase has real functionality -- it
handles patient data ingestion, authentication, alerts, and reporting --
but it lacks the compliance controls that a regulated medical device requires.

The next steps will show how Sentrik helps fix these findings systematically:
auto-patching traceability headers, suppressing false positives, remediating
secrets, and driving the compliance score from 49.7% to 100%.

---

## What Sentrik Did

- Found all 1,589 compliance issues in **2.7 seconds** with a single command
- Identified 3 hardcoded secrets with entropy analysis
- Generated reports in 4 formats for different audiences (developers, CI, auditors, management)
- Provided a clear compliance score (49.7%) and gate status (FAILED)
- Gave actionable remediation guidance for every finding
- Measured code quality metrics to identify structural risks (nesting depth 14)

## Without Sentrik

Achieving the same coverage manually would require:

- **SonarQube scan** for code quality metrics (nesting, complexity) -- separate install, separate config
- **Semgrep or custom rules** for IEC 62304 traceability -- no off-the-shelf solution exists
- **TruffleHog or GitLeaks** for secrets scanning -- separate tool, separate CI step
- **Manual HIPAA checklist** reviewed by a compliance officer -- days of work per review
- **SOC2 readiness assessment** from a consultant -- weeks of work, thousands of dollars
- **Manual OWASP review** by a security engineer -- hours per endpoint

Total time for equivalent coverage: **days to weeks**, across **4+ tools**,
with results scattered across different dashboards and formats.

With Sentrik: **one command, 2.7 seconds, one report**.

---

**Previous:** [02 - Init & Config](02-init-and-config.md)
**Next:** [04 - Fix Loop](04-fix-findings.md) -- Remediating findings with
auto-patches, suppressions, and manual fixes.
