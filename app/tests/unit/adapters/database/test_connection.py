"""Unit tests for the database connection session context manager."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError


def test_get_session_commits_on_success():
    """Covers lines 20-23: session is committed and closed on success."""
    mock_session = MagicMock()

    with patch(
        "app.src.adapters.database.connection.SessionLocal",
        return_value=mock_session,
    ):
        from app.src.adapters.database.connection import get_session

        with get_session() as session:
            assert session is mock_session

    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.rollback.assert_not_called()


def test_get_session_rolls_back_on_exception():
    """Covers lines 24-26: session is rolled back on exception."""
    mock_session = MagicMock()

    with patch(
        "app.src.adapters.database.connection.SessionLocal",
        return_value=mock_session,
    ):
        from app.src.adapters.database.connection import get_session

        with pytest.raises(SQLAlchemyError):
            with get_session():
                raise SQLAlchemyError("DB error")

    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    mock_session.commit.assert_not_called()
