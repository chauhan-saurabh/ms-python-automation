# utils/report_summary.py

from datetime import datetime


def create_summary():

    summary = f"""

========================================
M&S INDIA AUTOMATION EXECUTION SUMMARY
========================================

Execution Date:
{datetime.now()}

Automation Scope:
- Homepage Validation
- Product Search
- PDP Validation
- Size Selection
- Type/Fit Selection
- Add To Cart
- Cart Validation
- Checkout Flow
- Login Validation

Framework:
- Python
- Pytest
- Playwright

Browser:
- Chromium

Artifacts Generated:
- HTML Report
- Failure Screenshots
- Execution Logs

========================================
"""

    with open(
        "reports/execution_summary.txt",
        "w"
    ) as f:

        f.write(summary)