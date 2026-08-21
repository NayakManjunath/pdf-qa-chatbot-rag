"""
Production Logging Configuration

Centralized logging configuration for the PDF Q&A RAG application.
"""

import logging
import os


DEFAULT_LOG_LEVEL = "INFO"

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    DEFAULT_LOG_LEVEL,
).upper()


VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


if LOG_LEVEL not in VALID_LOG_LEVELS:
    LOG_LEVEL = DEFAULT_LOG_LEVEL


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def configure_logging() -> None:
    """
    Configure application-wide logging.

    The log level can be controlled through the LOG_LEVEL
    environment variable.

    Example:

        LOG_LEVEL=DEBUG
    """

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
    )

    # ---------------------------------------------------------
    # Third-party library noise control
    # ---------------------------------------------------------

    noisy_loggers = {
        "httpx": logging.WARNING,
        "sentence_transformers": logging.WARNING,
        "huggingface_hub": logging.WARNING,
        "urllib3": logging.WARNING,
        "chromadb": logging.WARNING,
    }

    for logger_name, level in noisy_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


# Configure logging when this module is imported.
configure_logging()