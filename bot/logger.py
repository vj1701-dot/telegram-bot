"""Logging configuration for the bot."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from shared.constants import LOG_ROTATION_SIZE, MAX_BACKUP_COUNT


def setup_logger(name: str, log_dir: Path = Path("/app/data/logs"),
                 level: str = "INFO") -> logging.Logger:
    """Configure logger with file and console handlers."""

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}.log"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_ROTATION_SIZE,
        backupCount=MAX_BACKUP_COUNT
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(file_format)
    logger.addHandler(console_handler)

    return logger


# Initialize root logger
root_logger = setup_logger("bot")
