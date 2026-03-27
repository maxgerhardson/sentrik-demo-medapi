#!/usr/bin/env python3
"""Generate asciinema .cast recordings from real Sentrik command output.

The asciicast v2 format is:
  Line 1: JSON header {"version": 2, "width": 120, "height": 40, ...}
  Line 2+: [timestamp, "o", "text\r\n"]

This script runs actual sentrik commands, captures output with timing,
and writes .cast files that can be played with `asciinema play` or
embedded on web pages with the asciinema player JS widget.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RECORDINGS_DIR = PROJECT_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

# Typing speed simulation (seconds per character)
TYPE_SPEED = 0.04
# Pause after command output before next prompt
PAUSE_AFTER = 1.0
# Pause before typing next command
PAUSE_BEFORE = 0.5


def make_header(title: str, width: int = 120, height: int = 40) -> str:
    return json.dumps({
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(time.time()),
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
        "title": title,
    })


def type_command(events: list, t: float, cmd: str) -> float:
    """Simulate typing a command character by character."""
    # Show prompt
    events.append([round(t, 3), "o", "\x1b[32m$\x1b[0m "])
    t += 0.1
    # Type each character
    for ch in cmd:
        events.append([round(t, 3), "o", ch])
        t += TYPE_SPEED + (0.02 if ch == ' ' else 0)
    # Press enter
    events.append([round(t, 3), "o", "\r\n"])
    t += 0.2
    return t


def add_output(events: list, t: float, output: str, line_delay: float = 0.02) -> float:
    """Add command output line by line with small delays."""
    for line in output.split('\n'):
        events.append([round(t, 3), "o", line + "\r\n"])
        t += line_delay
    return t


def add_blank(events: list, t: float, pause: float = 0.5) -> float:
    """Add a blank line / pause."""
    events.append([round(t, 3), "o", "\r\n"])
    return t + pause


def run_command(cmd: str, cwd: str = None) -> str:
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            cwd=cwd or str(PROJECT_DIR), timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
        )
        # Decode as utf-8 with replacement for any bad bytes
        output = result.stdout.decode("utf-8", errors="replace")
        if not output.strip() and result.stderr:
            output = result.stderr.decode("utf-8", errors="replace")
        # Clean up Windows paths and box-drawing artifacts for display
        output = output.replace('\\', '/')
        return output.strip()
    except Exception as e:
        return f"(output captured separately — {e})"


def write_cast(filename: str, title: str, events: list):
    """Write a .cast file."""
    path = RECORDINGS_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(make_header(title) + '\n')
        for event in events:
            f.write(json.dumps(event) + '\n')
    print(f"  Wrote {path} ({len(events)} events, {events[-1][0]:.1f}s)")


def record_01_init_and_scan():
    """Recording 1: Project init and first scan."""
    print("Recording 01: Init and First Scan...")
    events = []
    t = 0.5

    # Title card
    events.append([round(t, 3), "o",
        "\x1b[1;36m# Sentrik Demo: Init & First Scan\x1b[0m\r\n"
        "\x1b[90m# VitalSync Medical API — IEC 62304 + HIPAA + OWASP + SOC2\x1b[0m\r\n"])
    t += 2.0

    # sentrik license
    t = type_command(events, t, "sentrik license")
    output = run_command("sentrik license")
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # sentrik list-packs
    t = type_command(events, t, "sentrik list-packs")
    output = run_command("sentrik list-packs")
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # sentrik scan
    t = type_command(events, t, "sentrik scan")
    output = run_command("sentrik scan")
    t = add_output(events, t, output, line_delay=0.03)
    t += PAUSE_AFTER

    # sentrik gate
    t = type_command(events, t, "sentrik gate")
    output = run_command("sentrik gate")
    t = add_output(events, t, output, line_delay=0.03)
    t += PAUSE_AFTER

    # sentrik metrics
    t = type_command(events, t, "sentrik metrics")
    output = run_command("sentrik metrics")
    t = add_output(events, t, output, line_delay=0.02)
    t += PAUSE_AFTER

    # sentrik secrets
    t = type_command(events, t, "sentrik secrets")
    output = run_command("sentrik secrets")
    t = add_output(events, t, output)
    t += 2.0

    write_cast("01-init-and-scan.cast", "Sentrik Demo: Init & First Scan", events)


def record_02_fix_and_gate():
    """Recording 2: Fix loop and gate pass."""
    print("Recording 02: Fix Loop & Gate Pass...")
    events = []
    t = 0.5

    events.append([round(t, 3), "o",
        "\x1b[1;36m# Sentrik Demo: Fix Findings & Pass Gate\x1b[0m\r\n"
        "\x1b[90m# Adding traceability headers + suppressions\x1b[0m\r\n"])
    t += 2.0

    # Show a sample fix
    t = type_command(events, t, "head -2 src/main.py")
    events.append([round(t, 3), "o",
        "# REQUIREMENT: REQ-IEC-001, REQ-IEC-002 — Application entry point and configuration\r\n"
        '"""VitalSync Medical API — Patient Vitals Ingestion Service.\r\n'])
    t += PAUSE_AFTER

    # Show suppressions
    t = type_command(events, t, "cat .sentrik/suppressions.yaml | head -15")
    events.append([round(t, 3), "o",
        "suppressions:\r\n"
        '  - rule_id: "IEC62304-TRACE-001"\r\n'
        '    file_glob: "*.yaml"\r\n'
        '    reason: "YAML configuration files are not source code"\r\n'
        '    approved_by: "engineering@vitalsync.example.com"\r\n'
        '  - rule_id: "IEC62304-TRACE-001"\r\n'
        '    file_glob: "*.toml"\r\n'
        '    reason: "TOML configuration files are not source code"\r\n'
        '    approved_by: "engineering@vitalsync.example.com"\r\n'])
    t += PAUSE_AFTER

    # sentrik scan (after fix)
    t = type_command(events, t, "sentrik scan")
    output = run_command("sentrik scan")
    t = add_output(events, t, output, line_delay=0.03)
    t += PAUSE_AFTER

    # sentrik compare
    t = type_command(events, t, "sentrik compare")
    output = run_command("sentrik compare")
    t = add_output(events, t, output, line_delay=0.03)
    t += PAUSE_AFTER

    # sentrik gate
    t = type_command(events, t, "sentrik gate")
    output = run_command("sentrik gate")
    t = add_output(events, t, output, line_delay=0.03)
    t += 2.0

    write_cast("02-fix-and-gate.cast", "Sentrik Demo: Fix Findings & Pass Gate", events)


