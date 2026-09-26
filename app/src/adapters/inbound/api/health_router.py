from fastapi import APIRouter
from loguru import logger

from app.src.contracts.health.health_response import HealthResponse
from app.src.services.health_service import HealthService

router = APIRouter()
service = HealthService()


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Check application health status."""
    logger.debug("health check", status="healthy")
    return service.get()
