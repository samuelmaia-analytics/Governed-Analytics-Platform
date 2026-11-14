from __future__ import annotations

import os
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import Page, expect, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "assets" / "screenshots"
with socket.socket() as capture_socket:
    capture_socket.bind(("127.0.0.1", 0))
    APP_PORT = capture_socket.getsockname()[1]
APP_URL = f"http://127.0.0.1:{APP_PORT}"

PAGE_TARGETS: list[tuple[str, list[str], str]] = [
    ("", ["GOVERNED ANALYTICS PLATFORM"], "executive_overview.png"),
    (
        "lgpd-privacy-risk",
        ["Privacidade e Controles LGPD"],
        "lgpd_privacy_risk.png",
    ),
    ("data-quality", ["Qualidade dos Dados"], "data_quality.png"),
    (
        "governance-control-center",
        ["Laboratório de Governança", "Governance Lab"],
        "governance_control_center.png",
    ),
]


def wait_for_app_ready(timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(APP_URL, timeout=3) as response:
                if response.status == 200:
                    return
        except URLError:
            pass
        time.sleep(1)
    raise TimeoutError(
        f"Streamlit app did not become ready at {APP_URL} within {timeout_seconds} seconds."
    )


def goto_page(page: Page, url_path: str) -> None:
    target_url = APP_URL if not url_path else f"{APP_URL}/{url_path}"
    page.goto(target_url, wait_until="domcontentloaded", timeout=45_000)


def ensure_any_text(
    page: Page, candidates: list[str], timeout_ms: int = 60_000
) -> bool:
    for text in candidates:
        try:
            expect(page.get_by_text(text, exact=True).first).to_be_visible(
                timeout=timeout_ms
            )
            return True
        except AssertionError:
            continue
    return False


def capture_current_page(page: Page, output_file: Path) -> None:
    expect(page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()
    expect(page.locator('[data-testid="stStatusWidget"]')).to_have_count(
        0, timeout=120_000
    )
    expect(page.locator('[data-testid="stException"]')).to_have_count(0)
    expect(page.get_by_text("Page not found", exact=True)).to_have_count(0)
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(1000)
    png = page.screenshot(full_page=False, animations="disabled")
    if struct.unpack(">II", png[16:24]) != (1440, 900):
        raise RuntimeError("Screenshot must be exactly 1440 x 900 pixels")
    output_file.write_bytes(png)
    print(f"[OK] Saved: {output_file}")


def try_capture_privacy_preview(page: Page) -> None:
    preview_tab = page.get_by_role("tab", name="Prévia de transformações", exact=True)
    preview_tab.click()
    expect(preview_tab).to_have_attribute("aria-selected", "true")
    capture_current_page(page, OUTPUT_DIR / "privacy_transformation_preview.png")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    before_pngs = set(OUTPUT_DIR.glob("*.png"))
    streamlit_proc: subprocess.Popen[str] | None = None
    try:
        streamlit_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app/main.py",
                "--server.headless",
                "true",
                "--server.port",
                str(APP_PORT),
                "--server.address",
                "127.0.0.1",
                "--browser.gatherUsageStats",
                "false",
            ],
            cwd=ROOT_DIR,
            env={**os.environ, "PYTHONPATH": str(ROOT_DIR)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        wait_for_app_ready()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1440, "height": 900}, device_scale_factor=1
            )

            for url_path, expected_texts, file_name in PAGE_TARGETS:
                try:
                    goto_page(page, url_path)
                except PlaywrightTimeoutError:
                    print(f"[WARN] Could not open URL path: {url_path}")
                    raise
                if not ensure_any_text(page, expected_texts):
                    raise RuntimeError(f"Expected markers not found for: {file_name}")
                capture_current_page(page, OUTPUT_DIR / file_name)

            goto_page(page, "lgpd-privacy-risk")
            try_capture_privacy_preview(page)
            browser.close()
    finally:
        if streamlit_proc is not None and streamlit_proc.poll() is None:
            streamlit_proc.terminate()
            try:
                streamlit_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                streamlit_proc.kill()

    after_pngs = set(OUTPUT_DIR.glob("*.png"))
    generated_now = sorted(path for path in after_pngs if path not in before_pngs)
    if not after_pngs:
        print(f"[ERROR] No PNG files found in {OUTPUT_DIR}")
        return 1
    print(f"[OK] Refreshed 5 screenshots at 1440 x 900 in {OUTPUT_DIR}")
    if generated_now:
        print(f"[OK] Newly generated in this run: {len(generated_now)}")
    else:
        print(
            "[WARN] No brand-new files were created; existing screenshots were refreshed."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
