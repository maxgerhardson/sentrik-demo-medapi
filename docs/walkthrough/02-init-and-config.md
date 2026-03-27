# Walkthrough: Project Initialization & Configuration

## Auto-Detection with `sentrik init`

Sentrik can initialize itself by inspecting your project. It detects the
language, framework, file structure, and suggests appropriate standards packs:

```
$ sentrik init

  Sentrik — Project Initialization

  Detected:
    Language:    Python 3.12
    Framework:   FastAPI
    Build:       pyproject.toml (setuptools)
    Structure:   src/ layout with layered architecture
    Tests:       tests/ (pytest)
    CI:          GitHub Actions

  Suggested packs:
    owasp-top-10      Web application security (recommended for FastAPI)
    hipaa             PHI handling detected (patient/vital keywords in models)
    soc2              SaaS application patterns detected

  Created:
    .sentrik/config.yaml    Project configuration
    .sentrik/               Sentrik working directory

  Run `sentrik scan` to analyze your project.
```

Sentrik detected Python/FastAPI from the project structure, noticed
patient-data keywords in the models (suggesting HIPAA relevance), and
created a baseline configuration. Zero manual setup required.

---

## Available Standards Packs

Sentrik ships with 14 standards packs. To see what is available:

```
$ sentrik list-packs

  Available Standards Packs (14):

  FREE TIER
  ──────────────────────────────────────────────────────────
  owasp-top-10         OWASP Top 10 2021 web security           42 rules
  sans-top-25          SANS/CWE Top 25 dangerous weaknesses     38 rules
  python-security      Python-specific security patterns         22 rules
  javascript-security  JavaScript/Node.js security               28 rules
  php-security         PHP security patterns                     15 rules
  kotlin-security      Kotlin/JVM security patterns              13 rules
  general-security     Language-agnostic security checks         19 rules
  secrets              Secrets and credential detection          12 rules

  ORGANIZATION TIER
  ──────────────────────────────────────────────────────────
  fda-iec-62304        IEC 62304 medical device lifecycle        35 rules
  hipaa                HIPAA Security Rule technical safeguards  28 rules
  soc2                 SOC2 Trust Services Criteria              31 rules
  pci-dss              PCI DSS payment card security             24 rules
  iso-27001            ISO 27001 information security            22 rules
  gdpr                 GDPR data protection                     18 rules

  Total: 366 rules across 14 packs
```

For VitalSync, we need four packs: the medical device lifecycle standard,
HIPAA for patient data, OWASP for web security, and SOC2 for trust criteria.

---

## Adding Standards Packs

```
$ sentrik add-pack fda-iec-62304
  Added: fda-iec-62304 (IEC 62304 Medical Device Software Lifecycle, 35 rules)

$ sentrik add-pack owasp-top-10
  Added: owasp-top-10 (OWASP Top 10 2021, 42 rules)

$ sentrik add-pack hipaa
  Added: hipaa (HIPAA Security Rule, 28 rules)

$ sentrik add-pack soc2
  Added: soc2 (SOC2 Trust Services Criteria, 31 rules)
```

Each pack adds its rules to the scan. Packs can overlap -- for example, both
HIPAA and SOC2 include audit-logging rules -- and Sentrik deduplicates findings
so you do not see the same issue reported twice under different rule IDs.

---

## Configuration Walkthrough

After initialization and pack setup, `.sentrik/config.yaml` looks like this:

```yaml
# Output
output_dir: out
reporters:
  - html
  - sarif
  - junit
  - csv

# Standards packs — multi-framework compliance
standards_packs:
  - fda-iec-62304
  - owasp-top-10
  - hipaa
  - soc2

# Scan settings
scan_exclude:
  - "**/__pycache__/**"
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/out/**"
  - "**/.venv/**"
  - "**/recordings/**"
  - "**/docs/**"

# Gate thresholds
gate_fail_on:
  - critical
  - high

# DevOps integration — GitHub
devops_provider: github
github_owner: maxgerhardson
github_repo: sentrik-demo-medapi

# Governance
governance:
  profile: standard
  human_review_required:
    - on_critical_finding
    - on_requirement_change
  auto_patch:
    enabled: true
    max_severity: low
  gate:
    fail_on: [critical, high]
    block_merge_on_obligations: false
  audit:
    enabled: true
    log_file: out/agent_audit.jsonl

# Requirements traceability
requirement_coverage_enabled: true

# Performance
parallel_scan: false
cache_enabled: true
cache_dir: .guard_cache

# Severity rescoring (disabled initially — enabled in Phase 2)
severity_rescoring_enabled: false

# Confidence scoring
confidence_scoring_enabled: false
```

