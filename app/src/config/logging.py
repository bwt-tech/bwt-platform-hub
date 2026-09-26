import sys

from loguru import logger

from app.src.config.settings import settings


def configure_logging() -> None:
    """Configure loguru with a structured JSON sink.

    Removes the default stderr sink and replaces it with a JSON-formatted
    sink, respecting the log level from settings.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            '{{"time": "{time:YYYY-MM-DDTHH:mm:ss.SSSZ}", '
            '"level": "{level}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"}}'
        ),
        serialize=True,
        colorize=False,
    )


__all__ = ["configure_logging", "logger"]
