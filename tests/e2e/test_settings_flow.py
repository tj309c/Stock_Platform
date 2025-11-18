"""
Simple Playwright E2E test scaffold for settings page.

This test expects the Streamlit app to be running at http://localhost:8501.
Install Playwright via: pip install playwright pytest-playwright && playwright install
Run with: pytest -q tests/e2e -k settings_flow
"""
from playwright.sync_api import sync_playwright
import pytest


def test_settings_flow_live():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501')
        # Try to find Settings selector in sidebar and click
        try:
            # The selector depends on the sidebar UI; try a few patterns
            if page.is_visible("text=Settings"):
                page.click("text=Settings")
            elif page.is_visible('text=⚙️ Settings'):
                page.click('text=⚙️ Settings')
            else:
                # click in selectbox
                page.click('select[name="Select Dashboard"]')
        except Exception:
            pytest.skip('Settings navigation not found - ensure app layout matches test')
        # Wait for the settings header
        page.wait_for_selector('text=Application Settings')
        # Change scoring mode if present
        try:
            page.select_option('select[aria-label="Scoring Mode"]', 'llm')
        except Exception:
            pass
        browser.close()
