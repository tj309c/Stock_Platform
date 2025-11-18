from playwright.sync_api import sync_playwright
import os


def test_snapshot_basic():
    # This test requires Playwright browsers and Streamlit app running at localhost:8501
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501')
        # Take snapshot of landing page
        path = 'tests/e2e/snapshots/landing.png'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        page.screenshot(path=path)
        browser.close()
        assert os.path.exists(path)