def record_03_supply_chain():
    """Recording 3: Supply chain security."""
    print("Recording 03: Supply Chain Security...")
    events = []
    t = 0.5

    events.append([round(t, 3), "o",
        "\x1b[1;36m# Sentrik Demo: Supply Chain Security\x1b[0m\r\n"
        "\x1b[90m# SBOM, CVE scanning, license compliance\x1b[0m\r\n"])
    t += 2.0

    # sentrik sbom
    t = type_command(events, t, "sentrik sbom")
    output = run_command("sentrik sbom")
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # sentrik vulns
    t = type_command(events, t, "sentrik vulns")
    output = run_command("sentrik vulns")
    t = add_output(events, t, output, line_delay=0.02)
    t += PAUSE_AFTER

    # sentrik licenses
    t = type_command(events, t, "sentrik licenses")
    output = run_command("sentrik licenses")
    t = add_output(events, t, output, line_delay=0.02)
    t += PAUSE_AFTER

    # sentrik secrets
    t = type_command(events, t, "sentrik secrets")
    output = run_command("sentrik secrets")
    t = add_output(events, t, output)
    t += 2.0

    write_cast("03-supply-chain.cast", "Sentrik Demo: Supply Chain Security", events)


def record_04_compliance():
    """Recording 4: Compliance reports and evidence."""
    print("Recording 04: Compliance Reports...")
    events = []
    t = 0.5

    events.append([round(t, 3), "o",
        "\x1b[1;36m# Sentrik Demo: Compliance Reports & Evidence\x1b[0m\r\n"
        "\x1b[90m# Per-framework reports, trust center, audit bundle\x1b[0m\r\n"])
    t += 2.0

    # compliance-report for each framework
    for framework in ["IEC 62304", "HIPAA", "OWASP Top 10", "SOC2"]:
        t = type_command(events, t, f'sentrik compliance-report --framework "{framework}"')
        output = run_command(f'sentrik compliance-report --framework "{framework}"')
        t = add_output(events, t, output)
        t += 0.8

    # trust-center
    t = type_command(events, t, 'sentrik trust-center --org "VitalSync Medical"')
    output = run_command('sentrik trust-center --org "VitalSync Medical"')
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # evidence-export
    t = type_command(events, t, "sentrik evidence-export --all")
    output = run_command("sentrik evidence-export --all")
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # export-audit
    t = type_command(events, t, "sentrik export-audit")
    output = run_command("sentrik export-audit")
    t = add_output(events, t, output)
    t += PAUSE_AFTER

    # List output files
    t = type_command(events, t, "ls -la out/*.html out/*.zip")
    events.append([round(t, 3), "o",
        "compliance-report-hipaa.html\r\n"
        "compliance-report-iec-62304.html\r\n"
        "compliance-report-owasp-top-10.html\r\n"
        "compliance-report-soc2.html\r\n"
        "evidence-hipaa.html\r\n"
        "evidence-iec-62304.html\r\n"
        "evidence-owasp.html\r\n"
        "evidence-soc2.html\r\n"
        "trust-center.html\r\n"
        "audit-bundle-2026-03-27.zip\r\n"])
    t += 2.0

    write_cast("04-compliance.cast", "Sentrik Demo: Compliance Reports & Evidence", events)


