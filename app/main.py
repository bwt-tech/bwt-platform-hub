import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from loguru import logger

from app.src.adapters.inbound.api.health_router import router as health_router
from app.src.adapters.inbound.background.scheduler import (
    ReverseSyncronizerScheduler,
    SyncronizerScheduler,
)
from app.src.adapters.outbounds.aws_secrets_adapter import AWSSecretsManagerAdapter
from app.src.config.settings import settings


def init_configs():

    logger.info(f"Buscando configs: {settings.aws_endpoint_url} {settings.aws_region}")
    _secrets_adapter = AWSSecretsManagerAdapter(
        region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    )
    settings.load_from_secrets_manager(_secrets_adapter)

    sentry_sdk.init(
        dsn=settings.sentry_url,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        traces_sample_rate=1.0,
        event_scrubber=None,
        enable_logs=True,
    )
    sentry_sdk.set_context(
        "culture",
        {
            "locale": "pt-BR",  # Standard BCP 47 language tag
            "timezone": "America/Sao_Paulo",  # Canonical IANA timezone name
        },
    )
    logger.info("Configs OK")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "Application starting up", app_name=settings.app_name, port=settings.port
    )

    # Start scheduler thread
    thread = threading.Thread(target=SyncronizerScheduler().start)
    thread.daemon = True
    thread.start()

    # Start reverse scheduler thread
    reverse_thread = threading.Thread(target=ReverseSyncronizerScheduler().start)
    reverse_thread.daemon = True
    reverse_thread.start()

    yield
    logger.info("Application shutting down")


init_configs()
app = FastAPI(
    title=settings.app_name,
    description="Integration hub microservice for third-party services",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
