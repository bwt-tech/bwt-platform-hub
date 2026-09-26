from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def test_functional_health_check_negative_method(client: TestClient) -> None:
    response = client.post("/health")
    assert response.status_code == 405
    assert "detail" in response.json()
