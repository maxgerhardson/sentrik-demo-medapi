#!/usr/bin/env python3
"""Generate asciinema .cast recordings showing the Sentrik compliance journey.

Each recording shows the BEFORE state (findings, failures) followed by
the AFTER state (fixes, gate pass) to demonstrate the value of Sentrik.

The asciicast v2 format is:
  Line 1: JSON header {"version": 2, "width": 120, "height": 40, ...}
  Line 2+: [timestamp, "o", "text\r\n"]
"""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RECORDINGS_DIR = PROJECT_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)
TMPDIR = tempfile.gettempdir()

TYPE_SPEED = 0.04
PAUSE_AFTER = 1.2
CMD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1", "TERM": "dumb"}


def make_header(title, width=120, height=40):
    return json.dumps({
        "version": 2, "width": width, "height": height,
        "timestamp": int(time.time()),
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
        "title": title,
    })


def type_cmd(events, t, cmd):
    events.append([round(t, 3), "o", "\x1b[32m$\x1b[0m "])
    t += 0.1
    for ch in cmd:
        events.append([round(t, 3), "o", ch])
        t += TYPE_SPEED + (0.02 if ch == ' ' else 0)
    events.append([round(t, 3), "o", "\r\n"])
    return t + 0.3


def add_output(events, t, text, delay=0.015):
    for line in text.split('\n'):
        events.append([round(t, 3), "o", line + "\r\n"])
        t += delay
    return t


def add_title(events, t, title, subtitle=""):
    events.append([round(t, 3), "o",
        f"\x1b[1;36m# {title}\x1b[0m\r\n"])
    if subtitle:
        events.append([round(t + 0.1, 3), "o",
            f"\x1b[90m# {subtitle}\x1b[0m\r\n"])
    return t + 1.5


def add_section(events, t, label):
    events.append([round(t, 3), "o",
        f"\r\n\x1b[1;33m{'=' * 60}\x1b[0m\r\n"
        f"\x1b[1;33m  {label}\x1b[0m\r\n"
        f"\x1b[1;33m{'=' * 60}\x1b[0m\r\n\r\n"])
    return t + 1.0


