# Sentrik Demo Storyboard

> **Audience:** Prospects, investors, design partners
> **Project:** VitalSync Medical API — a FastAPI service for patient vitals from wearable devices
> **Regulations:** IEC 62304 (medical device), HIPAA (healthcare), OWASP Top 10 (security), SOC 2 (trust)

---

## Act 1: The Problem (2 minutes)

### Scene 1: AI writes code fast. Compliance can't keep up.

Your team uses AI coding agents. They generate code in minutes. But that code needs to comply with IEC 62304, HIPAA, OWASP, and SOC 2 — simultaneously.

**Without Sentrik**, you need 8-12 tools, manual checklists, and 6+ weeks to prepare audit evidence. When the auditor asks "show me where you encrypt patient data at rest," someone has to dig through git history.

### Scene 2: One command changes everything.

```bash
npm install -g sentrik
cd vitalsync-medical-api
sentrik init --no-interactive
sentrik scan
```

In 30 seconds, Sentrik auto-detects your project, loads 7 standards packs (526 rules), and scans every file.

---

## Act 2: Scan and Fix (5 minutes)

### Scene 3: First scan — see what's wrong

```bash
$ sentrik scan

Findings: 193 total
  critical: 7    high: 28    medium: 84    low: 52    info: 22

Gate: FAILED (7 critical, 28 high)
```

Every finding maps to a specific regulatory clause:
- `OWASP-A02-001` (A02:2021) — MD5 hashing in `encryption_service.py:45`
- `HIPAA-164.312-a1` (§164.312(a)(1)) — Missing access control on `/patients` endpoint
- `IEC62304-CODE-003` (§5.5.3) — Hardcoded credentials in `config.py:12`

### Scene 4: Risk scores on every finding

Every finding now includes a risk score:
```json
{
  "rule_id": "OWASP-A02-001",
  "severity": "high",
  "risk_score": {
    "score": 0.72,
    "exploitability": 0.85,
    "blast_radius": 0.65,
    "data_sensitivity": 0.6
  }
}
```

Prioritize by actual risk, not just severity labels.

### Scene 5: Fix with AI

Open the dashboard, click any finding, and click **"Fix with AI"**:

```bash
sentrik dashboard
```

The AI chat panel explains the vulnerability, suggests a fix, and can apply it directly. Compliance officers triage findings without touching an IDE.

### Scene 6: Auto-fix and re-scan

```bash
sentrik apply-patches        # Auto-fix what we can
sentrik scan                 # Re-scan
sentrik compare              # See what changed

Delta: 47 resolved, 146 remaining
```

### Scene 7: Gate passes

After fixing critical and high findings:

```bash
$ sentrik gate

Gate: PASSED
  critical: 0    high: 0    medium: 31    low: 52    info: 22
```

---

## Act 3: Evidence and Proof (3 minutes)

### Scene 8: Compliance Evidence Map

**This is the differentiator.** Most tools only show violations. Sentrik shows where your code *satisfies* requirements.

```bash
$ sentrik compliance-map

Compliance Evidence Map
  Coverage: 81.4%
  Met: 79    Violated: 18    Manual: 0    N/A: 33
```

The dashboard Evidence Map tab shows every rule with its status:
- **MET** — `HIPAA-164.312-b`: Audit logging found in `middleware/audit.py:14`
- **MET** — `OWASP-A01-001`: No wildcard CORS across 43 files
- **VIOLATED** — `OWASP-A02-001`: MD5 still used in 3 files
- **MET** — `IEC62304-DOC-001`: Risk management documentation found in `docs/risk-analysis.adoc`

When the auditor asks "show me where you implement audit logging," you point them here.

### Scene 9: Per-framework compliance reports

```bash
sentrik compliance-report -f "HIPAA"
sentrik compliance-report -f "IEC 62304"
sentrik trust-center --org "VitalSync Medical"
sentrik attest
```

Each report maps findings to specific regulatory clauses. The trust center is a public-safe HTML page. The attestation is cryptographically signed (HMAC-SHA256).

### Scene 10: Evidence export for auditors

```bash
sentrik auditor create --name "Jane Smith" --email jane@auditor.com
# → Auditor portal URL with token-based access

sentrik evidence-export -f "HIPAA"
# → ZIP bundle with findings, reports, attestation, scan history
```

