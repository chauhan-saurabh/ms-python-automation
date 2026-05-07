# conftest.py

import pytest
from playwright.sync_api import sync_playwright
from datetime import datetime
import os


# -----------------------------------
# CREATE REPORT FOLDER
# -----------------------------------

REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)


# -----------------------------------
# PLAYWRIGHT FIXTURE
# -----------------------------------

@pytest.fixture(scope="function")
def page():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            slow_mo=100
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        page = context.new_page()

        yield page

        context.close()
        browser.close()


# -----------------------------------
# SCREENSHOT ON FAILURE
# -----------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):

    outcome = yield

    report = outcome.get_result()

    extra = getattr(report, "extra", [])

    if report.when == "call":

        page = item.funcargs.get("page")

        if report.failed and page:

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            screenshot_path = (
                f"reports/failure_{timestamp}.png"
            )

            page.screenshot(
                path=screenshot_path,
                full_page=True
            )

            print(
                f"\nSCREENSHOT SAVED => {screenshot_path}"
            )