def load(name):
    path = os.path.join(TMPDIR, f"{name}.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"(output not captured - run from {path})"


def write_cast(filename, title, events):
    path = RECORDINGS_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(make_header(title) + '\n')
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    duration = events[-1][0] if events else 0
    print(f"  {filename}: {len(events)} events, {duration:.0f}s")


def record_01():
    """Init & First Scan - shows the failing state."""
    events = []
    t = add_title(events, 0.5,
        "Sentrik Demo: Init & First Scan",
        "VitalSync Medical API - discovering compliance gaps")

    t = add_section(events, t, "STEP 1: What packs are available?")
    t = type_cmd(events, t, "sentrik list-packs")
    t = add_output(events, t,
        "PACK ID            SOURCE   STATUS    TIER   RULES  NAME\n"
        "------------------------------------------------------------------------\n"
        "fda-iec-62304      builtin  ENABLED   Free   31     FDA IEC 62304\n"
        "owasp-top-10       builtin  ENABLED   Free   69     OWASP Top 10\n"
        "soc2               builtin  ENABLED   Free   30     SOC2 Trust Services\n"
        "hipaa              builtin  ENABLED   Free   25     HIPAA Security Rule\n"
        "pci-dss            builtin  available Free   33     PCI DSS v4.0\n"
        "iso-27001          builtin  available Free   32     ISO 27001:2022\n"
        "...and 8 more packs\n"
        "\n"
        "Total: 14 pack(s), 4 enabled")
    t += PAUSE_AFTER

    t = add_section(events, t, "STEP 2: Scan the codebase")
    t = type_cmd(events, t, "sentrik scan")
    t = add_output(events, t,
        "Scan Complete\n"
        "  Severity    Count\n"
        "  \x1b[31mhigh         1558\x1b[0m\n"
        "  info           31\n"
        "\n"
        "  Compliance Score: \x1b[1;31m49.7%\x1b[0m\n"
        "  154 of 155 rules passed\n"
        "\n"
        "  File                    Findings\n"
        "  src/config.py                 38\n"
        "  src/main.py                   38\n"
        "  src/__init__.py               38\n"
        "  tests/test_alerts.py          38\n"
        "  tests/test_audit.py           38\n"
        "\n"
        "  ...and 1553 more critical/high finding(s).\n"
        "  1589 finding(s) written to out/", delay=0.025)
    t += PAUSE_AFTER

    t = add_section(events, t, "STEP 3: Can we pass the gate?")
    t = type_cmd(events, t, "sentrik gate")
    t = add_output(events, t,
        "  Compliance Score: \x1b[1;31m49.7%\x1b[0m | 154/155 rules\n"
        "\n"
        "  \x1b[1;31m+-------------------------------------------+\x1b[0m\n"
        "  \x1b[1;31m| GATE FAILED                               |\x1b[0m\n"
        "  \x1b[1;31m| high=1558                                 |\x1b[0m\n"
        "  \x1b[1;31m+-------------------------------------------+\x1b[0m\n"
        "\n"
        "  Fix 0 critical and 1558 high finding(s),\n"
        "  then re-run sentrik gate.")
    t += PAUSE_AFTER

    t = add_section(events, t, "STEP 4: What secrets are exposed?")
    t = type_cmd(events, t, "sentrik secrets")
    t = add_output(events, t,
        "  Secrets Detected (3 findings)\n"
        "  +-----------------------------------------------------------+\n"
        "  | Severity | File          | Line | Type          | Match   |\n"
        "  |----------+---------------+------+---------------+---------|\n"
        "  | \x1b[1;31mCRITICAL\x1b[0m | src/config.py |    7 | DB conn str   | post*** |\n"
        "  | \x1b[1;31mHIGH\x1b[0m     | src/config.py |    6 | Hardcoded pwd | admi*** |\n"
        "  | \x1b[1;31mHIGH\x1b[0m     | src/config.py |   10 | API key       | sk_t*** |\n"
        "  +-----------------------------------------------------------+\n"
        "\n"
        "  \x1b[31m1 critical, 2 high, 0 medium\x1b[0m")
    t += PAUSE_AFTER

    t = add_section(events, t, "STEP 5: Code complexity")
    t = type_cmd(events, t, "sentrik metrics")
    t = add_output(events, t,
        "  Code Metrics (top 10 of 48 files)\n"
        "  +-----------------------------------------------------------+\n"
        "  | File                      | Lines | Nesting | Functions   |\n"
        "  |---------------------------+-------+---------+-------------|\n"
        "  | services/vitals_process.. |   332 |       6 |          13 |\n"
        "  | services/alert_engine.py  |   151 |    \x1b[31m  14\x1b[0m |           6 |\n"
        "  | firmware/checksum.c       |    94 |       3 |           7 |\n"
        "  | api/routes/vitals.py      |    93 |       6 |           6 |\n"
        "  | client/util.js            |    71 |       4 |           5 |\n"
        "  +-----------------------------------------------------------+\n"
        "\n"
        "  48 files | 2,003 lines of code | 117 functions | \x1b[31mmax nesting: 14\x1b[0m")
    t += 1.5

    events.append([round(t, 3), "o",
        "\r\n\x1b[1;31m1,589 findings. Gate FAILED. 3 secrets. 19 CVEs. Nesting depth 14.\x1b[0m\r\n"
        "\x1b[90mNext: Fix & Gate \u2192 see how we resolve every finding\x1b[0m\r\n"])
    t += 3.0
    write_cast("01-init-and-scan.cast", "Sentrik: Init & First Scan (FAILING)", events)


def record_02():
    """Fix loop - from 1,558 findings to gate PASS."""
    events = []
    t = add_title(events, 0.5,
        "Sentrik Demo: Fix Findings & Pass Gate",
        "From 1,558 high findings to 100% compliance")

    t = add_section(events, t, "BEFORE: 1,558 high findings, gate FAILED")
    t = type_cmd(events, t, "sentrik gate  # before fixes")
    t = add_output(events, t,
        "  Compliance Score: \x1b[1;31m49.7%\x1b[0m | 154/155 rules passed\n"
        "  \x1b[1;31mGATE FAILED - high=1558\x1b[0m")
    t += PAUSE_AFTER

    t = add_section(events, t, "FIX 1: Add traceability headers to all source files")
    t = type_cmd(events, t, "head -1 src/main.py")
    t = add_output(events, t,
        "# REQUIREMENT: REQ-IEC-001, REQ-IEC-002 - Application entry point")
    t += 0.5
    t = type_cmd(events, t, "head -1 src/services/vitals_processor.py")
    t = add_output(events, t,
        "# REQUIREMENT: REQ-IEC-006, REQ-HIPAA-007 - Vitals processing")
    t += 0.5
    t = type_cmd(events, t, "head -1 src/db/database.py")
    t = add_output(events, t,
        "# REQUIREMENT: REQ-OWASP-001, REQ-HIPAA-001 - Database layer")
    t += 0.3
    t = type_cmd(events, t, "# ...added to all 41 source files (Python, C, JS)")
    t += PAUSE_AFTER

    t = add_section(events, t, "FIX 2: Suppress traceability on config/docs files")
    t = type_cmd(events, t, "cat .sentrik/suppressions.yaml | head -12")
    t = add_output(events, t,
        'suppressions:\n'
        '  - rule_id: "IEC62304-TRACE-001"\n'
        '    file_glob: "*.yaml"\n'
        '    reason: "YAML config files are not source code"\n'
        '    approved_by: "engineering@vitalsync.example.com"\n'
        '  - rule_id: "IEC62304-TRACE-001"\n'
        '    file_glob: "*.toml"\n'
        '    reason: "TOML config files are not source code"\n'
        '    approved_by: "engineering@vitalsync.example.com"')
    t += PAUSE_AFTER

    t = add_section(events, t, "AFTER: Rescan the fixed codebase")
    t = type_cmd(events, t, "sentrik scan")
    t = add_output(events, t,
        "Scan Complete\n"
        "  Severity    Count\n"
        "  info           31\n"
        "\n"
        "  Compliance Score: \x1b[1;32m100.0%\x1b[0m\n"
        "  155 of 155 rules passed\n"
        "\n"
        "  31 finding(s) written to out/")
    t += PAUSE_AFTER

    t = add_section(events, t, "DELTA: What changed between scans?")
    t = type_cmd(events, t, "sentrik compare")
    t = add_output(events, t,
        "          Delta Analysis\n"
        "  +----------------------------------+\n"
        "  |              | Count | Breakdown |\n"
        "  |--------------+-------+-----------|\n"
        "  | + New        |     0 |           |\n"
        "  | \x1b[1;32m- Resolved\x1b[0m   | \x1b[1;32m1,558\x1b[0m | 1558 high |\n"
        "  | = Unchanged  |    31 |           |\n"
        "  +----------------------------------+\n"
        "\n"
        "  \x1b[1;32mResolved: 1,558 finding(s) fixed\x1b[0m")
    t += PAUSE_AFTER

    t = add_section(events, t, "GATE CHECK: Do we pass now?")
    t = type_cmd(events, t, "sentrik gate")
    t = add_output(events, t,
        "  Compliance Score: \x1b[1;32m100.0%\x1b[0m | 155/155 rules\n"
        "\n"
        "  \x1b[1;32m+-------------------------------------------+\x1b[0m\n"
        "  \x1b[1;32m| GATE PASSED                               |\x1b[0m\n"
        "  \x1b[1;32m+-------------------------------------------+\x1b[0m\n"
        "\n"
        "  Gate passed! Ready to commit.")
    t += 2.0

    events.append([round(t, 3), "o",
        "\r\n\x1b[1;32m49.7% -> 100%. 1,558 findings resolved. Gate: PASSED.\x1b[0m\r\n"
        "\x1b[90mNext: Dependencies & CVEs \u2192 find and fix vulnerable packages\x1b[0m\r\n"])
    t += 3.0
    write_cast("02-fix-and-gate.cast", "Sentrik: Fix Findings & Pass Gate", events)


def record_03():
    """Dependencies & CVEs - SBOM, vulnerability scanning, auto-fix, licenses."""
    events = []
    t = add_title(events, 0.5,
        "Sentrik Demo: Dependencies & CVEs",
        "SBOM generation, vulnerability scanning, auto-fix, license compliance")

    t = add_section(events, t, "SBOM: What dependencies do we have?")
    t = type_cmd(events, t, "sentrik sbom")
    t = add_output(events, t,
        "SBOM (cyclonedx) written to out/sbom.json - 13 component(s)\n\n"
        "Include this SBOM in your release artifacts or share with customers")
    t += PAUSE_AFTER

    t = add_section(events, t, "CVE SCAN: Are any dependencies vulnerable?")
    t = type_cmd(events, t, "sentrik vulns")
    t = add_output(events, t,
        "Scanning 13 dependencies for known vulnerabilities...\n\n"
        "\x1b[1;31mFound 19 vulnerability(ies) in 5 of 13 packages\x1b[0m\n\n"
        "  \x1b[31m1 critical\x1b[0m | \x1b[31m5 high\x1b[0m | 6 medium | 7 low\n\n"
        "  +--------------------------------------------------------------+\n"
        "  | Package          | Version | Severity | Fixed In | Summary   |\n"
        "  |------------------+---------+----------+----------+-----------|\n"
        "  | python-jose      | 3.3.0   | \x1b[1;31mCRITICAL\x1b[0m | 3.4.0    | algo conf |\n"
        "  | python-multipart | 0.0.6   | \x1b[1;31mHIGH\x1b[0m     | 0.0.22   | file writ |\n"
        "  | python-multipart | 0.0.6   | \x1b[1;31mHIGH\x1b[0m     | 0.0.18   | DoS bound |\n"
        "  | python-multipart | 0.0.6   | \x1b[1;31mHIGH\x1b[0m     | 0.0.7    | ReDoS     |\n"
        "  | cryptography     | 42.0.0  | \x1b[1;31mHIGH\x1b[0m     | 46.0.5   | subgroup  |\n"
        "  | cryptography     | 42.0.0  | \x1b[1;31mHIGH\x1b[0m     | 42.0.4   | NULL der  |\n"
        "  | requests         | 2.25.0  | MEDIUM   | 2.33.0   | proxy lk  |\n"
        "  | ...and 12 more vulnerabilities                               |\n"
        "  +--------------------------------------------------------------+")
    t += PAUSE_AFTER

    t = add_section(events, t, "AUTO-FIX: One command to patch them all")
    t = type_cmd(events, t, "sentrik vulns --fix")
    t = add_output(events, t,
        "  Proposed Fixes\n"
        "  +--------------------------------------------------+\n"
        "  | Package          | Current | Fixed  | Manifest   |\n"
        "  |------------------+---------+--------+------------|\n"
        "  | cryptography     | 42.0.0  | \x1b[32m46.0.5\x1b[0m | pyproject  |\n"
        "  | python-jose      | 3.3.0   | \x1b[32m3.4.0\x1b[0m  | pyproject  |\n"
        "  | python-multipart | 0.0.6   | \x1b[32m0.0.22\x1b[0m | pyproject  |\n"
        "  | requests         | 2.25.0  | \x1b[32m2.33.0\x1b[0m | pyproject  |\n"
        "  +--------------------------------------------------+\n\n"
        "  \x1b[32mApplied 4 fix(es), 0 skipped.\x1b[0m")
    t += PAUSE_AFTER

    t = add_section(events, t, "VERIFY: Rescan after fix")
    t = type_cmd(events, t, "sentrik vulns")
    t = add_output(events, t,
        "Scanning 13 dependencies...\n\n"
        "\x1b[32mFound 1 vulnerability in 1 of 13 packages\x1b[0m\n\n"
        "  0 critical | 0 high | \x1b[33m1 medium\x1b[0m | 0 low\n\n"
        "\x1b[90m(fastapi - no version fix available yet)\x1b[0m")
    t += PAUSE_AFTER

    t = add_section(events, t, "LICENSE COMPLIANCE")
    t = type_cmd(events, t, "sentrik licenses")
    t = add_output(events, t,
        "Scanning 13 dependencies for license information...\n\n"
        "  +-----------------------------------------------------------+\n"
        "  | Package       | License       | Risk | Copyleft          |\n"
        "  |---------------+---------------+------+-------------------|\n"
        "  | fastapi       | MIT           | none | No                |\n"
        "  | sqlalchemy    | MIT           | none | No                |\n"
        "  | pydantic      | MIT           | none | No                |\n"
        "  | cryptography  | Apache-2.0    | none | No                |\n"
        "  | psycopg2      | LGPL          | \x1b[33mlow\x1b[0m  | No (with except.) |\n"
        "  | ...8 more     | MIT/BSD/Apache| none | No                |\n"
        "  +-----------------------------------------------------------+\n\n"
        "  \x1b[32mNo copyleft violations found.\x1b[0m")
    t += 2.0

    events.append([round(t, 3), "o",
        "\r\n\x1b[1;32m19 CVEs -> 1. Auto-fixed in one command. All licenses clean.\x1b[0m\r\n"
        "\x1b[90mNext: Reports & Evidence \u2192 generate compliance artifacts for auditors\x1b[0m\r\n"])
    t += 3.0
    write_cast("03-supply-chain.cast", "Sentrik: Dependencies & CVEs", events)


def record_04():
    """Compliance reports and evidence."""
    events = []
    t = add_title(events, 0.5,
        "Sentrik Demo: Compliance Reports & Evidence",
        "Per-framework reports, trust center, audit bundle, work items")

    t = add_section(events, t, "FRAMEWORK REPORTS")
    for fw in ["IEC 62304", "HIPAA", "OWASP Top 10", "SOC2"]:
        t = type_cmd(events, t, f'sentrik compliance-report --framework "{fw}"')
        slug = fw.lower().replace(" ", "-")
        t = add_output(events, t,
            f"Compliance report written to out/compliance-report-{slug}.html\n"
            f"  0 code finding(s), documentation obligation(s) tracked\n")
        t += 0.6

    t = add_section(events, t, "TRUST CENTER - public compliance page")
    t = type_cmd(events, t, 'sentrik trust-center --org "VitalSync Medical"')
    t = add_output(events, t,
        "Trust center page written to out/trust-center.html\n\n"
        "Share this page publicly or embed on your website")
    t += PAUSE_AFTER

    t = add_section(events, t, "EVIDENCE EXPORT - for auditors")
    t = type_cmd(events, t, "sentrik evidence-export --all")
    t = add_output(events, t,
        "Evidence report written to out/evidence-soc2.html\n"
        "Evidence report written to out/evidence-iec-62304.html\n"
        "Evidence report written to out/evidence-hipaa.html\n"
        "Evidence report written to out/evidence-owasp.html\n\n"
        "Share this evidence package with auditors")
    t += PAUSE_AFTER

    t = add_section(events, t, "AUDIT BUNDLE - complete submission package")
    t = type_cmd(events, t, "sentrik export-audit")
    t = add_output(events, t,
        "Audit bundle created: out/audit-bundle-2026-03-27.zip\n\n"
        "Share the audit bundle with your QA or regulatory team")
    t += PAUSE_AFTER

    t = add_section(events, t, "DEVOPS INTEGRATION - auto-create work items")
    t = type_cmd(events, t, "sentrik reconcile --dry-run")
    t = add_output(events, t,
        "[CREATE] IEC62304-5.1.1: software-development-plan\n"
        "[CREATE] IEC62304-5.3.1: architecture-documentation\n"
        "[CREATE] OWASP-A04-001: threat-model\n"
        "[CREATE] HIPAA-164.308-a1: risk-analysis\n"
        "[CREATE] HIPAA-164.308-a7: contingency-plan\n"
        "[CREATE] SOC2-CC8-001: change-management-policy\n"
        "...and 14 more\n\n"
        "Dry run: 20 action(s) would be taken.")
    t += 1.0
    t = type_cmd(events, t, "sentrik reconcile")
    t = add_output(events, t,
        "\x1b[32mReconcile complete: 20 created, 0 updated, 0 closed\x1b[0m\n"
        "20 work item(s) synced as GitHub Issues.")
    t += 2.0

    events.append([round(t, 3), "o",
        "\r\n\x1b[1;32mFull compliance evidence generated. 20 work items created.\x1b[0m\r\n"
        "\x1b[90mSee Full Lifecycle \u2192 the complete journey in one recording\x1b[0m\r\n"])
    t += 3.0
    write_cast("04-compliance.cast", "Sentrik: Compliance Reports & Evidence", events)


def record_05():
    """Full lifecycle - condensed end-to-end."""
    events = []
    t = add_title(events, 0.5,
        "Sentrik: Full Compliance Lifecycle",
        "From 1,589 findings to 100% compliance in minutes")

    # BEFORE
    t = add_section(events, t, "BEFORE - Initial scan of ungoverned codebase")
    t = type_cmd(events, t, "sentrik scan")
    t = add_output(events, t,
        "Scan Complete\n"
        "  Severity    Count\n"
        "  \x1b[31mhigh         1558\x1b[0m\n"
        "  info           31\n\n"
        "  Compliance Score: \x1b[1;31m49.7%\x1b[0m  (154/155 rules)")
    t += 0.8

    t = type_cmd(events, t, "sentrik gate")
    t = add_output(events, t,
        "  \x1b[1;31m+-------------------------------------------+\x1b[0m\n"
        "  \x1b[1;31m| GATE FAILED  |  high=1558                 |\x1b[0m\n"
        "  \x1b[1;31m+-------------------------------------------+\x1b[0m")
    t += 0.8

    t = type_cmd(events, t, "sentrik secrets")
    t = add_output(events, t,
        "  \x1b[31m3 secrets detected:\x1b[0m DB password, API key, connection string")
    t += 0.8

    t = type_cmd(events, t, "sentrik vulns")
    t = add_output(events, t,
        "  \x1b[31m19 vulnerabilities\x1b[0m in 5 packages (1 critical, 5 high)")
    t += PAUSE_AFTER

    # FIX
    t = add_section(events, t, "FIX - Traceability headers + dependency upgrades")
    t = type_cmd(events, t, "# Added REQUIREMENT headers to all 41 source files")
    t += 0.5
    t = type_cmd(events, t, "# Created .sentrik/suppressions.yaml for non-source files")
    t += 0.5
    t = type_cmd(events, t, "sentrik vulns --fix")
    t = add_output(events, t,
        "  \x1b[32mApplied 4 fix(es):\x1b[0m cryptography->46.0.5, python-jose->3.4.0,\n"
        "  python-multipart->0.0.22, requests->2.33.0")
    t += PAUSE_AFTER

    # AFTER
    t = add_section(events, t, "AFTER - Rescan the fixed codebase")
    t = type_cmd(events, t, "sentrik scan")
    t = add_output(events, t,
        "Scan Complete\n"
        "  Severity    Count\n"
        "  info           31\n\n"
        "  Compliance Score: \x1b[1;32m100.0%\x1b[0m  (155/155 rules)")
    t += 0.8

    t = type_cmd(events, t, "sentrik gate")
    t = add_output(events, t,
        "  \x1b[1;32m+-------------------------------------------+\x1b[0m\n"
        "  \x1b[1;32m| GATE PASSED                               |\x1b[0m\n"
        "  \x1b[1;32m+-------------------------------------------+\x1b[0m")
    t += 0.8

    t = type_cmd(events, t, "sentrik compare")
    t = add_output(events, t,
        "  \x1b[32mResolved: 1,558 finding(s)\x1b[0m | New: 0 | Unchanged: 31 (info)")
    t += 0.8

    t = type_cmd(events, t, "sentrik vulns")
    t = add_output(events, t,
        "  \x1b[32m1 remaining\x1b[0m (medium, no fix available) | 19 -> 1 CVEs")
    t += PAUSE_AFTER

    # COMPLIANCE
    t = add_section(events, t, "SHIP - Generate compliance artifacts")
    t = type_cmd(events, t, 'sentrik compliance-report --framework "HIPAA"')
    t = add_output(events, t, "  Compliance report -> out/compliance-report-hipaa.html")
    t += 0.4
    t = type_cmd(events, t, 'sentrik trust-center --org "VitalSync Medical"')
    t = add_output(events, t, "  Trust center -> out/trust-center.html")
    t += 0.4
    t = type_cmd(events, t, "sentrik export-audit")
    t = add_output(events, t, "  Audit bundle -> out/audit-bundle-2026-03-27.zip")
    t += 0.4
    t = type_cmd(events, t, "sentrik reconcile")
    t = add_output(events, t, "  \x1b[32m20 GitHub Issues created from findings\x1b[0m")
    t += 1.5

    # SUMMARY TABLE
    events.append([round(t, 3), "o",
        "\r\n"
        "\x1b[1;36m+-----------------------------------------------------+\x1b[0m\r\n"
        "\x1b[1;36m|  BEFORE              ->  AFTER                       |\x1b[0m\r\n"
        "\x1b[1;36m|  Compliance: \x1b[31m49.7%\x1b[1;36m    ->  \x1b[32m100%\x1b[1;36m                        |\x1b[0m\r\n"
        "\x1b[1;36m|  Findings:  \x1b[31m1,558\x1b[1;36m     ->  \x1b[32m0 blocking\x1b[1;36m                  |\x1b[0m\r\n"
        "\x1b[1;36m|  CVEs:      \x1b[31m19\x1b[1;36m         ->  \x1b[32m1 (medium)\x1b[1;36m                  |\x1b[0m\r\n"
        "\x1b[1;36m|  Gate:      \x1b[31mFAILED\x1b[1;36m     ->  \x1b[32mPASSED\x1b[1;36m                     |\x1b[0m\r\n"
        "\x1b[1;36m|  Secrets:   \x1b[31m3 found\x1b[1;36m    ->  \x1b[33mtracked\x1b[1;36m                    |\x1b[0m\r\n"
        "\x1b[1;36m|  Work items: \x1b[31m0\x1b[1;36m         ->  \x1b[32m20 auto-created\x1b[1;36m             |\x1b[0m\r\n"
        "\x1b[1;36m+-----------------------------------------------------+\x1b[0m\r\n"
        "\r\n"
        "\x1b[1;32mOne tool. Full compliance lifecycle.\x1b[0m\r\n"
        "\x1b[90mhttps://sentrik.dev\x1b[0m\r\n"])
    t += 5.0
    write_cast("05-full-lifecycle.cast", "Sentrik: Full Compliance Lifecycle", events)


if __name__ == "__main__":
    print("Generating asciinema recordings...\n")
    record_01()
    record_02()
    record_03()
    record_04()
    record_05()
    print(f"\nAll recordings in {RECORDINGS_DIR}/")
    print("Play: asciinema play recordings/05-full-lifecycle.cast")
    print("View: python -m http.server 9090 (from recordings/)")
