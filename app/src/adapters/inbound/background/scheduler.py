import json
import os
from datetime import datetime
from app.src.core.datetime_utils import get_now

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.src.adapters.database.connection import get_session
from app.src.adapters.database.repositories.chat_repository_adapter import (
    SQLAlchemyChatRepositoryAdapter,
)
from app.src.adapters.database.repositories.contact_repository_adapter import (
    SQLAlchemyContactRepositoryAdapter,
)
from app.src.adapters.database.repositories.deal_repository_adapter import (
    SQLAlchemyDealRepositoryAdapter,
)
from app.src.adapters.outbounds.aws_config_adapter import AWSParameterStoreAdapter
from app.src.adapters.outbounds.aws_s3_adapter import AWSS3Adapter
from app.src.adapters.outbounds.octadesk import OctadeskAdapter
from app.src.adapters.outbounds.rdstation import RDStationAdapter
from app.src.config.settings import settings
from app.src.services.orchestrator import OrchestratorService
from app.src.services.orchestrator_reverse import OrchestratorReverseService

# Global scheduler instance
scheduler = BackgroundScheduler()

class SyncronizerScheduler:
    _instance = None
    _job_id = "sync_job"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):  # pragma: no cover
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._config_adapter = AWSParameterStoreAdapter(
            region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
        )

        # 3. Load initial configuration from Parameter Store
        self._config = self._config_adapter.get_scheduler_config()

        # 4. Initialize Core Business Adapters (using resolved settings)
        self._octadesk = OctadeskAdapter(
            api_key=settings.octadesk_api_key or os.getenv("OCTADESK_API_KEY"),
            base_url=settings.octadesk_base_url or os.getenv("OCTADESK_BASE_URL")
        )
        self._rdstation = RDStationAdapter(
            token=settings.rdstation_token or os.getenv("RDSTATION_TOKEN")
        )
        self.s3_adapter = AWSS3Adapter(
            region_name=settings.aws_region,
        )

        self._initialized = True

    def start(self):
        """Starts the background scheduler and registers jobs."""

        # A. Schedule the main synchronization job
        self._add_job(
            self._execute, CronTrigger.from_crontab(self._config.cron), id=self._job_id
        )

        # B. Schedule the dynamic configuration polling (every 5 minutes)
        scheduler.add_job(
            self.check_config, "interval", minutes=5, id="config_poll_job"
        )

        scheduler.start()
        logger.info(f"Scheduler started with cron: {self._config.cron}")

    def check_config(self):
        """Polls AWS Parameter Store for changes and applies them dynamically."""
        logger.info("Polling configuration from AWS Parameter Store...")
        try:
            new_config = self._config_adapter.get_scheduler_config()

            # 1. Check for Cron changes
            if new_config.cron != self._config.cron:
                logger.info(
                    f"Cron expression changed: {self._config.cron} -> {new_config.cron}"
                )
                scheduler.reschedule_job(
                    self._job_id, trigger=CronTrigger.from_crontab(new_config.cron)
                )

            # 2. Check for Batch Size changes
            if new_config.batch_size != self._config.batch_size:
                logger.info(
                    f"Batch size changed: {self._config.batch_size} -> {new_config.batch_size}"
                )
            # 3. Cache the new configuration
            self._config = new_config
            logger.info("Configuration sync complete.")

        except Exception as e:
            logger.error(f"Failed to sync remote configuration: {e}")

    def stop(self):
        """Gracefully shuts down the scheduler."""
        scheduler.shutdown()
        logger.info("Scheduler stopped.")

    def _add_job(self, func, trigger, **kwargs):
        scheduler.add_job(func, trigger, **kwargs)

    def _execute(self):
        """Triggers the sync process if enabled."""
        if not self._config.enabled:
            logger.info("Synchronization is disabled via remote config. Skipping run.")
            return

        logger.info("Executing periodic synchronization...")
        with get_session() as session:
            contact_repo = SQLAlchemyContactRepositoryAdapter(session)
            deal_repo = SQLAlchemyDealRepositoryAdapter(session)
            chat_repo = SQLAlchemyChatRepositoryAdapter(session)

            service = OrchestratorService(
                octadesk_port=self._octadesk,
                rdstation_port=self._rdstation,
                config_port=self._config_adapter,
                contact_repo=contact_repo,
                deal_repo=deal_repo,
                chat_repo=chat_repo,
            )
            service.batch_size = self._config.batch_size

            service.start_process()


# Global reverse scheduler instance (separate from the forward scheduler)
reverse_scheduler = BackgroundScheduler()


class ReverseSyncronizerScheduler:
    _instance = None
    _job_id = "reverse_sync_job"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):  # pragma: no cover
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._config_adapter = AWSParameterStoreAdapter(
            region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
        )

        self._config = self._config_adapter.get_reverse_scheduler_config()

        self._octadesk = OctadeskAdapter(
            api_key=settings.octadesk_api_key or os.getenv("OCTADESK_API_KEY"),
            base_url=settings.octadesk_base_url or os.getenv("OCTADESK_BASE_URL"),
        )
        self._rdstation = RDStationAdapter(
            token=settings.rdstation_token or os.getenv("RDSTATION_TOKEN")
        )

        self._initialized = True

    def start(self):
        """Starts the reverse background scheduler and registers jobs."""
        reverse_scheduler.add_job(
            self._execute,
            CronTrigger.from_crontab("* * * * *"),
            id=self._job_id,
        )
        reverse_scheduler.add_job(
            self.check_config,
            "interval",
            minutes=5,
            id="reverse_config_poll_job",
        )
        reverse_scheduler.start()
        logger.info(f"Reverse scheduler started with cron: {self._config.cron}")

    def check_config(self):
        """Polls AWS Parameter Store for reverse scheduler config changes."""
        logger.info("Polling reverse scheduler configuration from AWS Parameter Store...")
        try:
            new_config = self._config_adapter.get_reverse_scheduler_config()

            if new_config.cron != self._config.cron:
                logger.info(
                    f"Reverse cron expression changed: {self._config.cron} -> {new_config.cron}"
                )
                reverse_scheduler.reschedule_job(
                    self._job_id,
                    trigger=CronTrigger.from_crontab(new_config.cron),
                )

            if new_config.batch_size != self._config.batch_size:
                logger.info(
                    f"Reverse batch size changed: {self._config.batch_size} -> {new_config.batch_size}"
                )

            self._config = new_config
            logger.info("Reverse scheduler configuration sync complete.")

        except Exception as e:
            logger.error(f"Failed to sync reverse scheduler configuration: {e}")

    def stop(self):
        """Gracefully shuts down the reverse scheduler."""
        reverse_scheduler.shutdown()
        logger.info("Reverse scheduler stopped.")

    def _execute(self):
        """Triggers the reverse sync process if enabled."""
        if not self._config.enabled:
            logger.info(
                "Reverse synchronization is disabled via remote config. Skipping run."
            )
            return

        logger.info("Executing periodic reverse synchronization...")
        from app.src.services.orchestrator_reverse import OrchestratorReverseService

        with get_session() as session:
            contact_repo = SQLAlchemyContactRepositoryAdapter(session)
            deal_repo = SQLAlchemyDealRepositoryAdapter(session)
            chat_repo = SQLAlchemyChatRepositoryAdapter(session)

            service = OrchestratorReverseService(
                octadesk_port=self._octadesk,
                rdstation_port=self._rdstation,
                contact_repo=contact_repo,
                deal_repo=deal_repo,
                chat_repo=chat_repo,
            )
            service.batch_size = self._config.batch_size
            service.start_process()
