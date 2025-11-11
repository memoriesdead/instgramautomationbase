"""
Logging configuration for Instagram bot
"""

import logging
import sys
from datetime import datetime

def setup_logging():
    """Configure logging with both file and console output"""

    # Create timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"instagram_bot_{timestamp}.log"

    # Create logger
    logger = logging.getLogger('InstagramBot')
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create file handler (detailed logs)
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Create console handler (important logs only)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("="*60)
    logger.info(f"Logging initialized - Log file: {log_filename}")
    logger.info("="*60)

    return logger, log_filename
