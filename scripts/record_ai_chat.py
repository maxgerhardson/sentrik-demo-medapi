#!/usr/bin/env python3
"""Record the Findings + AI Chat demo video.

This script:
1. Starts the dashboard with LLM configured (Anthropic Claude)
2. Registers the API key via /api/ai-key
3. Navigates to findings, expands one, opens Fix with AI
4. Types a real question and waits for Claude's response
5. Records everything as a high-quality video
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
TMP_DIR = RECORDINGS_DIR / "tmp_ai_chat"

PORT = 8770
FFMPEG = "C:/Users/mgerh/AppData/Local/Programs/Python/Python312/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

LICENSE_KEY = "GUARD-ENTERPRISE-20260625-54433fa77ea882f5"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "GUARD_LICENSE_KEY": LICENSE_KEY,
    "GUARD_LLM_PROVIDER": "anthropic",
    "GUARD_LLM_MODEL": "claude-haiku-4-5-20251001",
    "NO_COLOR": "1",
    "TERM": "dumb",
}


def main():
    if not API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        return

    # Clean
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True)

    # Temporarily hide .guard.yaml so .sentrik/config.yaml is used
    guard_yaml = PROJECT_DIR / ".guard.yaml"
    guard_yaml_bak = PROJECT_DIR / ".guard.yaml.recording-bak"
    if guard_yaml.exists():
        guard_yaml.rename(guard_yaml_bak)

    # Scan at v0.1 for real findings (only src/tests/firmware/client)
    print("Scanning v0.1 application code for findings data...")
    subprocess.run("git checkout v0.1-requirements -- src/ tests/ firmware/ client/",
                   shell=True, capture_output=True, cwd=str(PROJECT_DIR))
    subprocess.run("sentrik scan", shell=True, capture_output=True,
                   env=ENV, timeout=300, cwd=str(PROJECT_DIR))
    subprocess.run("git checkout main -- src/ tests/ firmware/ client/",
                   shell=True, capture_output=True, cwd=str(PROJECT_DIR))

    # Start dashboard
    print("Starting dashboard with LLM enabled...")
    proc = subprocess.Popen(
        f"sentrik dashboard --no-open --port {PORT}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=ENV, cwd=str(PROJECT_DIR)
    )
    for _ in range(25):
        try:
            r = httpx.get(f"http://localhost:{PORT}/health", timeout=2)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)
    print("Dashboard ready")

    # Register API key via the dashboard API
    print("Registering API key...")
    try:
        r = httpx.post(
            f"http://localhost:{PORT}/api/ai-key",
            json={"provider": "anthropic", "api_key": API_KEY},
            timeout=5,
        )
        print(f"  API key registration: {r.status_code} {r.json()}")
    except Exception as e:
        print(f"  API key registration failed: {e}")

    # Record video
    print("Recording video...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(TMP_DIR),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        page.goto(f"http://localhost:{PORT}/dashboard",
                  wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(2500)

        # -- SCENE 1: Findings tab --
        print("  Scene 1: Findings tab")
        tab = page.locator('[data-tab="findings"]')
        if tab.count() > 0:
            tab.first.click()
            page.wait_for_timeout(2500)

        # -- SCENE 2: Click severity filter to show HIGH findings --
        print("  Scene 2: Severity filter")
        high_pill = page.locator('[data-sev="high"]')
        if high_pill.count() > 0:
            high_pill.first.click()
            page.wait_for_timeout(2000)

        # -- SCENE 3: Click on a finding to expand + open chat via JS --
        print("  Scene 3: Expand finding and open AI chat")
        page.evaluate("""
            // Click the first finding row to expand it
            const rows = document.querySelectorAll('tr[onclick]');
            if (rows.length > 0) rows[0].click();
        """)
        page.wait_for_timeout(2500)

        # -- SCENE 4: Open chat panel via JS (more reliable than clicking the button) --
        print("  Scene 4: Opening chat panel")
        page.evaluate("""
            // Find and click the "Fix with AI" button
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                if (b.textContent.trim() === 'Fix with AI' && b.offsetParent !== null) {
                    b.click();
                    break;
                }
            }
        """)
        page.wait_for_timeout(3000)

        # Check if chat panel opened
        panel_open = page.evaluate("document.getElementById('chat-panel')?.classList.contains('open')")
        if not panel_open:
            # Force open via JS using the first finding
            print("  Forcing chat panel open via JS")
            page.evaluate("""
                if (typeof filteredFindings !== 'undefined' && filteredFindings.length > 0) {
                    openChatPanel(filteredFindings[0]);
                }
            """)
            page.wait_for_timeout(3000)

        print("  Chat panel open:", page.evaluate("document.getElementById('chat-panel')?.classList.contains('open')"))

        # -- SCENE 5: Type a question --
        print("  Scene 5: Type question")
        # Use JS to focus and fill the chat input
        page.evaluate("""
            const input = document.getElementById('chat-input');
            if (input) {
                input.scrollIntoView();
                input.focus();
            }
        """)
        page.wait_for_timeout(500)

        question = "How do I fix this? Show me the exact code I need to add."
        page.evaluate(f"document.getElementById('chat-input').value = ''")
        for char in question:
            page.evaluate(f"document.getElementById('chat-input').value += '{char}'")
            page.wait_for_timeout(35)
        page.wait_for_timeout(1000)

        # -- SCENE 6: Send and wait for response --
        print("  Scene 6: Sending message, waiting for LLM...")
        page.evaluate("sendChatMessage()")
        page.wait_for_timeout(15000)

        # Scroll chat to see full response
        page.evaluate("""
            const msgs = document.getElementById('chat-messages');
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
        """)
        page.wait_for_timeout(4000)

        print("  Response should be visible")

        # -- SCENE 7: Hold on the result --
        page.wait_for_timeout(3000)

        # Take a screenshot too
        page.screenshot(path=str(RECORDINGS_DIR / "ai-chat-screenshot.png"))
        print("  Screenshot saved")

        # Close
        context.close()
        browser.close()
        video_path = page.video.path()

    # Stop dashboard
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

    # Restore .guard.yaml
    if guard_yaml_bak.exists():
        guard_yaml_bak.rename(guard_yaml)

    # Convert to mp4
    print("Converting to mp4...")
    mp4_path = RECORDINGS_DIR / "findings-and-ai.mp4"
    subprocess.run(
        [FFMPEG, "-i", str(video_path), "-c:v", "libx264", "-preset", "slow",
         "-crf", "18", "-movflags", "+faststart", str(mp4_path), "-y"],
        capture_output=True, timeout=120
    )

    # Cleanup
    shutil.rmtree(TMP_DIR, ignore_errors=True)

    if mp4_path.exists():
        size = mp4_path.stat().st_size / 1024 / 1024
        print(f"\nDone! findings-and-ai.mp4 ({size:.1f}MB)")
    else:
        print("\nERROR: mp4 not created")


if __name__ == "__main__":
    main()
