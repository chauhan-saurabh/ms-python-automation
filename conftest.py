# conftest.py

import pytest
import base64
import os
import platform
import subprocess
from datetime import datetime
from playwright.sync_api import sync_playwright
from pytest_html import extras as html_extras


# -----------------------------------
# DIRECTORIES
# -----------------------------------

REPORT_DIR     = "reports"
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")

os.makedirs(REPORT_DIR,     exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# -----------------------------------
# STEP TRACKER
# -----------------------------------

class StepTracker:
    """
    Records named steps during a test run.
    Inject via the `steps` fixture and call:
        steps.add("Navigate to PDP")
        steps.fail("Size not found")
        steps.info("Retrying selector")
    """

    def __init__(self):
        self._steps: list[dict] = []

    def add(self, label: str, status: str = "pass"):
        self._steps.append({
            "label":  label,
            "status": status,
            "time":   datetime.now().strftime("%H:%M:%S"),
        })

    def fail(self, label: str):
        self.add(label, "fail")

    def info(self, label: str):
        self.add(label, "info")

    @property
    def steps(self):
        return list(self._steps)


@pytest.fixture(scope="function")
def steps():
    return StepTracker()


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
            viewport={"width": 1440, "height": 900}
        )

        page = context.new_page()

        yield page

        context.close()
        browser.close()


# -----------------------------------
# ENVIRONMENT METADATA
# -----------------------------------

