import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


from unittest.mock import patch


def test_app_startup_fallback_on_aws_error(client, mock_aws_secrets, mock_aws_config):
    # Simulate errors by patching the client methods
    # (since moto clients are real objects, we patch their methods)
    with patch.object(
        mock_aws_secrets,
        "get_secret_value",
        side_effect=Exception("Secrets Manager Unreachable"),
    ), patch.object(
        mock_aws_config, "get_parameters", side_effect=Exception("SSM Unreachable")
    ):

        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