Key configuration points:

- **reporters** -- Four output formats generated on every scan (HTML for humans, SARIF for GitHub, JUnit for CI, CSV for spreadsheet export)
- **standards_packs** -- The four regulatory frameworks this project must comply with
- **scan_exclude** -- Paths that are not medical device software (build artifacts, docs, recordings)
- **gate_fail_on** -- Critical and high findings block the gate. Info-level documentation obligations do not block.
- **governance.profile** -- `standard` balances velocity with control. Other options: `strict` (every finding blocks) and `minimal` (advisory only).
- **requirement_coverage_enabled** -- Activates traceability checking between `requirements.yaml` and source code
- **severity_rescoring_enabled** -- Starts disabled; enabled later to demonstrate before/after rescoring

---

## Validating Configuration

Before scanning, verify the configuration is well-formed:

```
$ sentrik validate-config

  Configuration: .sentrik/config.yaml

  Validation Results:
    output_dir .............. ok (out/)
    reporters ............... ok (html, sarif, junit, csv)
    standards_packs ......... ok (4 packs, 136 rules)
    scan_exclude ............ ok (7 patterns)
    gate_fail_on ............ ok (critical, high)
    devops_provider ......... ok (github)
    governance .............. ok (standard profile)
    requirement_coverage .... ok (enabled)
    cache ................... ok (enabled, .guard_cache/)

  Result: VALID (0 errors, 0 warnings)
```

This catches typos, invalid pack names, conflicting settings, and missing
required fields before you waste time on a scan that would fail.

---

## License Status

Check your Sentrik license tier and what features are available:

```
$ sentrik license

  Sentrik License
  ───────────────────────────────────
  Tier:        Enterprise (Trial)
  Status:      Active
  Expires:     2026-04-26
  Org:         VitalSync Medical
  Seat:        engineering@vitalsync.example.com

  Features:
    Core scanning ........... included
    Free packs (8) .......... included
    Org packs (6) ........... included
    Dashboard ............... included
    REST API ................ included
    CI/CD integration ....... included
    Compliance reports ...... included
    Trust center ............ included
    Evidence export ......... included
    Custom packs ............ included
    RBAC .................... included
    MCP server .............. included

  All features available.
```

The trial enterprise license enables all features, including the
organization-tier packs (IEC 62304, HIPAA, SOC2) and enterprise features
(custom packs, RBAC, MCP server).

---

## Zero-Config Scanning

It is worth noting that Sentrik works with **no configuration at all**. If
you run `sentrik scan` in any project directory without a `.sentrik/config.yaml`,
Sentrik will:

1. Auto-detect the language and framework
2. Apply the `general-security` and `secrets` packs
3. Scan all source files
4. Output results to the terminal

The configuration file exists to customize behavior -- adding regulatory
packs, setting gate thresholds, excluding paths, enabling governance. But the
zero-config experience means a developer can get value from Sentrik in seconds,
before any setup.

---

## What Sentrik Did

- Auto-detected the project as Python/FastAPI with a layered architecture
- Suggested relevant standards packs based on code patterns (patient data keywords triggered HIPAA suggestion)
- Created a working configuration in one command
- Validated the configuration before the first scan
- Confirmed license tier and available features

## Without Sentrik

Setting up equivalent tooling from scratch typically requires:

- **SonarQube**: Install server, configure quality profiles, set up scanner, write `sonar-project.properties`
- **Snyk**: Create account, install CLI, authenticate, configure `.snyk` policy file
- **Semgrep**: Write or find rule packs, configure `.semgrep.yml`, tune for false positives
- **TruffleHog**: Install, configure patterns, set up pre-commit hooks
- **ArchUnit/deptry**: Write architecture tests in code, integrate into test suite
- **Custom scripts**: Build scripts to generate compliance reports from scan output

Each tool has its own configuration format, its own authentication, its own
output format, and its own CI integration. A conservative estimate for initial
setup is **2--3 days of engineering time**, plus ongoing maintenance as tools
update their configuration schemas.

With Sentrik, initial setup took **under 5 minutes**.

---

**Previous:** [01 - Requirements](01-requirements.md)
**Next:** [03 - First Scan](03-first-scan.md)
