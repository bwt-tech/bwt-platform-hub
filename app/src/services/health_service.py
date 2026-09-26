from app.src.contracts.health.health_response import HealthResponse
from app.src.core.health import get_health_status


class HealthService:
    """Service to handle health-related operations."""

    def get(self) -> HealthResponse:
        """Get the current health status wrapped in a HealthResponse contract."""
        result = get_health_status()
        # Mypy correctly warns that a generic str is not formally Literal["healthy"].
        # Pydantic's strict mode validates this at runtime.
        return HealthResponse(status=result["status"])  # type: ignore[arg-type]
