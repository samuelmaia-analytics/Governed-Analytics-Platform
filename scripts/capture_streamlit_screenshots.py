from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "assets" / "screenshots"
APP_URL = "http://127.0.0.1:8501"

PAGE_TARGETS: list[tuple[str, list[str], str]] = [
    ("", ["Executive Summary", "Resumo Executivo"], "executive_overview.png"),
    ("lgpd-privacy-risk", ["LGPD & Privacy Risk", "LGPD e Risco de Privacidade"], "lgpd_privacy_risk.png"),
    ("data-quality", ["Data Quality", "Qualidade de Dados"], "data_quality.png"),
    ("governance-control-center", ["Governance Control Center", "Central de Controles de Governança"], "governance_control_center.png"),
]

PRIVACY_PREVIEW_ANCHORS = [
    "Privacy Transformation Preview",
    "Prévia de Transformações de Privacidade",
    "Prévia de Transformação de Privacidade",
]


def update_readme_screenshots_section() -> None:
    generated_privacy = (OUTPUT_DIR / "privacy_transformation_preview.png").exists()
    screenshots_lines = [
        "## Screenshots",
        "",
        "### Executive Overview",
        "![Executive Overview](assets/screenshots/executive_overview.png)",
        "",
        "### LGPD & Privacy Risk",
        "![LGPD & Privacy Risk](assets/screenshots/lgpd_privacy_risk.png)",
        "",
        "### Data Quality",
        "![Data Quality](assets/screenshots/data_quality.png)",
        "",
        "### Governance Control Center",
        "![Governance Control Center](assets/screenshots/governance_control_center.png)",
        "",
    ]
    if generated_privacy:
        screenshots_lines.extend(
            [
                "### Privacy Transformation Preview",
                "![Privacy Transformation Preview](assets/screenshots/privacy_transformation_preview.png)",
                "",
            ]
        )
    screenshots_block = "\n".join(screenshots_lines)

    readme_targets = [
        (ROOT_DIR / "README.md", "### Como atualizar screenshots localmente"),
        (ROOT_DIR / "README.en.md", "### How to refresh screenshots locally"),
    ]
    for readme_path, marker in readme_targets:
        content = readme_path.read_text(encoding="utf-8")
        start = content.find("## Screenshots")
        end = content.find(marker)
        if start == -1 or end == -1 or end <= start:
            print(f"[WARN] Could not update screenshots section in {readme_path}")
            continue
        updated = content[:start] + screenshots_block + "\n" + content[end:]
        readme_path.write_text(updated, encoding="utf-8")
        print(f"[OK] Updated screenshots section in {readme_path}")


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
    raise TimeoutError(f"Streamlit app did not become ready at {APP_URL} within {timeout_seconds} seconds.")


def goto_page(page: Page, url_path: str) -> None:
    target_url = APP_URL if not url_path else f"{APP_URL}/{url_path}"
    page.goto(target_url, wait_until="networkidle", timeout=45_000)
    time.sleep(2)


def dismiss_page_not_found_modal(page: Page) -> None:
    try:
        if page.get_by_text("Page not found").first.is_visible(timeout=1500):
            close_button = page.get_by_role("button", name="x")
            if close_button.first.is_visible(timeout=1500):
                close_button.first.click()
                time.sleep(1)
    except PlaywrightTimeoutError:
        pass


def ensure_any_text(page: Page, candidates: list[str], timeout_ms: int = 12_000) -> bool:
    for text in candidates:
        try:
            if page.get_by_text(text).first.is_visible(timeout=timeout_ms):
                return True
        except PlaywrightTimeoutError:
            continue
    return False


def capture_current_page(page: Page, output_file: Path) -> None:
    page.wait_for_load_state("networkidle", timeout=30_000)
    time.sleep(2)
    page.screenshot(path=str(output_file), full_page=True)
    print(f"[OK] Saved: {output_file}")


def try_capture_privacy_preview(page: Page) -> None:
    for anchor in PRIVACY_PREVIEW_ANCHORS:
        locator = page.get_by_text(anchor)
        try:
            if locator.first.is_visible(timeout=3000):
                locator.first.scroll_into_view_if_needed()
                time.sleep(2)
                output_file = OUTPUT_DIR / "privacy_transformation_preview.png"
                page.screenshot(path=str(output_file), full_page=True)
                print(f"[OK] Saved: {output_file}")
                return
        except PlaywrightTimeoutError:
            continue
    print("[WARN] Privacy Transformation Preview section not found; skipping optional screenshot.")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    before_pngs = set(OUTPUT_DIR.glob("*.png"))
    streamlit_proc: subprocess.Popen[str] | None = None
    try:
        streamlit_proc = subprocess.Popen(
            [
                "python",
                "-m",
                "streamlit",
                "run",
                "app/main.py",
                "--server.headless",
                "true",
                "--server.port",
                "8501",
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
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.goto(APP_URL, wait_until="networkidle")
            time.sleep(2)

            for url_path, expected_texts, file_name in PAGE_TARGETS:
                try:
                    goto_page(page, url_path)
                except PlaywrightTimeoutError:
                    print(f"[WARN] Could not open URL path: {url_path}")
                    continue
                dismiss_page_not_found_modal(page)
                if not ensure_any_text(page, expected_texts):
                    print(f"[WARN] Expected markers not found for: {file_name}")
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
    print(f"[OK] Total PNG files in {OUTPUT_DIR}: {len(after_pngs)}")
    if generated_now:
        print(f"[OK] Newly generated in this run: {len(generated_now)}")
    else:
        print("[WARN] No brand-new files were created; existing screenshots were refreshed.")
    update_readme_screenshots_section()
    return 0


if __name__ == "__main__":
    sys.exit(main())
