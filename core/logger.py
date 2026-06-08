# logger_config.py
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs.txt"


def setup_logging():
    logger = logging.getLogger("mpesa")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers (important for uvicorn --reload)
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.propagate = False

    return logger


# Create a shared logger instance
logger = setup_logging()
