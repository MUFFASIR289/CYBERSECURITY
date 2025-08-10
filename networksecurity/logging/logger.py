import logging
import os
from datetime import datetime

# Create log file name with timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Use a safe directory (home folder)
logs_dir = os.path.expanduser("~/NetworkLogs")
os.makedirs(logs_dir, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)
print(f"Logging to: {LOG_FILE_PATH}")

logger = logging.getLogger("networksecurity")

# Clear existing handlers to avoid conflicts
if logger.hasHandlers():
    logger.handlers.clear()

# Add fresh file handler with UTF-8 encoding
file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
formatter = logging.Formatter("[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)