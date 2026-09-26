from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def test_health_router_get(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_router_post_method_not_allowed(client: TestClient) -> None:
    response = client.post("/health")
    assert response.status_code == 405


def test_health_router_put_method_not_allowed(client: TestClient) -> None:
    response = client.put("/health")
    assert response.status_code == 405


def test_health_router_delete_method_not_allowed(client: TestClient) -> None:
    response = client.delete("/health")
    assert response.status_code == 405
