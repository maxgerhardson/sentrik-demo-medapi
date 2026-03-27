# Step 6: CI/CD Gate

> **Goal:** Automate compliance enforcement on every pull request so non-compliant code cannot merge.

Manual compliance checks do not scale. Sentrik integrates directly into CI/CD pipelines to enforce compliance as a merge gate — the same way teams enforce passing tests before merging.

---

## GitHub Actions Workflow

The full workflow lives at `.github/workflows/sentrik-gate.yml`:

```yaml
name: Sentrik Compliance Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  statuses: write
  security-events: write

jobs:
  compliance-gate:
    name: Sentrik Gate
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git-range

      - name: Install Sentrik
        run: npm install -g sentrik

      - name: Run Sentrik Scan
        run: sentrik scan
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run Sentrik Gate
        if: github.event_name == 'pull_request'
        run: |
          sentrik gate \
            --git-range "origin/${{ github.base_ref }}...HEAD" \
            --decorate-pr \
            --status-check
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GUARD_GITHUB_OWNER: ${{ github.repository_owner }}
          GUARD_GITHUB_REPO: ${{ github.event.repository.name }}

      - name: Run Sentrik Gate (push)
        if: github.event_name == 'push'
        run: sentrik gate
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload SARIF to Code Scanning
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: out/findings.sarif.json
        continue-on-error: true

      - name: Upload HTML Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sentrik-report
          path: |
            out/*.html
            out/findings.json
            out/scan_metrics.json

      - name: Upload JUnit Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sentrik-junit
          path: out/findings.junit.xml

  supply-chain:
    name: Supply Chain Security
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Sentrik
        run: npm install -g sentrik

      - name: SBOM Generation
        run: sentrik sbom

      - name: Vulnerability Scan
        run: sentrik vulns

      - name: License Compliance
        run: sentrik licenses

      - name: Secrets Scan
        run: sentrik secrets

      - name: Upload SBOM
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: out/sbom.*
```

### Key Steps Explained

**1. `sentrik scan`** — Runs the full compliance scan against all configured standards packs. Generates SARIF, HTML, JUnit, and JSON reports in `out/`.

**2. `sentrik gate`** — Evaluates findings against the configured thresholds:

| Flag | Purpose |
|---|---|
| `--git-range "origin/main...HEAD"` | Scope findings to only the PR's changed files |
| `--decorate-pr` | Post a compliance summary comment on the pull request |
| `--status-check` | Set a GitHub commit status (pass/fail) that branch protection can enforce |

**3. SARIF Upload** — Pushes findings to GitHub Code Scanning so they appear inline in the "Security" tab alongside CodeQL results.

**4. Artifact Upload** — Stores the HTML report, JUnit XML, and scan metrics as downloadable CI artifacts for auditors and reviewers.

**5. Supply Chain Job** — Runs in parallel: SBOM, vulnerabilities, licenses, and secrets scan with SBOM artifact upload.

---

## How the Gate Works on Pull Requests

### Gate FAIL — PR Blocked

When a PR introduces critical or high findings, the gate fails:

```
  Sentrik Gate — PR #12
  ======================

  New findings in this PR:     3
  Critical:                    1 (hardcoded database password)
  High:                        2 (missing input validation)

  ┌──────────────────────────┐
  │   ❌  GATE FAILED        │
  │   Merge blocked          │
  └──────────────────────────┘
```

The `--status-check` flag sets the GitHub commit status to `failure`. With branch protection rules requiring the "Sentrik Gate" check to pass, the merge button is disabled.

The `--decorate-pr` flag posts a comment on the PR with:
- Summary of new findings introduced by this PR
- Breakdown by severity
- Links to specific files and lines
- Remediation guidance

### Gate PASS — PR Approved

When all findings are resolved (as in PR #13 and PR #14):

```
  Sentrik Gate — PR #13
  ======================

  New findings in this PR:     0
  Resolved in this PR:     1,558

  ┌──────────────────────────┐
  │   ✅  GATE PASSED        │
  │   100% compliance        │
  └──────────────────────────┘
```

The commit status is set to `success` and the PR is eligible to merge.

---

## Real Examples from This Project

| PR | Description | Gate Result | Why |
|---|---|---|---|
| **#12** | Initial codebase (before fixes) | FAIL | 1,558 critical/high/medium findings |
| **#13** | Traceability headers + suppressions | PASS | All findings resolved or suppressed |
| **#14** | Dependency version bumps | PASS | 18 CVEs patched |

---

## Scoping to PR Diff

The `--git-range` flag is important for developer experience. Without it, the gate evaluates **all** findings in the entire codebase. With it:

```bash
sentrik gate --git-range "origin/main...HEAD"
```

Only findings in files changed by the PR are evaluated. This means:
- A developer is not responsible for pre-existing findings in files they did not touch
- The gate only blocks on issues the PR **introduces**
- Existing tech debt does not block unrelated feature work

---

## Pre-Commit Hook

CI catches issues after push. The pre-commit hook catches them before commit:

```bash
# Install the hook
sentrik hook install

# What it does on every commit:
sentrik scan --staged
```

The `--staged` flag scans only the files in the git staging area. It runs in under 2 seconds for typical commits, providing immediate feedback without slowing down the development workflow.

If a staged file contains a critical finding (e.g., a leaked secret, a hardcoded password), the commit is blocked with a clear error message and remediation guidance.

---

## Branch Protection Setup

To make the gate mandatory, configure GitHub branch protection:

1. Go to **Settings > Branches > Branch protection rules**
2. Add rule for `main`
3. Enable **Require status checks to pass before merging**
4. Search for and select **Sentrik Gate**
5. Enable **Require branches to be up to date before merging**

Now non-compliant code physically cannot merge to main.

---

## What Sentrik Did

| Capability | How it helped |
|---|---|
| CI workflow | Single YAML file for full compliance pipeline |
| `--decorate-pr` | Compliance summary posted directly on PRs |
| `--status-check` | GitHub status check blocks non-compliant merges |
| `--git-range` | Scopes to PR diff so developers only fix what they changed |
| SARIF upload | Findings appear in GitHub Security tab |
| Pre-commit hook | Catches issues before code reaches CI |
| Parallel jobs | Compliance gate and supply chain run simultaneously |

## Without Sentrik

- **Manual review checklists:** Someone has to remember to check compliance on every PR
- **No automated enforcement:** Branch protection cannot require "compliance" without a tool providing the status check
- **Post-hoc audits:** Compliance issues discovered weeks or months after merge, requiring costly rework
- **Multiple CI jobs:** Separate jobs for SAST, SCA, license scanning, secrets scanning — each with its own configuration and failure modes
- **No PR decoration:** Developers have to dig through CI logs to understand what failed and why

---

**Next:** [Step 7 — Dashboard and API](07-dashboard.md)
