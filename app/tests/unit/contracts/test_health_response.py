import pytest
from pydantic import ValidationError

from app.src.contracts.health.health_response import HealthResponse


def test_health_response_positive() -> None:
    response = HealthResponse(status="healthy")
    assert response.status == "healthy"


def test_health_response_negative_wrong_string() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status="unhealthy")  # type: ignore[arg-type]


def test_health_response_negative_wrong_type() -> None:
    with pytest.raises(ValidationError):
        HealthResponse(status=1)  # type: ignore[arg-type]
