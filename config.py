"""
Configuration management for the quiz application.

This module handles all application configuration including:
- Environment variables
- Secret key management
- Logging configuration
- Flask app settings
"""

import logging
import os
import secrets
from datetime import timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from constants import SEPARATOR_WIDTH

# Get module logger
logger = logging.getLogger(__name__)


class Config:
    """
    Application configuration class.

    Handles loading configuration from environment variables with sensible defaults.
    Provides methods for setting up logging and managing the secret key.
    """

    # Load environment variables from .env file
    _env_loaded = False

    def __init__(self, env_file: Optional[Path] = None) -> None:
        """
        Initialize configuration.

        Args:
            env_file: Optional path to .env file. If not provided, looks for .env in project root.
        """
        # Load .env file only once
        if not Config._env_loaded:
            if env_file is None:
                # Look for .env in the same directory as this config.py file
                env_file = Path(__file__).parent / ".env"

            if env_file.exists():
                load_dotenv(env_file)
                logger.info("✓ Loaded environment variables from %s", env_file)
            else:
                # Try loading from current directory as fallback
                load_dotenv()

            Config._env_loaded = True

        # Flask settings
        self.SECRET_KEY = self._get_or_create_secret_key()
        self.DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

        # Session settings
        self.SESSION_COOKIE_SECURE = (
            os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
        )
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"
        self.PERMANENT_SESSION_LIFETIME = timedelta(
            hours=int(os.environ.get("SESSION_LIFETIME_HOURS", "2"))
        )

        # Rate limiting
        self.RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

        # Logging settings
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "True").lower() == "true"
        self.LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "logs/app.log")
        self.LOG_FORMAT = os.environ.get(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.LOG_DATE_FORMAT = os.environ.get("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

        # Quiz settings
        self.MAX_TIME_LIMIT_MINUTES = int(os.environ.get("MAX_TIME_LIMIT_MINUTES", "120"))
        self.MIN_TIME_LIMIT_MINUTES = int(os.environ.get("MIN_TIME_LIMIT_MINUTES", "1"))
        self.DEFAULT_TIME_LIMIT_MINUTES = int(os.environ.get("DEFAULT_TIME_LIMIT_MINUTES", "10"))

    def _get_or_create_secret_key(self) -> str:
        """
        Get secret key from environment or .env file.

        If SECRET_KEY is not set, generates a new one and provides instructions
        for adding it to .env file for persistence.

        Returns:
            Secret key string
        """
        secret_key = os.environ.get("SECRET_KEY")

        if secret_key:
            return secret_key

        # Generate a new secret key
        new_secret_key = secrets.token_hex(32)

        # Provide helpful guidance
        env_file = Path(__file__).parent / ".env"

        separator = "=" * SEPARATOR_WIDTH
        logger.warning(separator)
        logger.warning("⚠️  WARNING: No SECRET_KEY found in environment!")
        logger.warning(separator)
        logger.warning("A temporary secret key has been generated, but sessions will be")
        logger.warning("invalidated when the server restarts.")
        logger.warning("")
        logger.warning("To fix this, add the following line to your .env file:")
        logger.warning("")
        logger.warning("SECRET_KEY=%s", new_secret_key)
        logger.warning("")

        if not env_file.exists():
            logger.warning("Create the file at: %s", env_file)
            logger.warning("")
            logger.warning("You can also copy .env.example to .env and update it:")
            logger.warning("  cp .env.example .env")
        else:
            logger.warning("Add it to: %s", env_file)

        logger.warning(separator)

        return new_secret_key

    def setup_logging(self) -> None:
        """
        Configure application logging.

        Sets up both console and file logging with proper formatting.
        Creates log directory if it doesn't exist.
        """
        # Create formatter
        formatter = logging.Formatter(
            fmt=self.LOG_FORMAT,
            datefmt=self.LOG_DATE_FORMAT,
        )

        # Get log level
        log_level = getattr(logging, self.LOG_LEVEL, logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (if enabled)
        if self.LOG_TO_FILE:
            log_file = Path(self.LOG_FILE_PATH)

            # Create log directory if it doesn't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            logger.info("✓ Logging to file: %s", log_file)

        # Set Flask's logger to use the same configuration
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

        logger.info("✓ Logging configured (level: %s)", self.LOG_LEVEL)

    def apply_to_flask_app(self, app) -> None:
        """
        Apply configuration to a Flask application.

        Args:
            app: Flask application instance
        """
        app.config.update(
            SECRET_KEY=self.SECRET_KEY,
            DEBUG=self.DEBUG,
            SESSION_COOKIE_SECURE=self.SESSION_COOKIE_SECURE,
            SESSION_COOKIE_HTTPONLY=self.SESSION_COOKIE_HTTPONLY,
            SESSION_COOKIE_SAMESITE=self.SESSION_COOKIE_SAMESITE,
            PERMANENT_SESSION_LIFETIME=self.PERMANENT_SESSION_LIFETIME,
        )

    def __repr__(self) -> str:
        """String representation of config (hides secret key)."""
        return (
            f"Config("
            f"DEBUG={self.DEBUG}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"SECRET_KEY={'***' if self.SECRET_KEY else 'NOT SET'}"
            f")"
        )
