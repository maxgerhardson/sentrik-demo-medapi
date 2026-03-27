#!/usr/bin/env python3
"""Take screenshots of every Sentrik dashboard tab using Playwright.

Starts sentrik dashboard, waits for it, then navigates to each tab
and takes screenshots in both light and dark mode.
"""
import subprocess
import time
import sys
import os
from pathlib import Path

# Ensure we're in the project directory
PROJECT_DIR = Path(__file__).parent.parent
SCREENSHOTS_DIR = PROJECT_DIR / "docs" / "walkthrough" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_PORT = 8765
DASHBOARD_URL = f"http://localhost:{DASHBOARD_PORT}"

# Dashboard tabs — sidebar navigation
# Each entry: (tab_name, selector_to_click, wait_for_selector, filename)
TABS = [
    ("Overview",       '[data-tab="overview"]',       '.health-grid, .severity-chart, .chart-container',  "01-overview"),
    ("Findings",       '[data-tab="findings"]',       '.findings-list, .finding-card, .findings-table',   "02-findings"),
    ("Vulnerabilities",'[data-tab="vulns"]',          '.vuln-list, .vuln-table, .vulns-container',        "03-vulnerabilities"),
    ("History",        '[data-tab="history"]',        '.history-list, .history-container, .run-list',      "04-history"),
    ("Rules",          '[data-tab="rules"]',          '.rules-list, .rule-card, .rules-table',            "05-rules"),
    ("Packs",          '[data-tab="packs"]',          '.packs-list, .pack-card, .packs-grid',             "06-packs"),
    ("Reports",        '[data-tab="reports"]',        '.reports-container, .report-section',               "07-reports"),
    ("Licenses",       '[data-tab="licenses"]',       '.license-list, .license-table, .licenses-container', "08-licenses"),
    ("Impact",         '[data-tab="impact"]',         '.impact-container, .impact-section',               "09-impact"),
    ("Work Items",     '[data-tab="work-items"]',     '.work-items-list, .work-item-card',                "10-work-items"),
    ("Integration",    '[data-tab="integration"]',    '.integration-container, .provider-section',         "11-integration"),
    ("Policies",       '[data-tab="policies"]',       '.policies-container, .governance-section',          "12-policies"),
    ("Approvals",      '[data-tab="approvals"]',      '.approvals-container, .approval-list',             "13-approvals"),
    ("Audit Log",      '[data-tab="audit"]',          '.audit-log, .audit-container, .audit-list',        "14-audit-log"),
    ("Settings",       '[data-tab="settings"]',       '.settings-container, .config-viewer',              "15-settings"),
]


def start_dashboard():
    """Start sentrik dashboard in background."""
    print(f"Starting sentrik dashboard on port {DASHBOARD_PORT}...")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(
        f"sentrik dashboard --no-open --port {DASHBOARD_PORT}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=env
    )
    # Wait for it to be ready
    import httpx
    for i in range(30):
        try:
            r = httpx.get(f"{DASHBOARD_URL}/health", timeout=2)
            if r.status_code == 200:
                print(f"  Dashboard ready at {DASHBOARD_URL}")
                return proc
        except Exception:
            pass
        time.sleep(1)
    print("  WARNING: Dashboard may not be ready yet, proceeding anyway...")
    return proc


def take_screenshots():
    """Navigate to each tab and screenshot."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for theme in ["dark", "light"]:
            print(f"\n{'='*50}")
            print(f"  Theme: {theme}")
            print(f"{'='*50}")

            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"{DASHBOARD_URL}/dashboard", wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(2000)  # Let initial JS render

            # Toggle theme if needed
            if theme == "light":
                # Try to find and click theme toggle
                try:
                    toggle = page.locator('[data-action="toggle-theme"], .theme-toggle, #theme-toggle, button:has-text("theme")')
                    if toggle.count() > 0:
                        toggle.first.click()
                        page.wait_for_timeout(500)
                        print("  Toggled to light theme")
                    else:
                        # Try keyboard shortcut or inject CSS
                        page.evaluate("document.body.classList.toggle('light-theme')")
                        print("  Injected light theme class")
                except Exception as e:
                    print(f"  Could not toggle theme: {e}")

            for tab_name, selector, wait_selector, filename in TABS:
                try:
                    # Click the tab
                    tab_el = page.locator(selector)
                    if tab_el.count() > 0:
                        tab_el.first.click()
                        page.wait_for_timeout(1000)
                    else:
                        # Try clicking by text
                        text_el = page.locator(f'text="{tab_name}"')
                        if text_el.count() > 0:
                            text_el.first.click()
                            page.wait_for_timeout(1000)
                        else:
                            # Try sidebar link
                            sidebar = page.locator(f'.sidebar a:has-text("{tab_name}"), .nav-item:has-text("{tab_name}")')
                            if sidebar.count() > 0:
                                sidebar.first.click()
                                page.wait_for_timeout(1000)
                            else:
                                print(f"  SKIP {tab_name}: selector not found")
                                continue

                    # Wait for content
                    try:
                        page.wait_for_selector(wait_selector, timeout=3000)
                    except Exception:
                        pass  # Content may not match expected selector, screenshot anyway

                    page.wait_for_timeout(500)

                    # Screenshot
                    path = SCREENSHOTS_DIR / f"{filename}-{theme}.png"
                    page.screenshot(path=str(path), full_page=False)
                    print(f"  {tab_name}: {path.name}")

                except Exception as e:
                    # Screenshot whatever is on screen
                    path = SCREENSHOTS_DIR / f"{filename}-{theme}.png"
                    try:
                        page.screenshot(path=str(path), full_page=False)
                        print(f"  {tab_name}: {path.name} (with error: {e})")
                    except Exception:
                        print(f"  {tab_name}: FAILED - {e}")

            page.close()

        browser.close()


def main():
    # Start dashboard
    proc = start_dashboard()

    try:
        take_screenshots()
    finally:
        # Stop dashboard
        print("\nStopping dashboard...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # Count results
    pngs = list(SCREENSHOTS_DIR.glob("*.png"))
    print(f"\nDone! {len(pngs)} screenshots in {SCREENSHOTS_DIR}/")


if __name__ == "__main__":
    main()
