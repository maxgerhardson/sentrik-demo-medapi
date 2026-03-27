# Step 5: Supply Chain Security

> **Goal:** Generate an SBOM, find and fix vulnerable dependencies, verify license compliance, and scan for leaked secrets.

Modern applications are mostly third-party code. VitalSync Medical API depends on 13 Python packages — any one of them could contain a critical vulnerability or an incompatible license. Sentrik covers the entire supply chain in four commands.

---

## SBOM Generation

A Software Bill of Materials (SBOM) is required by FDA cybersecurity guidance and increasingly by enterprise procurement. Sentrik generates one in CycloneDX format:

```
$ sentrik sbom

  Sentrik SBOM — VitalSync Medical API
  =====================================

  Format:     CycloneDX 1.5 (JSON)
  Components: 13
  Output:     out/sbom.json

  Components:
  ┌─────────────────────┬──────────┬─────────┐
  │ Package             │ Version  │ License │
  ├─────────────────────┼──────────┼─────────┤
  │ fastapi             │ 0.109.0  │ MIT     │
  │ uvicorn             │ 0.27.0   │ BSD-3   │
  │ sqlalchemy          │ 2.0.25   │ MIT     │
  │ pydantic            │ 2.5.3    │ MIT     │
  │ requests            │ 2.25.0   │ Apache  │
  │ cryptography        │ 42.0.0   │ Apache  │
  │ python-jose         │ 3.3.0    │ MIT     │
  │ python-multipart    │ 0.0.6    │ Apache  │
  │ bcrypt              │ 4.1.2    │ Apache  │
  │ alembic             │ 1.13.1   │ MIT     │
  │ httpx               │ 0.26.0   │ BSD-3   │
  │ python-dotenv       │ 1.0.0    │ BSD-3   │
  │ pyotp               │ 2.9.0    │ MIT     │
  └─────────────────────┴──────────┴─────────┘
```

The SBOM is uploaded as a CI artifact (see [Step 6](06-ci-gate.md)) and can be shared with customers, auditors, or fed into other tools.

---

## Vulnerability Scanning

```
$ sentrik vulns

  Sentrik Vulnerability Scan — VitalSync Medical API
  ====================================================

  Packages scanned: 13
  Vulnerabilities:  19

  ┌─────────────────────┬──────────┬──────┬──────────┬────────────────────────────┐
  │ Package             │ Version  │ CVEs │ Severity │ Summary                    │
  ├─────────────────────┼──────────┼──────┼──────────┼────────────────────────────┤
  │ requests            │ 2.25.0   │  5   │ high     │ SSRF, header injection,    │
  │                     │          │      │          │ proxy auth leak            │
  │ cryptography        │ 42.0.0   │  5   │ high     │ RSA decryption, PKCS7,     │
  │                     │          │      │          │ NULL dereference           │
  │ python-jose         │ 3.3.0    │  3   │ critical │ JWE denial of service,     │
  │                     │          │      │          │ ECDSA key forgery          │
  │ python-multipart    │ 0.0.6    │  3   │ high     │ ReDoS, header injection,   │
  │                     │          │      │          │ resource exhaustion        │
  │ fastapi             │ 0.109.0  │  1   │ medium   │ Content-Type header ReDoS  │
  └─────────────────────┴──────────┴──────┴──────────┴────────────────────────────┘

  19 vulnerabilities found across 5 packages.
```

These are real CVEs. The `requests 2.25.0` and `python-jose 3.3.0` versions were intentionally pinned to outdated versions to demonstrate the detection and remediation workflow.

### Key Findings

| Package | CVEs | Worst Severity | Why it matters |
|---|---|---|---|
| **requests 2.25.0** | 5 | High | SSRF allows attackers to reach internal services through the API |
| **cryptography 42.0.0** | 5 | High | RSA decryption oracle can leak private keys |
| **python-jose 3.3.0** | 3 | Critical | ECDSA key forgery allows JWT token forging |
| **python-multipart 0.0.6** | 3 | High | ReDoS and resource exhaustion enable denial of service |
| **fastapi 0.109.0** | 1 | Medium | Content-Type parsing ReDoS |

---

## Auto-Fix Vulnerabilities

Sentrik does not just find vulnerabilities — it fixes them:

```
$ sentrik vulns --fix

  Sentrik Vulnerability Auto-Fix
  ===============================

  Patching pyproject.toml...

  ✅ requests:        2.25.0 → 2.32.3
  ✅ cryptography:    42.0.0 → 44.0.0
  ✅ python-multipart: 0.0.6 → 0.0.18
  ✅ fastapi:         0.109.0 → 0.115.0
  ⚠️  python-jose:     3.3.0 — no patched version available (consider migrating to PyJWT)

  Fixed: 4 packages, 18 CVEs resolved
  Remaining: 1 vulnerability (python-jose)

  Branch: fix/sentrik-vuln-patches
  PR #14 created: https://github.com/maxgerhardson/sentrik-demo-medapi/pull/14
```

