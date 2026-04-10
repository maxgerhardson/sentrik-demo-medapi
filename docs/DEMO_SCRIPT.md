# Sentrik Demo Script

> Read this word for word. Every command is meant to be run live. Pause where indicated.

---

## Opening (30 seconds)

"Thanks for joining. Today I'm going to show you Sentrik — a tool that solves a problem every engineering team using AI is about to face.

AI coding agents like Claude Code and Cursor are writing more code than ever. But that code still needs to comply with regulations — HIPAA, SOC 2, OWASP, IEC 62304, PCI-DSS — depending on your industry. Right now, teams are catching compliance issues weeks or months after the code ships, usually when an auditor finds it.

Sentrik catches it before the code merges. And it doesn't just find what's wrong — it proves what's right. Let me show you."

---

## Part 1: Setup (1 minute)

"I'm going to use a real project — VitalSync Medical API. It's a FastAPI service that ingests patient vital signs from wearable medical devices. It handles heart rate, blood pressure, oxygen saturation, temperature — all protected health information under HIPAA.

This project sits at the intersection of four regulations: IEC 62304 for medical device software, HIPAA for patient data protection, OWASP Top 10 for web security, and SOC 2 for trust services.

Let me install Sentrik and scan this project."

**Run:**
```bash
npm install -g sentrik
```

*Wait for install to finish.*

"That's it. One install. Now let me scan."

---

## Part 2: First Scan (2 minutes)

**Run:**
```bash
sentrik scan
```

*Wait for scan to complete. Point at the output.*

"So Sentrik just scanned every file in this project against 526 rules from 7 different regulatory frameworks. It took about 30 seconds.

Let me point out a few things in the results.

First — the severity breakdown. We have critical findings, high findings, medium, low. The critical and high ones are what block you from merging.

Second — every finding maps to a specific regulatory clause. This isn't just 'you have a bug.' It's 'you're violating HIPAA section 164.312, paragraph a, subparagraph 1 — access control.' That's what auditors care about.

Let me show you some specific findings."

**Run:**
```bash
sentrik next-action -n 5
```

*Point at the output.*

"Sentrik tells you exactly what to fix first, which file, which line, and how to fix it. Now let me run the gate — this is what would run in your CI pipeline."

**Run:**
```bash
sentrik gate
```

*Point at GATE FAILED.*

"Gate failed. Seven critical findings, twenty-eight high. This PR would be blocked. No non-compliant code ships."

---

## Part 3: The Dashboard (3 minutes)

"Now let me show you the dashboard. This is what your compliance team lives in."

**Run:**
```bash
sentrik dashboard
```

*Wait for Edge to open in app mode. Navigate to Overview tab.*

"This is the overview. You can see the compliance score, finding counts by severity, gate status. That red banner at the top — that's the governance system telling you human review is required before this can merge.

Let me click into findings."

*Click Findings tab.*

"Here's every finding. I can filter by severity — let me click Critical."

*Click Critical pill.*

"Seven critical findings. Each one shows the rule ID, the file, the line number, the regulatory clause. Let me click one."

*Click a finding to expand it.*

"See this — it shows the code snippet, explains why this is a violation, and gives you remediation guidance. But watch this."

*Click 'Fix with AI' button on a finding.*

"I just opened an AI chat about this specific finding. I can ask it to explain the vulnerability, suggest a fix, or generate the corrected code. Compliance officers can triage findings without opening an IDE."

*Close chat panel.*

---

## Part 4: Evidence Map — The Differentiator (3 minutes)

"Now I want to show you the feature that no other tool has."

*Click Evidence Map tab.*

"This is the Compliance Evidence Map. Every other security tool tells you what's wrong. Sentrik also tells you what's right.

Look at the summary — coverage percentage, requirements met, violated, manual review, not applicable.

Now look at the table. Each row is a regulatory requirement. The green 'MET' badges show where your code satisfies the requirement — with the exact file and line number.

For example..."

*Point at a MET row.*

"This HIPAA requirement for audit logging — Sentrik found that audit logging is implemented in the audit middleware, line 14. It matched the pattern. That's not a finding — that's proof of compliance.

And this one..."

*Point at another MET row, ideally a documentation_obligation.*

"This documentation obligation — Sentrik searched through our markdown and AsciiDoc files and found that risk management is documented. It matched keywords in the actual document content.

Why does this matter? Because when an auditor asks 'show me where you implement encryption at rest' or 'show me your risk management documentation,' you don't dig through git history. You open this page.

Let me filter by framework."

*Select a framework from the dropdown.*

"Now I'm only seeing OWASP rules. Green, green, green — and two violations we need to fix. This is audit evidence generated automatically on every scan."

---

## Part 5: Supply Chain (1 minute)

