# run_tests.py

import os
from utils.report_summary import create_summary

os.system("pytest tests/test_cart.py -v -s")

create_summary()