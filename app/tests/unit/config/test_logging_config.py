import sys
from unittest.mock import patch

from app.src.config.logging import configure_logging


def test_configure_logging_adds_stdout_sink():
    """Covers app/src/config/logging.py lines 1-31: configure_logging() removes
    the default sink and adds a structured JSON sink to stdout."""
    with patch("app.src.config.logging.logger") as mock_logger:
        configure_logging()

        mock_logger.remove.assert_called_once()
        mock_logger.add.assert_called_once()

        call_kwargs = mock_logger.add.call_args
        positional = call_kwargs[0]
        keyword = call_kwargs[1]

        assert positional[0] is sys.stdout
        assert keyword.get("serialize") is True
        assert keyword.get("colorize") is False
