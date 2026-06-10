import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from pages.control_aduanero_page import ControlAduaneroPage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@pytest.fixture
def page(base_url):
    browser_channel = os.getenv("BROWSER_CHANNEL", "msedge")
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    slow_mo = int(os.getenv("SLOW_MO", "0"))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel=browser_channel,
            headless=headless,
            slow_mo=slow_mo,
            args=["--start-maximized"],
        )
        context = browser.new_context(
            base_url=base_url,
            no_viewport=True,
            timezone_id="America/Guatemala",
            locale="es-GT",
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        test_page = context.new_page()
        yield test_page
        trace_path = f"trace_{os.environ.get('PYTEST_CURRENT_TEST', 'test').split(' ')[0].replace('::', '_')}.zip"
        context.tracing.stop(path=trace_path)
        browser.close()


@pytest.fixture
def control_aduanero_page(page):
    return ControlAduaneroPage(page)