# Step 10 — Advanced Features

> Enterprise governance without enterprise complexity — custom rules, AI
> integration, architecture enforcement, and more.

---

## 1. Custom Rules Pack

Sentrik supports project-specific rules alongside the built-in standards packs.
The VitalSync demo includes `medapi-custom.yaml` with four rules tailored to
this codebase:

| Rule ID | Description |
|---------|-------------|
| MEDAPI-001 | All API endpoints must validate patient ID format |
| MEDAPI-002 | Vital sign values must have physiological range checks |
| MEDAPI-003 | PHI fields must use the project encryption service |
| MEDAPI-004 | All database queries must go through the repository layer |

Custom packs use the same YAML schema as built-in packs. Organizations can
import and export custom packs across repositories:

```bash
# Import a custom pack
sentrik add-pack medapi-custom.yaml

# Export for use in another repo
sentrik export-pack medapi-custom
```

> **Enterprise feature** — custom rule packs require the Organization tier.

---

## 2. Architecture Rules

Enforce layered architecture constraints so code changes cannot bypass
boundaries:

```bash
sentrik check-arch
```

Validates the defined dependency rules for VitalSync:

```
api/ --> services/ --> db/
```

- API routes may call services but not database repositories directly
- Services may call repositories but not API routes
- No circular dependencies between layers

Violations are reported as findings with the specific import or call that
breaks the architecture rule.

---

## 3. Governance Profiles

Control how aggressively Sentrik enforces rules with governance profiles:

| Profile | Behavior |
|---------|----------|
| **strict** | All findings block the gate. Human review required for suppressions. Auto-patch disabled. |
| **standard** | Critical and high findings block. Suppressions require justification. Auto-patch for safe fixes. |
| **permissive** | Only critical findings block. Suppressions allowed freely. Auto-patch enabled for all safe categories. |

Profiles are set in `.sentrik/config.yaml`:

```yaml
governance:
  profile: standard
  human_review_gate: true
  auto_patch: safe_only
```

The human review gate ensures that auto-generated patches are reviewed before
merge — Sentrik creates the fix but a human approves it.

---

## 4. MCP Integration

Sentrik provides a Model Context Protocol (MCP) server for AI-assisted
development workflows.

### MCP Server

```bash
sentrik mcp-server
```

Exposes Sentrik scan results, rules, and compliance context to MCP-compatible
AI tools (Claude Code, Cursor, Windsurf). The AI assistant can query findings,
understand rule intent, and suggest compliant code.

### MCP Security Audit

```bash
sentrik audit-mcp
```

Audits your MCP tool configuration for security issues — overly broad
permissions, unscoped file access, missing authentication on tool servers.

### Agent Context

```bash
sentrik context
```

Outputs a structured context block (JSON) summarizing the current project
state — active findings, compliance posture, recent changes, and applicable
rules. Designed for consumption by AI coding agents that need project awareness.

---

## 5. C/C++ Analysis

For projects with native code (firmware, embedded systems, device drivers),
Sentrik integrates with clang-tidy for C/C++ static analysis:

```
firmware/
  checksum.c    # CRC-32 checksum implementation
```

Sentrik runs clang-tidy checks and maps findings to the applicable compliance
rules (particularly IEC 62304 for medical device firmware).

> **Enterprise feature** — C/C++ analysis requires the Organization tier.

---

## 6. Continuous Monitoring

### File Change Detection

```bash
sentrik watch
```

Monitors the working directory for file changes and re-runs relevant rules
incrementally. Useful during active development — findings appear in real time
as you save files.

### CVE Monitoring

```bash
sentrik watch --vulns
```

Periodically checks dependencies against vulnerability databases and creates
PRs automatically when new CVEs affect your dependencies. Runs on a
configurable schedule.

---

## 7. Change Impact Analysis

```bash
sentrik impact --staged
```

Shows which rules and compliance controls are affected by your currently staged
changes. Before you commit, you can see:

- Which rules will be re-evaluated
- Which compliance frameworks are touched
- Whether the change is likely to introduce new findings

Useful for scoping review effort on large changesets.

---

## 8. Organization Dashboard

```bash
sentrik org-dashboard
```

Multi-repository compliance dashboard for organizations managing several
projects. Shows:

- Per-repo compliance posture scores
- Aggregate finding trends across the organization
- Repositories with the most critical open findings
- Cross-repo standards coverage

> **Organization+ tier** required.

---

## 9. GRC Integration

Push compliance data to your Governance, Risk, and Compliance platform:

```bash
sentrik grc-push
```

Supported platforms:

| Platform | Integration |
|----------|-------------|
| **Drata** | Automated evidence collection |
| **Vanta** | Control mapping and evidence sync |
| **Secureframe** | Compliance task completion |

Sentrik maps its findings and evidence to the platform's control framework,
eliminating manual evidence uploads.

---

## 10. Auditor Portal

Create time-boxed, read-only access for external auditors:

```bash
sentrik auditor create
```

Generates a temporary access token with:
- Read-only access to compliance reports and evidence
- Configurable expiration (e.g., 7 days, 30 days)
- Scoped to specific frameworks or the full compliance view
- Audit log of all auditor access

No need to grant auditors access to your source code repository.

---

## 11. ASPM Posture Score

The `/api/posture` endpoint provides an Application Security Posture Management
score aggregating all compliance dimensions:

- Code quality findings (weighted by severity)
- Dependency vulnerabilities (weighted by CVSS)
- License compliance status
- Documentation obligation completion
- Framework-specific compliance percentages

The posture score gives a single number (0-100) representing your overall
compliance health, tracked over time.

---

## 12. Configuration Migration

```bash
sentrik migrate
```

Migrates from the legacy `.guard.yaml` configuration format to the current
`.sentrik/config.yaml` structure. Preserves all settings, pack selections,
suppressions, and governance configuration.

---

## What Sentrik Did

Enterprise governance without enterprise complexity. Custom rules enforce
project-specific standards alongside regulatory frameworks. Architecture rules
prevent structural decay. AI integration brings compliance context into the
developer's editor. Continuous monitoring and CVE watching keep the project
secure between explicit scan runs. GRC integration and auditor portals connect
the development workflow to the compliance workflow — no manual handoff.

## Without Sentrik

Each capability listed above would require a separate specialized tool:
custom linting rules in one tool, architecture enforcement in another,
GRC integration through a third-party connector, auditor access through
a separate portal, and AI context stitched together manually. Coordinating
these tools, keeping their configurations in sync, and mapping their outputs
to compliance frameworks is a full-time job.

---

Previous: [Step 9 — DevOps Integration](09-devops-integration.md)
