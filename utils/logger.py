# utils/logger.py

import logging
import os


os.makedirs("reports/logs", exist_ok=True)

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    handlers=[

        logging.FileHandler(
            "reports/logs/test_execution.log"
        ),

        logging.StreamHandler()
    ]
)

logger = logging.getLogger()