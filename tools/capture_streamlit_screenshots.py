from __future__ import annotations

from pathlib import Path
import re
import time

from playwright.sync_api import Page, expect, sync_playwright


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "images" / "dashboard"
APP_URL = "http://127.0.0.1:8501"


def wait_for_dashboard(page: Page) -> None:
    page.goto(APP_URL, wait_until="networkidle")
    expect(page.get_by_text("Executive Commerce Analytics")).to_be_visible(timeout=60_000)
    expect(page.get_by_role("heading", name="Filtros Globais")).to_be_visible(timeout=60_000)
    time.sleep(2)


def save_overview(page: Page) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    page.screenshot(path=str(OUTPUT_DIR / "01_overview.png"), full_page=False)


def save_kpis(page: Page) -> None:
    section = page.locator("div.kpi-shell").first
    expect(section).to_be_visible(timeout=30_000)
    section.scroll_into_view_if_needed()
    time.sleep(1)
    section.screenshot(path=str(OUTPUT_DIR / "02_kpis.png"))


def click_nav(page: Page, label: str, section_text: str) -> None:
    page.get_by_role("button", name=label).first.click()
    expect(page.get_by_text(section_text)).to_be_visible(timeout=30_000)
    time.sleep(2)


def save_section(page: Page, section_text: str, output_name: str) -> None:
    heading = page.get_by_role("heading", name=re.compile(re.escape(section_text)))
    expect(heading).to_be_visible(timeout=30_000)
    heading.scroll_into_view_if_needed()
    time.sleep(1)
    page.screenshot(path=str(OUTPUT_DIR / output_name), full_page=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 1400}, device_scale_factor=1.25)
        wait_for_dashboard(page)

        save_overview(page)
        save_kpis(page)

        click_nav(page, "Tempo", "Tendência, sazonalidade e ritmo operacional")
        save_section(page, "Tendência, sazonalidade e ritmo operacional", "03_temporal.png")

        click_nav(page, "Categorias", "Quais categorias sustentam resultado, risco e oportunidade")
        save_section(page, "Quais categorias sustentam resultado, risco e oportunidade", "04_categories.png")

        click_nav(page, "Regional", "Quais UFs geram mais valor e onde o desempenho perde eficiência")
        save_section(page, "Quais UFs geram mais valor e onde o desempenho perde eficiência", "05_geography.png")

        browser.close()


if __name__ == "__main__":
    main()
