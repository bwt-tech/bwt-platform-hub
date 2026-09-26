from unittest.mock import MagicMock

from app.src.config.settings import Settings, _build_database_url


def test_settings_load_from_aws_success():
    # Prepare
    mock_adapter = MagicMock()
    mock_adapter.get_secret.return_value = {
        "OCTADESK_API_KEY": "aws-key",
        "OCTADESK_SUBDOMAIN": "aws-sub",
        "RDSTATION_TOKEN": "aws-token",
    }

    settings = Settings()

    # Execute
    # We expect a method like 'load_secrets' or similar to be implemented in T014
    settings.load_from_secrets_manager(mock_adapter)

    # Assert
    assert settings.octadesk_api_key == "aws-key"
    assert settings.octadesk_subdomain == "aws-sub"
    assert settings.rdstation_token == "aws-token"


def test_settings_load_from_aws_fallback_on_error():
    # Prepare
    mock_adapter = MagicMock()
    mock_adapter.get_secret.side_effect = Exception("AWS Down")

    # Start with some defaults or env values
    settings = Settings(
        octadesk_api_key="env-key",
        octadesk_subdomain="env-sub",
        rdstation_token="env-token",
    )

    # Execute
    settings.load_from_secrets_manager(mock_adapter)

    # Assert - should keep original values
    assert settings.octadesk_api_key == "env-key"
    assert settings.octadesk_subdomain == "env-sub"
    assert settings.rdstation_token == "env-token"


def test_resolve_database_url_uses_full_url_when_set(monkeypatch):
    """Covers line 22: when DATABASE_URL env var is set directly, return it."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    result = _build_database_url()
    assert result == "postgresql://user:pass@host:5432/db"


def test_resolve_database_url_uses_components_when_set(monkeypatch):
    """Covers line 31: when DB_* components are all set, build and return composite URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_HOST", "my-host")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "mydb")
    monkeypatch.setenv("DB_USER", "myuser")
    monkeypatch.setenv("DB_PASSWORD", "mypass")
    result = _build_database_url()
    assert result == "postgresql://myuser:mypass@my-host:5433/mydb"