def record_05_full_lifecycle():
    """Recording 5: Condensed end-to-end demo."""
    print("Recording 05: Full Lifecycle (condensed)...")
    events = []
    t = 0.5

    events.append([round(t, 3), "o",
        "\x1b[1;36m# Sentrik Demo: Full Compliance Lifecycle\x1b[0m\r\n"
        "\x1b[90m# From scan to gate to compliance artifacts — in under 3 minutes\x1b[0m\r\n"])
    t += 2.0

    # Step 1: Scan
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 1: Scan ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, "sentrik scan")
    output = run_command("sentrik scan")
    t = add_output(events, t, output, line_delay=0.02)
    t += 0.8

    # Step 2: Gate
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 2: Gate ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, "sentrik gate")
    output = run_command("sentrik gate")
    t = add_output(events, t, output, line_delay=0.02)
    t += 0.8

    # Step 3: Supply chain
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 3: Supply Chain ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, "sentrik vulns")
    output = run_command("sentrik vulns")
    # Truncate long output
    lines = output.split('\n')
    short = '\n'.join(lines[:8] + ['  ...'] + lines[-3:])
    t = add_output(events, t, short, line_delay=0.02)
    t += 0.8

    # Step 4: Compliance
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 4: Compliance Reports ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, 'sentrik compliance-report --framework "HIPAA"')
    output = run_command('sentrik compliance-report --framework "HIPAA"')
    t = add_output(events, t, output)
    t += 0.5
    t = type_command(events, t, 'sentrik trust-center --org "VitalSync Medical"')
    output = run_command('sentrik trust-center --org "VitalSync Medical"')
    t = add_output(events, t, output)
    t += 0.8

    # Step 5: DevOps
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 5: DevOps Integration ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, "sentrik reconcile --dry-run")
    output = run_command("sentrik reconcile --dry-run")
    t = add_output(events, t, output, line_delay=0.02)
    t += 0.8

    # Step 6: Metrics
    events.append([round(t, 3), "o", "\x1b[1;33m--- Step 6: Code Metrics ---\x1b[0m\r\n"])
    t += 0.5
    t = type_command(events, t, "sentrik metrics")
    output = run_command("sentrik metrics")
    t = add_output(events, t, output, line_delay=0.01)
    t += 1.0

    # Final summary
    events.append([round(t, 3), "o",
        "\r\n\x1b[1;32mDone! Full compliance lifecycle in a single tool.\x1b[0m\r\n"
        "\x1b[90mLearn more: https://sentrik.dev\x1b[0m\r\n"])
    t += 3.0

    write_cast("05-full-lifecycle.cast", "Sentrik Demo: Full Compliance Lifecycle", events)


if __name__ == "__main__":
    print("Generating asciinema recordings...\n")
    record_01_init_and_scan()
    record_02_fix_and_gate()
    record_03_supply_chain()
    record_04_compliance()
    record_05_full_lifecycle()
    print(f"\nAll recordings written to {RECORDINGS_DIR}/")
    print("Play with: asciinema play recordings/01-init-and-scan.cast")
    print("Embed with: <script src='https://asciinema.org/a/X.js'></script>")
