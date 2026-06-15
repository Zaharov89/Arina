import logging
import logging.config
import os
from pathlib import Path

from Arina.config import LOG_LEVEL, LOG_TO_FILE, LOG_DIR


def configure_logging() -> None:
    """Configure application logging once for Flask, DB and business services."""
    log_level = str(LOG_LEVEL or "INFO").upper()
    handlers = ["console"]
    log_dir = Path(LOG_DIR)
    if LOG_TO_FILE:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append("file")

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": str(log_dir / "arina.log"),
                "maxBytes": 2_000_000,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": log_level,
            "handlers": handlers,
        },
        "loggers": {
            "werkzeug": {"level": "WARNING", "handlers": handlers, "propagate": False},
            "sqlalchemy.engine": {"level": os.getenv("ARINA_SQL_LOG_LEVEL", "WARNING"), "handlers": handlers, "propagate": False},
            "Arina": {"level": log_level, "handlers": handlers, "propagate": False},
        },
    }
    logging.config.dictConfig(logging_config)
    logging.getLogger(__name__).info("Logging configured: level=%s, file=%s, dir=%s", log_level, LOG_TO_FILE, log_dir)
