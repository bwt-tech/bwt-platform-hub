import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_with_parameterization_happy(
    client, mock_aws_secrets, mock_aws_config
):
    # This functional test now uses session-scoped mocks that
    # prevent real AWS calls and lifespan background threads.
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
