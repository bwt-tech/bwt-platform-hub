from unittest.mock import MagicMock, patch

import pytest
from app.src.adapters.inbound.background.scheduler import SyncronizerScheduler
from app.src.domain.entities.scheduler_config import SchedulerConfig


@pytest.fixture(autouse=True)
def mock_db_session_context():
    """Globally mock the database get_session context manager to prevent real DB connections."""
    with patch(
        "app.src.adapters.inbound.background.scheduler.get_session"
    ) as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = None
        yield mock_get_session


@pytest.fixture
def mock_scheduler_global():
    with patch("app.src.adapters.inbound.background.scheduler.scheduler") as mock:
        yield mock


@pytest.fixture
def sync_scheduler_ready():
    # Patch adapters and core logic in __init__ and _execute
    with patch(
        "app.src.adapters.inbound.background.scheduler.AWSParameterStoreAdapter"
    ) as mock_param_adapter_class, patch(
        "app.src.adapters.inbound.background.scheduler.OctadeskAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.RDStationAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.OrchestratorService"
    ) as mock_orch_class, patch(
        "app.src.adapters.inbound.background.scheduler.AWSS3Adapter"
    ) as mock_s3_class, patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyContactRepositoryAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyDealRepositoryAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyChatRepositoryAdapter"
    ):

        mock_param_adapter = MagicMock()
        mock_param_adapter.get_scheduler_config.return_value = SchedulerConfig(
            enabled=True, cron="* * * * *", batch_size=50
        )
        mock_param_adapter_class.return_value = mock_param_adapter

        mock_s3_adapter = MagicMock()
        mock_s3_class.return_value = mock_s3_adapter

        # Single shared service mock — returned every time OrchestratorService() is called,
        # including the re-instantiation inside _execute().
        mock_service = MagicMock()
        mock_orch_class.return_value = mock_service

        # Reset singleton for testing
        SyncronizerScheduler._instance = None
        s = SyncronizerScheduler()
        s._config_adapter = mock_param_adapter
        s.s3_adapter = mock_s3_adapter
        # Expose shared mock instances so _execute() finds them on self
        s._octadesk = MagicMock()
        s._rdstation = MagicMock()
        # Expose the shared service mock so tests can assert on it
        s._service = mock_service
        yield s
        SyncronizerScheduler._instance = None


def test_scheduler_check_config_cron_change(
    sync_scheduler_ready, mock_scheduler_global
):
    # Prepare
    sync_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="original", batch_size=50
    )
    sync_scheduler_ready._config_adapter.get_scheduler_config.return_value = (
        SchedulerConfig(enabled=True, cron="0 0 * * *", batch_size=50)
    )

    # Execute
    sync_scheduler_ready.check_config()

    # Assert
    mock_scheduler_global.reschedule_job.assert_called_once()
    args, kwargs = mock_scheduler_global.reschedule_job.call_args
    assert args[0] == "sync_job"
    assert sync_scheduler_ready._config.cron == "0 0 * * *"


def test_scheduler_check_config_batch_size_change(
    sync_scheduler_ready, mock_scheduler_global
):
    # Prepare
    sync_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="same", batch_size=50
    )
    sync_scheduler_ready._config_adapter.get_scheduler_config.return_value = (
        SchedulerConfig(enabled=True, cron="same", batch_size=100)
    )

    # Execute
    sync_scheduler_ready.check_config()

    # Assert
    assert sync_scheduler_ready._config.batch_size == 100


def test_scheduler_execute_respects_enabled_flag(sync_scheduler_ready):
    # Prepare
    sync_scheduler_ready._config = SchedulerConfig(
        enabled=False, cron="* * * * *", batch_size=50
    )

    # Execute
    sync_scheduler_ready._execute()

    # Assert
    sync_scheduler_ready._service.start_process.assert_not_called()

    sync_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="* * * * *", batch_size=50
    )
    sync_scheduler_ready._execute()
    sync_scheduler_ready._service.start_process.assert_called_once()


def test_scheduler_execute_skips_s3_upload_on_empty_result(sync_scheduler_ready):
    """When start_process returns an empty list, _execute does NOT upload to S3."""
    sync_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="* * * * *", batch_size=50
    )
    sync_scheduler_ready._service.start_process.return_value = []

    sync_scheduler_ready._execute()

    sync_scheduler_ready.s3_adapter.upload_content.assert_not_called()


def test_scheduler_check_config_exception(sync_scheduler_ready):
    # Prepare
    sync_scheduler_ready._config_adapter.get_scheduler_config.side_effect = Exception(
        "Boom"
    )

    # Execute
    sync_scheduler_ready.check_config()
    # Should not raise exception


def test_scheduler_stop(sync_scheduler_ready, mock_scheduler_global):
    # Execute
    sync_scheduler_ready.stop()

    # Assert
    mock_scheduler_global.shutdown.assert_called_once()


def test_scheduler_start(sync_scheduler_ready, mock_scheduler_global):
    """Covers the start() method: _execute + _add_job + scheduler.start."""
    from app.tests.conftest import ORIGINAL_START

    sync_scheduler_ready._config = SchedulerConfig(
        enabled=False, cron="* * * * *", batch_size=50
    )
    sync_scheduler_ready._service.start_process.return_value = []

    ORIGINAL_START(sync_scheduler_ready)

    # _execute was called (enabled=False so no start_process)
    sync_scheduler_ready._service.start_process.assert_not_called()
    # scheduler.add_job was called for config_poll and the main job (via _add_job)
    mock_scheduler_global.start.assert_called_once()


def test_scheduler_add_job(sync_scheduler_ready, mock_scheduler_global):
    """Covers the _add_job method directly."""
    trigger = MagicMock()
    sync_scheduler_ready._add_job(lambda: None, trigger, id="test_job")
    mock_scheduler_global.add_job.assert_called()