The auditor gets a read-only portal with everything they need. No access to your codebase.

---

## Act 4: Supply Chain (2 minutes)

### Scene 11: SBOM, CVEs, and licenses

```bash
sentrik sbom               # CycloneDX SBOM
sentrik vulns               # 19 CVEs found
sentrik vulns --fix         # Auto-bump to patched versions
sentrik licenses            # Flag copyleft dependencies
sentrik secrets             # 3 hardcoded secrets detected
```

### Scene 12: Continuous monitoring

```bash
sentrik watch --vulns --fix --create-pr
```

Runs in the background. When a new CVE hits your dependencies, Sentrik auto-fixes and creates a PR.

---

## Act 5: CI/CD and Integrations (2 minutes)

### Scene 13: One-line GitHub Action

```yaml
# .github/workflows/sentrik.yml
- uses: maxgerhardson/sentrik-community@v1
```

The gate runs on every PR. SARIF uploads to GitHub Code Scanning. Findings appear as PR comments.

### Scene 14: AI agent integration (MCP)

```bash
sentrik mcp-server
```

Claude Code, Cursor, and Cline call Sentrik via MCP. The AI checks compliance rules *before* writing code — so generated code passes the gate on the first try.

### Scene 15: VS Code extension

Install from the VS Code Marketplace. Scans on save, findings sidebar, quick fixes, quality score in status bar. "Open Dashboard" launches the full compliance dashboard.

---

## Act 6: Intelligence (2 minutes)

### Scene 16: Quality score

```bash
$ sentrik quality-score --verbose

Overall Score: 53/100
  compliance:     0/100  (79 code findings)
  complexity:    80/100  (manageable)
  test_coverage: 45/100  (needs work)
  documentation: 60/100  (partial)
  consistency:   85/100  (good)
  dep_health:    50/100  (19 CVEs)
```

Track over time. Set minimum thresholds in the gate.

### Scene 17: STRIDE threat modeling

```bash
sentrik threat-model --file src/api/routes/patients.py
```

AI-powered STRIDE analysis: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. Filter by category, discuss mitigations with AI, track remediation.

### Scene 18: Expertise tracking

```bash
sentrik check-expertise --git-range HEAD~10..HEAD
```

When a PR touches code outside someone's expertise, Sentrik flags it for senior review. Builds developer profiles from git history.

---

## Act 7: The Pitch (1 minute)

### Without Sentrik
- 8-12 tools, $75K-260K/year
- 6 weeks per audit
- Manual checklists and spreadsheets
- No visibility into AI-generated code compliance

### With Sentrik
- One CLI, one dashboard, one CI step
- 22 frameworks, 526 rules
- Compliance evidence generated on every commit
- Free tier: 5 packs, 158 rules, forever

```bash
npm install -g sentrik
sentrik scan
```

---

## Running This Demo

### Prerequisites
```bash
git clone https://github.com/maxgerhardson/sentrik-demo-medapi
cd sentrik-demo-medapi
npm install -g sentrik
```

### Tag-based walkthrough
```bash
git checkout v0.1-requirements    # Flawed code with violations
sentrik scan                      # See 193 findings, gate fails

git checkout v1.0-compliant       # Fixed code
sentrik scan                      # Gate passes

git checkout v2.0-demo-complete   # Full demo with all features
sentrik dashboard                 # Open full dashboard
```

### Key commands for live demo
```bash
sentrik scan                      # Core scan
sentrik gate                      # Gate check
sentrik compliance-map            # Evidence map (NEW)
sentrik quality-score --verbose   # Quality score
sentrik vulns                     # CVE scan
sentrik trust-center --org "VitalSync" # Public trust center
sentrik dashboard                 # Full dashboard with all tabs
```

### Dashboard tabs to show
1. **Overview** — compliance score, severity chart
2. **Evidence Map** — where code satisfies requirements (KEY DIFFERENTIATOR)
3. **Findings** — click one, show "Fix with AI"
4. **Vulnerabilities** — CVE list
5. **Quality Score** — 6 dimensions
6. **Threat Model** — STRIDE analysis