**After the fix:**

```
$ sentrik vulns

  Packages scanned: 13
  Vulnerabilities:  1

  ┌─────────────────────┬──────────┬──────┬──────────┬────────────────────────────┐
  │ Package             │ Version  │ CVEs │ Severity │ Summary                    │
  ├─────────────────────┼──────────┼──────┼──────────┼────────────────────────────┤
  │ python-jose         │ 3.3.0    │  1   │ high     │ ECDSA key forgery (no fix  │
  │                     │          │      │          │ available — migrate to     │
  │                     │          │      │          │ PyJWT recommended)         │
  └─────────────────────┴──────────┴──────┴──────────┴────────────────────────────┘

  19 → 1 vulnerability. 18 resolved by version bumps.
```

The `python-jose` package is unmaintained — the recommended path is to migrate to `PyJWT`. Sentrik flags this clearly rather than silently ignoring it.

---

## License Compliance

Regulated industries and enterprise procurement require license audits. One command:

```
$ sentrik licenses

  Sentrik License Scan — VitalSync Medical API
  ==============================================

  Packages scanned: 13

  License Distribution:
    MIT:           6 packages
    Apache-2.0:    4 packages
    BSD-3-Clause:  3 packages

  Risk Assessment:
  ┌─────────────────────┬──────────────┬───────┐
  │ Package             │ License      │ Risk  │
  ├─────────────────────┼──────────────┼───────┤
  │ fastapi             │ MIT          │ none  │
  │ uvicorn             │ BSD-3-Clause │ none  │
  │ sqlalchemy          │ MIT          │ none  │
  │ pydantic            │ MIT          │ none  │
  │ requests            │ Apache-2.0   │ none  │
  │ cryptography        │ Apache/BSD   │ low   │
  │ python-jose         │ MIT          │ none  │
  │ python-multipart    │ Apache-2.0   │ none  │
  │ bcrypt              │ Apache-2.0   │ none  │
  │ alembic             │ MIT          │ none  │
  │ httpx               │ BSD-3-Clause │ none  │
  │ python-dotenv       │ BSD-3-Clause │ none  │
  │ pyotp               │ MIT          │ none  │
  └─────────────────────┴──────────────┴───────┘

  ✅ No copyleft (GPL/AGPL) licenses detected.
  ℹ️  2 low-risk items: cryptography uses dual Apache/BSD license.
```

All 13 packages use permissive licenses (MIT, BSD, Apache). No GPL or AGPL licenses that would require source disclosure. The dual-license on `cryptography` is flagged as low-risk for visibility but requires no action.

---

## Secrets Scanning

Sentrik scans for leaked credentials, API keys, and tokens:

```
$ sentrik secrets

  Sentrik Secrets Scan — VitalSync Medical API
  ==============================================

  Files scanned: 67
  Secrets found: 0

  ✅ No secrets detected in tracked files.
```

### Pre-Commit Hook

The real value of secrets scanning is catching leaks **before** they reach the repository. With the Sentrik pre-commit hook:

```
$ git commit -m "add database config"

  Sentrik pre-commit: scanning staged files...

  ❌ SECRET DETECTED
  File: config/database.py
  Line 12: AWS_SECRET_ACCESS_KEY = "AKIA..."
  Rule: SECRETS-001 (AWS access key)

  Commit blocked. Remove the secret and try again.
  Tip: Use environment variables or a secrets manager instead.
```

The hook runs `sentrik scan --staged` on every commit, scanning only the files being committed. It adds less than 2 seconds to the commit workflow.

---

## Pull Request

The vulnerability fixes were auto-committed to a feature branch and submitted as **PR #14**:

- **Title:** fix: patch 18 CVEs across 4 dependencies
- **Contents:** Version bumps in `pyproject.toml` for requests, cryptography, python-multipart, and fastapi
- **Remaining:** 1 CVE in python-jose (no fix available, migration recommended)
- **Gate status:** PASSED

---

## What Sentrik Did

| Capability | How it helped |
|---|---|
| `sentrik sbom` | CycloneDX SBOM for FDA submission and procurement |
| `sentrik vulns` | Found 19 CVEs across 5 packages in seconds |
| `sentrik vulns --fix` | Auto-patched 4 packages, created PR with version bumps |
| `sentrik licenses` | Verified all 13 packages use permissive licenses |
| `sentrik secrets` | Pre-commit hook prevents credential leaks |

## Without Sentrik

- **SBOM:** Manual creation with `pip-licenses` + CycloneDX CLI + custom scripting
- **Vulnerabilities:** Snyk, npm audit, pip-audit — separate tools for each ecosystem, none auto-fix
- **Licenses:** `pip-licenses` gives you a list but no risk assessment or policy enforcement
- **Secrets:** git-secrets or truffleHog — separate install, separate config, separate CI step
- **Integration:** Four separate tools, four separate configurations, four separate CI jobs, no unified view

---

**Next:** [Step 6 — CI/CD Gate](06-ci-gate.md)
