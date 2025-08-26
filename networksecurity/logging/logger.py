import logging
import os
from datetime import datetime

# Create log file name with timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Define log directory
LOGS_DIR = os.path.join(os.path.expanduser("~"), "NetworkLogs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Full path to log file
LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE)

# Optional: print log path for debugging (can be removed in production)
print(f"Logging to: {LOG_FILE_PATH}")

# Create logger instance
logger = logging.getLogger("networksecurity")
logger.setLevel(logging.INFO)

# Clear existing handlers to avoid duplicate logs
if logger.hasHandlers():
    logger.handlers.clear()

# Create file handler
file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
formatter = logging.Formatter("[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)