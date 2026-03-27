#!/usr/bin/env python3
"""Record polished dashboard demo videos with Playwright.

Creates multiple focused demo videos showcasing different Sentrik features,
each designed as a standalone selling point. Uses enterprise license for
full feature access.

Videos:
  1. overview-tour.mp4      — The compliance journey (before/after)
  2. findings-and-ai.mp4    — Finding drill-down + Fix with AI
  3. supply-chain.mp4        — Vulnerabilities + licenses + SBOM
  4. governance-audit.mp4    — Policies, approvals, audit log
  5. devops-integration.mp4  — Work items, reconcile, traceability
  6. standards-rules.mp4     — Packs, rules browser, custom rules
"""
import subprocess
import time
import os
import shutil
import httpx
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_DIR = Path(__file__).parent.parent
RECORDINGS_DIR = PROJECT_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)
TMP_DIR = RECORDINGS_DIR / "tmp"

PORT = 8768
DASHBOARD_URL = f"http://localhost:{PORT}/dashboard"
LICENSE_KEY = "GUARD-ENTERPRISE-20260625-54433fa77ea882f5"
FFMPEG = "C:/Users/mgerh/AppData/Local/Programs/Python/Python312/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "NO_COLOR": "1",
    "TERM": "dumb",
    "GUARD_LICENSE_KEY": LICENSE_KEY,
}


def scan_at(tag=None):
    """Run sentrik scan, optionally checking out app code from a git tag."""
    if tag:
        subprocess.run(f"git checkout {tag} -- src/ tests/ firmware/ client/",
                       shell=True, capture_output=True, cwd=str(PROJECT_DIR))
    subprocess.run("sentrik scan", shell=True, capture_output=True, env=ENV, timeout=300, cwd=str(PROJECT_DIR))
    if tag:
        subprocess.run("git checkout main -- src/ tests/ firmware/ client/",
                       shell=True, capture_output=True, cwd=str(PROJECT_DIR))


def start_dashboard():
    proc = subprocess.Popen(
        f"sentrik dashboard --no-open --port {PORT}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=ENV, cwd=str(PROJECT_DIR)
    )
    for _ in range(25):
        try:
            r = httpx.get(f"http://localhost:{PORT}/health", timeout=2)
            if r.status_code == 200:
                return proc
        except Exception:
            pass
        time.sleep(1)
    print("  WARNING: Dashboard may not be ready")
    return proc


def stop_dashboard(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    time.sleep(2)


def convert_to_mp4(webm_path, mp4_path):
    subprocess.run(
        [FFMPEG, "-i", str(webm_path), "-c:v", "libx264", "-preset", "fast",
         "-crf", "18", "-preset", "slow", "-movflags", "+faststart", str(mp4_path), "-y"],
        capture_output=True, timeout=120
    )


class DashboardRecorder:
    """Record a browser session as video."""

    def __init__(self, name):
        self.name = name
        self.tmp = TMP_DIR / name
        self.tmp.mkdir(parents=True, exist_ok=True)
        self._pw = None
        self._browser = None
        self._context = None
        self.page = None

    def start(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self._context = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(self.tmp),
            record_video_size={"width": 1920, "height": 1080},
        )
        self.page = self._context.new_page()
        self.page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=15000)
        self.page.wait_for_timeout(2000)
        return self

    def click_tab(self, tab_id, wait_ms=2000):
        tab = self.page.locator(f'[data-tab="{tab_id}"]')
        if tab.count() > 0:
            tab.first.click()
            self.page.wait_for_timeout(wait_ms)
        return self

    def click(self, selector, wait_ms=1500):
        try:
            el = self.page.locator(selector)
            if el.count() > 0:
                el.first.click(timeout=5000)
                self.page.wait_for_timeout(wait_ms)
        except Exception:
            pass
        return self

    def click_text(self, text, wait_ms=1500):
        try:
            el = self.page.locator(f"text={text}")
            if el.count() > 0:
                el.first.click(timeout=5000)
                self.page.wait_for_timeout(wait_ms)
        except Exception:
            pass
        return self

    def hover(self, selector, wait_ms=800):
        el = self.page.locator(selector)
        if el.count() > 0:
            el.first.hover()
            self.page.wait_for_timeout(wait_ms)
        return self

    def scroll_down(self, pixels=400, wait_ms=1000):
        self.page.mouse.wheel(0, pixels)
        self.page.wait_for_timeout(wait_ms)
        return self

    def scroll_to_top(self, wait_ms=500):
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(wait_ms)
        return self

    def wait(self, ms=2000):
        self.page.wait_for_timeout(ms)
        return self

    def type_in(self, selector, text, wait_ms=1000):
        try:
            el = self.page.locator(selector)
            if el.count() > 0:
                el.first.click(timeout=3000)
                el.first.fill(text)
                self.page.wait_for_timeout(wait_ms)
        except Exception:
            pass
        return self

    def finish(self):
        """Close browser, convert video, cleanup."""
        self._context.close()
        self._browser.close()
        self._pw.stop()

        # Find the webm file
        webms = list(self.tmp.glob("*.webm"))
        if not webms:
            print(f"  ERROR: No video file found for {self.name}")
            return None

        webm = webms[0]
        mp4 = RECORDINGS_DIR / f"{self.name}.mp4"
        convert_to_mp4(str(webm), str(mp4))
        shutil.rmtree(self.tmp, ignore_errors=True)

        if mp4.exists():
            size = mp4.stat().st_size / 1024 / 1024
            print(f"  {self.name}.mp4 ({size:.1f}MB)")
            return mp4
        return None


