import sys

from loguru import logger

LEVEL_SHORTHAND = {
    "TRACE": "TRC",
    "DEBUG": "DBG",
    "INFO": "INF",
    "SUCCESS": "SUC",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}
"""Three-letter shorthand for each built-in loguru level name."""

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{extra[lvl]}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
"""Log line format shared by the console and file handlers."""


def _add_level_shorthand(record):
    """Store the level shorthand in `record["extra"]["lvl"]`.

    Levels missing from `LEVEL_SHORTHAND` (e.g. custom levels) keep their full name.
    """
    name = record["level"].name
    record["extra"]["lvl"] = LEVEL_SHORTHAND.get(name, name)


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
    - File handler at DEBUG level writing to LOG_FILE (default: app.log)

    Both handlers use `LOG_FORMAT`, which produces lines like:

        2026-10-24 20:33:18 | INF | second_brain.app:main:29 - Hello from second_brain!

    Timestamps have no milliseconds, and levels are shown as the three-letter
    shorthand from `LEVEL_SHORTHAND` (custom levels fall back to their full name).
    Console output is colored by level; the log file is plain text.
    """
    import os

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE", "app.log")
    logger.remove()
    logger.configure(patcher=_add_level_shorthand)
    logger.add(sys.stderr, level=log_level, format=LOG_FORMAT)
    logger.add(
        log_file, level="DEBUG", format=LOG_FORMAT, rotation="50 KB", retention=1
    )


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from second_brain!")
