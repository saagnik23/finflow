"""Automated micro-interaction and cursor verification script for SpendStory Recomposition."""

import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8501/?nav=Overview&month=2026-11"


def verify_cursor():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. Hover on Neutral Background
        page.mouse.move(100, 100)
        time.sleep(0.5)
        neutral_state = page.evaluate("""() => {
            const el = document.getElementById("spendstory-cursor-follower");
            return {
                exists: !!el,
                isInteractive: el ? el.classList.contains("is-interactive") : null,
                opacity: el ? window.getComputedStyle(el).opacity : null,
            };
        }""")
        print("Neutral canvas state:", neutral_state)
        assert neutral_state["exists"], "Follower element must exist"
        assert not neutral_state["isInteractive"], "Neutral canvas must show arrow (not interactive)"

        # 2. Hover on Segmented Nav Button
        nav_button = page.get_by_role("button", name="Transactions").first
        nav_button.hover()
        time.sleep(0.5)
        nav_state = page.evaluate("""() => {
            const el = document.getElementById("spendstory-cursor-follower");
            return {
                isInteractive: el ? el.classList.contains("is-interactive") : null,
            };
        }""")
        print("Nav pill hover state:", nav_state)
        assert nav_state["isInteractive"], "Hovering over nav pill must switch cursor to Hand"

        # 3. Hover on Search Input
        search_input = page.locator('input[aria-label="Search"]').first
        search_input.hover()
        time.sleep(0.5)
        input_state = page.evaluate("""() => {
            const el = document.getElementById("spendstory-cursor-follower");
            return {
                opacity: el ? window.getComputedStyle(el).opacity : null,
            };
        }""")
        print("Text input hover state (follower suppressed for native I-beam):", input_state)
        assert float(input_state["opacity"]) == 0.0, "Follower opacity must be 0 over input field"

        # 4. Pointer Down / Press
        page.mouse.move(200, 200)
        page.mouse.down()
        time.sleep(0.2)
        down_state = page.evaluate("""() => {
            const el = document.getElementById("spendstory-cursor-follower");
            return {
                isPressed: el ? el.classList.contains("is-pressed") : null,
            };
        }""")
        print("Pointer down state:", down_state)
        assert down_state["isPressed"], "Active mouse down must apply is-pressed class"
        page.mouse.up()

        browser.close()
        print("All cursor micro-interactions passed verification!")


if __name__ == "__main__":
    verify_cursor()