def pytest_configure(config):

    config._metadata = getattr(config, "_metadata", {})

    config._metadata["Project"]     = "Marks & Spencer — E2E Automation"
    config._metadata["Browser"]     = "Chromium (Playwright)"
    config._metadata["Base URL"]    = "https://www.marksandspencer.in"
    config._metadata["Environment"] = "Production"
    config._metadata["Platform"]    = platform.platform()
    config._metadata["Python"]      = platform.python_version()
    config._metadata["Run Date"]    = datetime.now().strftime("%d %b %Y  %H:%M:%S")

    try:
        ver = subprocess.check_output(
            ["python", "-m", "playwright", "--version"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        config._metadata["Playwright"] = ver
    except Exception:
        pass


# -----------------------------------
# REPORT TITLE
# -----------------------------------

def pytest_html_report_title(report):
    report.title = "M&S Automation — Test Report"


# -----------------------------------
# BANNER + CSS
# -----------------------------------

def pytest_html_results_summary(prefix, summary, postfix):

    now = datetime.now().strftime("%d %b %Y, %H:%M:%S")

    html = f"""
    <style>{_custom_css()}</style>
    <div class="ms-banner">
        <div class="ms-banner-left">
            <span class="ms-logo">M&amp;S</span>
            <div>
                <div class="ms-banner-title">Automation Test Report</div>
                <div class="ms-banner-subtitle">End-to-End · Playwright · Python</div>
            </div>
        </div>
        <div class="ms-banner-right">
            <span class="ms-tag">Production</span>
            <span class="ms-run-time">🕐 {now}</span>
        </div>
    </div>
    """

    prefix.extend([html_extras.html(html)])


# -----------------------------------
# TRACK CURRENT ITEM
# -----------------------------------

class _CurrentItem:
    def __init__(self):
        self._item = None

    def set(self, item):
        self._item = item

    def get(self):
        return self._item


_current_item = _CurrentItem()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    _current_item.set(item)
    return None


# -----------------------------------
# PER-TEST EXTRAS  (pytest-html v4)
# report.extras  (not report.extra)
# -----------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    report  = outcome.get_result()

    if report.when != "call":
        return

    page      = item.funcargs.get("page")
    tracker   = item.funcargs.get("steps")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = item.name.replace("/", "_").replace("::", "_")
    status    = "FAILED" if report.failed else "PASSED"

    extra_list = []

    # 1. Step timeline
    if tracker and tracker.steps:
        extra_list.append(html_extras.html(_steps_card(tracker.steps, status)))

    # 2. Screenshot
    if page:
        filename = f"{status}_{test_name}_{timestamp}.png"
        path     = os.path.join(SCREENSHOT_DIR, filename)
        try:
            page.screenshot(path=path, full_page=True)
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            extra_list.append(html_extras.html(_screenshot_card(b64, status, timestamp)))
            if report.failed:
                print(f"\nSCREENSHOT SAVED => {path}")
        except Exception as e:
            print(f"\nSCREENSHOT ERROR => {e}")

    # 3. Meta card
    extra_list.append(html_extras.html(
        _meta_card(
            test_name = item.name,
            node_id   = item.nodeid,
            duration  = getattr(report, "duration", 0),
            status    = status,
            markers   = [m.name for m in item.iter_markers()],
            longrepr  = str(report.longrepr) if report.failed else None,
        )
    ))

    # pytest-html v4 uses .extras (plural)
    report.extras = (getattr(report, "extras", None) or []) + extra_list


# -----------------------------------
# HTML HELPERS
# -----------------------------------

def _steps_card(steps: list, overall_status: str) -> str:

    total  = len(steps)
    passed = sum(1 for s in steps if s["status"] == "pass")
    failed = sum(1 for s in steps if s["status"] == "fail")

    rows = ""
    for i, step in enumerate(steps, 1):
        icon  = {"pass": "✅", "fail": "❌", "info": "ℹ️"}.get(step["status"], "•")
        color = {"pass": "#27ae60", "fail": "#e74c3c", "info": "#2471a3"}.get(step["status"], "#888")
        bg    = {"pass": "#f0faf4", "fail": "#fdf2f2", "info": "#eaf2ff"}.get(step["status"], "#fff")

        rows += f"""
        <tr style="background:{bg}">
            <td style="color:#aaa;padding:7px 10px;width:30px;text-align:center;font-size:0.8rem">{i}</td>
            <td style="padding:7px 10px;font-weight:600;color:{color}">{icon}&nbsp;{_escape(step["label"])}</td>
            <td style="padding:7px 10px;color:#aaa;font-size:0.78rem;text-align:right">{step["time"]}</td>
        </tr>
        """

    header_color = "#27ae60" if overall_status == "PASSED" else "#e74c3c"
    fail_badge   = f"&nbsp;·&nbsp;<span style='color:#e74c3c'>{failed} failed</span>" if failed else ""

    return f"""
    <div class="ms-card" style="border-left-color:{header_color}">
        <div class="ms-card-header" style="color:{header_color}">
            🪜 Test Steps
            <span style="font-size:0.8rem;font-weight:400;color:#888">
                {total} steps &nbsp;·&nbsp;
                <span style="color:#27ae60">{passed} passed</span>
                {fail_badge}
            </span>
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:0.88rem;border-radius:6px;overflow:hidden">
            {rows}
        </table>
    </div>
    """


def _screenshot_card(b64: str, label: str, timestamp: str) -> str:

    border = "#e74c3c" if label == "FAILED" else "#27ae60"
    icon   = "❌" if label == "FAILED" else "✅"

    return f"""
    <div class="ms-card" style="border-left-color:{border}">
        <div class="ms-card-header" style="color:{border}">
            {icon} Final Screenshot — {label}
            <span class="ms-ts">{timestamp}</span>
        </div>
        <img
            src="data:image/png;base64,{b64}"
            class="ms-screenshot"
            onclick="this.classList.toggle('ms-screenshot-zoom')"
            title="Click to zoom"
        />
        <div class="ms-hint">Click image to zoom</div>
    </div>
    """


def _meta_card(
    test_name: str,
    node_id:   str,
    duration:  float,
    status:    str,
    markers:   list,
    longrepr:  "str | None",
) -> str:

    color     = "#e74c3c" if status == "FAILED" else "#27ae60"
    badge_cls = "ms-badge-fail" if status == "FAILED" else "ms-badge-pass"

    marker_str = "".join(
        f'<span class="ms-marker">@{m}</span>' for m in markers
    ) or '<span class="ms-marker ms-marker-none">none</span>'

    error_block = ""
    if longrepr:
        lines   = longrepr.strip().splitlines()
        trimmed = "\n".join(lines[-20:])
        error_block = f"""
        <div class="ms-error-header">💥 Failure Details</div>
        <pre class="ms-traceback">{_escape(trimmed)}</pre>
        """

    return f"""
    <div class="ms-card" style="border-left-color:{color}">
        <div class="ms-card-header">
            📋 Test Details
            <span class="ms-badge {badge_cls}">{status}</span>
        </div>
        <table class="ms-meta-table">
            <tr><td>Test</td>    <td><code>{_escape(test_name)}</code></td></tr>
            <tr><td>Node ID</td> <td><code>{_escape(node_id)}</code></td></tr>
            <tr><td>Duration</td><td><strong>{duration:.2f}s</strong></td></tr>
            <tr><td>Markers</td> <td>{marker_str}</td></tr>
        </table>
        {error_block}
    </div>
    """


def _escape(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">",  "&gt;")
    )


def _custom_css() -> str:
    return """
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f6fa; }
    #results-table { border-radius: 8px; overflow: hidden; }

    .ms-banner {
        display: flex; align-items: center; justify-content: space-between;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        color: #fff; padding: 20px 28px; border-radius: 12px;
        margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    .ms-banner-left  { display: flex; align-items: center; gap: 16px; }
    .ms-banner-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .ms-logo {
        font-size: 2rem; font-weight: 900; background: #fff; color: #1a1a2e;
        padding: 6px 14px; border-radius: 6px; letter-spacing: 2px;
    }
    .ms-banner-title    { font-size: 1.3rem; font-weight: 700; }
    .ms-banner-subtitle { font-size: 0.85rem; opacity: 0.75; margin-top: 2px; }
    .ms-tag {
        background: #e74c3c; padding: 4px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
    }
    .ms-run-time { font-size: 0.85rem; opacity: 0.85; }

    .ms-card {
        background: #fff; border-left: 5px solid #3498db; border-radius: 8px;
        padding: 16px 20px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .ms-card-header {
        font-weight: 700; font-size: 0.95rem; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .ms-ts { font-size: 0.78rem; color: #888; font-weight: 400; }

    .ms-screenshot {
        width: 100%; max-width: 900px; border: 1px solid #ddd;
        border-radius: 6px; cursor: zoom-in; transition: transform 0.3s ease; display: block;
    }
    .ms-screenshot-zoom {
        transform: scale(1.6); transform-origin: top left;
        z-index: 999; position: relative; cursor: zoom-out;
    }
    .ms-hint { font-size: 0.75rem; color: #aaa; margin-top: 6px; }

    .ms-meta-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .ms-meta-table td { padding: 5px 10px; vertical-align: top; }
    .ms-meta-table td:first-child {
        font-weight: 600; color: #555; white-space: nowrap; width: 90px;
    }
    .ms-meta-table code {
        background: #f0f0f0; padding: 2px 6px; border-radius: 4px;
        font-size: 0.83rem; word-break: break-all;
    }

    .ms-badge {
        font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
        border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .ms-badge-pass { background: #d5f5e3; color: #1e8449; }
    .ms-badge-fail { background: #fadbd8; color: #c0392b; }

    .ms-marker {
        display: inline-block; background: #eaf2ff; color: #2471a3;
        font-size: 0.78rem; padding: 2px 8px; border-radius: 4px; margin-right: 4px;
    }
    .ms-marker-none { background: #f5f5f5; color: #aaa; }

    .ms-error-header { font-weight: 700; color: #c0392b; margin: 14px 0 6px; font-size: 0.88rem; }
    .ms-traceback {
        background: #1e1e2e; color: #f8f8f2; padding: 12px 16px; border-radius: 6px;
        font-size: 0.8rem; overflow-x: auto; white-space: pre-wrap;
        word-break: break-word; max-height: 300px; overflow-y: auto;
    }
    """