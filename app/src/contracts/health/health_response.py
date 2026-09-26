from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Response contract for the GET /health endpoint."""

    model_config = ConfigDict(strict=True)

    status: Literal["healthy"]
