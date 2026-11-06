"""Automated screenshot capture script for SpendStory Recomposition & Visual Redesign.
Captures high-resolution evidence across desktop, laptop, tablet, and mobile viewports.
"""

from pathlib import Path
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("docs/screenshots/recomposition")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://127.0.0.1:8501"

PAGES = [
    ("01_overview_desktop_1440.png", f"{BASE_URL}/?nav=Overview&month=2026-11", 1440, 960),
    ("02_transactions_desktop_1440.png", f"{BASE_URL}/?nav=Transactions&month=2026-11", 1440, 960),
    ("03_budgets_desktop_1440.png", f"{BASE_URL}/?nav=Budgets&month=2026-11", 1440, 960),
    ("04_category_review_desktop_1440.png", f"{BASE_URL}/?nav=Category+Review&month=2026-11", 1440, 960),
    ("05_model_eval_desktop_1440.png", f"{BASE_URL}/?nav=Model+Evaluation&month=2026-11", 1440, 960),
    ("06_overview_laptop_1280.png", f"{BASE_URL}/?nav=Overview&month=2026-11", 1280, 800),
    ("07_overview_tablet_768.png", f"{BASE_URL}/?nav=Overview&month=2026-11", 768, 1024),
    ("08_overview_mobile_375.png", f"{BASE_URL}/?nav=Overview&month=2026-11", 375, 812),
]


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for filename, url, width, height in PAGES:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=2,
            )
            page = context.new_page()
            print(f"Loading {url} at {width}x{height}...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Allow Streamlit and components to settle
            page.wait_for_timeout(2500)
            
            output_path = OUTPUT_DIR / filename
            page.screenshot(path=str(output_path), full_page=False)
            print(f"Captured: {output_path} ({width}x{height})")
            context.close()
        browser.close()


if __name__ == "__main__":
    capture()