# ============================================================================
# DEMO 1: Overview Tour — The Compliance Journey
# ============================================================================
def record_overview_tour():
    """Before state (failing) → rescan → After state (passing). Single session."""
    print("\n[1/6] Overview Tour — The Compliance Journey")

    # Scan at v0.1 for the failing state
    scan_at("v0.1-requirements")
    proc = start_dashboard()

    rec = DashboardRecorder("overview-tour").start()

    # BEFORE: see the red 49.7%, warning banner
    rec.click_tab("overview", 4000)
    rec.scroll_down(300, 1500)
    rec.scroll_to_top()

    # Findings — wall of high-severity violations
    rec.click_tab("findings", 3000)
    rec.scroll_down(200, 1000)

    # Vulnerabilities
    rec.click_tab("vulns", 3000)

    # Now trigger a rescan at main (via API) to show the "after" state
    try:
        # Scan main in background
        subprocess.run("git checkout main", shell=True, capture_output=True, cwd=str(PROJECT_DIR))
        httpx.post(f"http://localhost:{PORT}/api/run-scan", timeout=30)
        rec.wait(3000)
    except Exception:
        pass

    # AFTER: overview now shows 100%
    rec.click_tab("overview", 4000)
    rec.scroll_down(300, 1500)
    rec.scroll_to_top()

    # Clean findings
    rec.click_tab("findings", 3000)

    # History — shows the improvement over time
    rec.click_tab("history", 3000)

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# DEMO 2: Findings & AI Fix
# ============================================================================
def record_findings_and_ai():
    """Drill into findings, expand details, use Fix with AI chat."""
    print("\n[2/6] Findings & AI Fix")

    scan_at("v0.1-requirements")
    proc = start_dashboard()

    rec = DashboardRecorder("findings-and-ai").start()

    # Findings tab
    rec.click_tab("findings", 2000)

    # Click on severity filter pills to show filtering
    rec.click('[data-sev="high"]', 1500)
    rec.click('[data-sev="all"]', 1500)

    # Click a finding row to expand it
    rec.click(".finding-row, tr.finding-row, [onclick*='toggleFinding']", 2000)
    rec.scroll_down(200, 1500)

    # Click "Fix with AI" button
    rec.click_text("Fix with AI", 3000)
    rec.scroll_down(100, 1000)
    rec.scroll_to_top()

    # Back to findings
    rec.click_tab("findings", 2000)

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# DEMO 3: Supply Chain Security
# ============================================================================
def record_supply_chain():
    """Vulnerabilities, licenses, SBOM — dependency security."""
    print("\n[3/6] Supply Chain Security")

    scan_at("v0.1-requirements")
    proc = start_dashboard()

    rec = DashboardRecorder("supply-chain").start()

    # Vulnerabilities tab
    rec.click_tab("vulns", 3000)
    rec.scroll_down(200, 1500)
    rec.scroll_down(200, 1500)
    rec.scroll_to_top(500)

    # Click "Chat" on a vulnerability if available
    rec.click_text("Chat", 2500)

    # Licenses tab
    rec.click_tab("licenses", 3000)
    rec.scroll_down(200, 1000)
    rec.scroll_to_top()

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# DEMO 4: Governance & Audit Trail
# ============================================================================
def record_governance_audit():
    """Policies, approvals, audit log — enterprise governance."""
    print("\n[4/6] Governance & Audit Trail")

    scan_at()
    proc = start_dashboard()

    rec = DashboardRecorder("governance-audit").start()

    # Policies tab
    rec.click_tab("policies", 3000)
    rec.scroll_down(200, 1000)
    rec.scroll_to_top()

    # Approvals tab
    rec.click_tab("approvals", 2500)

    # Audit log tab
    rec.click_tab("audit", 3000)
    # Click an audit entry to expand
    rec.click(".audit-entry, .audit-row, [onclick*='toggleAuditDetail']", 2000)
    rec.scroll_down(200, 1000)

    # Click "Export Audit Bundle"
    rec.click_text("Export Audit Bundle", 2000)

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# DEMO 5: DevOps Integration
# ============================================================================
def record_devops_integration():
    """Work items, reconcile, coverage — DevOps sync."""
    print("\n[5/6] DevOps Integration")

    scan_at()
    proc = start_dashboard()

    rec = DashboardRecorder("devops-integration").start()

    # Work Items tab
    rec.click_tab("work-items", 3000)
    rec.scroll_down(200, 1500)
    rec.scroll_to_top()

    # Click "Check Coverage"
    rec.click_text("Check Coverage", 2000)

    # Click a work item detail
    rec.click_text("Detail", 2000)

    # Show generate requirements
    rec.click_text("Generate Requirements", 2000)

    # Integration tab (GitHub connected)
    rec.click_tab("integration", 3000)

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# DEMO 6: Standards & Rules
# ============================================================================
def record_standards_rules():
    """Packs management, rule browser, custom rules."""
    print("\n[6/6] Standards & Rules")

    scan_at()
    proc = start_dashboard()

    rec = DashboardRecorder("standards-rules").start()

    # Packs tab
    rec.click_tab("packs", 3000)
    rec.scroll_down(200, 1500)
    rec.scroll_to_top()

    # Rules tab
    rec.click_tab("rules", 3000)

    # Search for a rule
    rec.type_in('input[placeholder*="Search"], input[type="search"], #rules-search', "injection", 2000)
    rec.type_in('input[placeholder*="Search"], input[type="search"], #rules-search', "", 1000)

    # Filter by severity
    rec.click('[data-sev="high"], .sev-pill[data-sev="high"]', 1500)
    rec.click('[data-sev="all"], .sev-pill[data-sev="all"]', 1000)

    # Click a rule to expand
    rec.click_text("Detail", 2000)

    rec.scroll_down(200, 1000)

    # Reports tab
    rec.click_tab("reports", 2000)

    # History tab
    rec.click_tab("history", 3000)

    # Settings
    rec.click_tab("settings", 2000)

    stop_dashboard(proc)
    rec.finish()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Sentrik Dashboard Demo Videos")
    print("  Enterprise license + real scan data")
    print("=" * 60)

    # Clean tmp
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)

    # Hide .guard.yaml so .sentrik/config.yaml is used (with scan_exclude)
    guard_yaml = PROJECT_DIR / ".guard.yaml"
    guard_yaml_bak = PROJECT_DIR / ".guard.yaml.recording-bak"
    if guard_yaml.exists():
        guard_yaml.rename(guard_yaml_bak)

    try:
        record_overview_tour()
        record_findings_and_ai()
        record_supply_chain()
        record_governance_audit()
        record_devops_integration()
        record_standards_rules()
    finally:
        # Restore .guard.yaml
        if guard_yaml_bak.exists():
            guard_yaml_bak.rename(guard_yaml)

    # Final cleanup
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    print("\n" + "=" * 60)
    print("  All videos in recordings/")
    mp4s = list(RECORDINGS_DIR.glob("*.mp4"))
    total = 0
    for mp4 in sorted(mp4s):
        size = mp4.stat().st_size / 1024 / 1024
        total += size
        print(f"  {mp4.name:40s} {size:.1f}MB")
    print(f"  {'TOTAL':40s} {total:.1f}MB")
    print("=" * 60)