"Let me show you supply chain security. This is built in — no extra tools."

**Run (or show in dashboard Vulnerabilities tab):**
```bash
sentrik vulns
```

*Point at CVE list.*

"Sentrik scanned every dependency against the OSV vulnerability database. It found CVEs with severity levels and — importantly — the fix version. I can auto-fix these."

**Run:**
```bash
sentrik sbom
```

"That generated a CycloneDX Software Bill of Materials. Required for FDA submissions and many enterprise contracts.

And I can set up continuous monitoring:"

```bash
sentrik watch --vulns --fix --create-pr
```

"This runs in the background. When a new CVE hits one of my dependencies, Sentrik auto-bumps the version and creates a pull request. Like Dependabot, but integrated with your compliance layer."

---

## Part 6: CI/CD Integration (1 minute)

"Getting this into your CI pipeline is one line."

*Show the GitHub Action:*

```yaml
- uses: maxgerhardson/sentrik-community@v1
```

"That's the Sentrik GitHub Action. It installs the tool, runs the gate, uploads SARIF results to GitHub Code Scanning, and attaches the findings report as an artifact. It auto-detects PR context — no configuration needed.

We also have a VS Code extension on the Marketplace. It scans on every save, shows findings inline in the editor, and has a button to open this dashboard directly from your IDE.

And for AI coding agents — Claude Code, Cursor, Cline — Sentrik runs as an MCP server. The AI checks compliance rules before writing code, so the generated code passes the gate on the first try."

---

## Part 7: Compliance Reports (1 minute)

"Let me show you what you hand to an auditor."

**Run:**
```bash
sentrik trust-center --org "VitalSync Medical"
```

*Open the HTML file.*

"This is a public-safe trust center page. Compliance scores by framework, no code paths exposed. You embed this on your website.

For a full audit:"

**Run:**
```bash
sentrik attest
```

"That generated a cryptographically signed attestation — HMAC-SHA256. Tamper-evident. Auditors can verify the signature.

And I can create a read-only portal for the auditor:"

**Run:**
```bash
sentrik auditor create --name "Jane Smith" --email jane@auditor.com
```

*Point at the URL.*

"I send that URL to the auditor. They get a read-only view of findings, compliance reports, and evidence — without access to our codebase. Token expires in 48 hours."

---

## Part 8: Quality and Intelligence (1 minute)

"One more thing. Sentrik doesn't just check compliance — it understands your code."

*Click Quality Score tab in dashboard.*

"Quality score — zero to one hundred across six dimensions. Compliance, complexity, test coverage, documentation, consistency, dependency health. You can set a minimum threshold in the gate.

And this..."

*Click Threat Model tab if populated, otherwise run:*
```bash
sentrik threat-model --file src/api/routes/patients.py
```

"STRIDE threat modeling. Sentrik analyzes your code for spoofing, tampering, information disclosure, denial of service, and elevation of privilege threats. Each one can be discussed with AI and tracked to resolution."

---

## Closing (30 seconds)

"So to recap — Sentrik replaces 8 to 12 tools with one CLI command. It scans against 22 regulatory frameworks with 526 rules. It gates every PR in CI. It generates audit evidence automatically. And with the Evidence Map, it proves where your code satisfies each requirement — not just where it fails.

The free tier includes five standards packs with 158 rules. No credit card, no time limit. Install it, scan your project, and see what it finds.

```bash
npm install -g sentrik
sentrik scan
```

Any questions?"

---

## Cheat Sheet for Q&A

| Question | Answer |
|----------|--------|
| "How long does a scan take?" | 10-30 seconds for a typical project. |
| "Does it work offline?" | Yes. HMAC-based license validation, no phone-home. |
| "What languages?" | Python, JavaScript, TypeScript, Go, PHP, Kotlin, C/C++, Java, Rust, Swift, and more. Rules are regex-based so they work on any text file. |
| "Can I write custom rules?" | Yes, YAML-based. Organization tier and up. |
| "How is this different from SonarQube?" | SonarQube finds bugs. Sentrik maps findings to specific regulatory clauses and generates audit evidence. Plus the Evidence Map — SonarQube can't prove compliance, only violations. |
| "How is this different from Snyk?" | Snyk focuses on dependencies and container scanning. Sentrik covers that plus static analysis, compliance reporting, threat modeling, and regulatory evidence. One tool instead of three. |
| "Does it integrate with our GRC platform?" | We have a webhook endpoint for Drata, Vanta, and Secureframe. Partnerships in progress. |
| "What about GDPR / EU AI Act / NIST?" | All built in. 22 frameworks total. |
| "How much does it cost?" | Free tier: 5 packs, 158 rules, forever. Team: $29/month. Organization: $99/month. |
