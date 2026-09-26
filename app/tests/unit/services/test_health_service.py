from app.src.contracts.health.health_response import HealthResponse
from app.src.services.health_service import HealthService


def test_health_service_get_returns_health_response() -> None:
    service = HealthService()
    result = service.get()
    assert isinstance(result, HealthResponse)
    assert result.status == "healthy"
