"""FastAPI server configuration."""

import dataclasses
import logging
import logging.config
import os
from pathlib import Path

# import dotenv
# from singleton import Singleton

# dotenv.load_dotenv()


@dataclasses.dataclass
class Settings:
    """Server config settings."""

    base_dir: Path = (
        Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
    )

    project_name: str = os.getenv("PROJECT_NAME", default="Pixiee")
    root_url: str = os.getenv("DOMAIN", default="http://localhost:8000")
    debug: bool = os.getenv("DEBUG", default=True)

    # TELETHON
    TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")

    log_config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "standard",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "filename": base_dir / "logs" / "info.log",
                "formatter": "standard",
            },
            "errors": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "filename": base_dir / "logs" / "error.log",
                "formatter": "standard",
            },
        },
        "formatters": {
            "standard": {
                "format": "[{levelname} : {filename}:{lineno} : {asctime} -> {funcName:10}] {message}",
                "style": "{",
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "errors"],
                "level": (
                    "INFO"
                    if os.getenv("TESTING", default="").lower() not in ["true", "1"]
                    else "DEBUG"
                ),
                "propagate": True,
            },
        },
    }

    @classmethod
    def config_logger(cls):
        if not (cls.base_dir / "logs").exists():
            (cls.base_dir / "logs").mkdir()

        logging.config.dictConfig(cls.log_config)
