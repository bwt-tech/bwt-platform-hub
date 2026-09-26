from unittest.mock import MagicMock, patch

import pytest

from app.src.adapters.inbound.background.scheduler import ReverseSyncronizerScheduler
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
def mock_reverse_scheduler_global():
    with patch("app.src.adapters.inbound.background.scheduler.reverse_scheduler") as mock:
        yield mock


@pytest.fixture
def reverse_scheduler_ready():
    with patch(
        "app.src.adapters.inbound.background.scheduler.AWSParameterStoreAdapter"
    ) as mock_param_adapter_class, patch(
        "app.src.adapters.inbound.background.scheduler.OctadeskAdapter"
    ) as mock_octadesk_class, patch(
        "app.src.adapters.inbound.background.scheduler.RDStationAdapter"
    ) as mock_rdstation_class, patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyContactRepositoryAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyDealRepositoryAdapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.SQLAlchemyChatRepositoryAdapter"
    ), patch(
        "app.src.services.orchestrator_reverse.OrchestratorReverseService"
    ) as mock_reverse_service_class:

        mock_param_adapter = MagicMock()
        mock_param_adapter.get_reverse_scheduler_config.return_value = SchedulerConfig(
            enabled=True, cron="* * * * *", batch_size=50
        )
        mock_param_adapter_class.return_value = mock_param_adapter

        # Single shared service mock — returned every time OrchestratorReverseService()
        # is called, including the re-instantiation inside _execute().
        mock_service = MagicMock()
        mock_reverse_service_class.return_value = mock_service

        # Reset singleton for each test
        ReverseSyncronizerScheduler._instance = None
        s = ReverseSyncronizerScheduler()
        s._config_adapter = mock_param_adapter
        s._octadesk = mock_octadesk_class.return_value
        s._rdstation = mock_rdstation_class.return_value
        # Expose the shared service mock so tests can assert on it
        s._service = mock_service
        yield s
        ReverseSyncronizerScheduler._instance = None


def test_reverse_scheduler_execute_disabled(reverse_scheduler_ready):
    """_execute with enabled=False must not call start_process and must log."""
    reverse_scheduler_ready._config = SchedulerConfig(
        enabled=False, cron="* * * * *", batch_size=50
    )

    log_messages = []
    import loguru
    handler_id = loguru.logger.add(lambda msg: log_messages.append(msg), level="INFO")
    try:
        reverse_scheduler_ready._execute()
    finally:
        loguru.logger.remove(handler_id)

    reverse_scheduler_ready._service.start_process.assert_not_called()
    assert any("disabled" in m.lower() or "skipping" in m.lower() for m in log_messages)


def test_reverse_scheduler_execute_enabled(reverse_scheduler_ready):
    """_execute with enabled=True must call start_process."""
    reverse_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="* * * * *", batch_size=50
    )

    reverse_scheduler_ready._execute()

    reverse_scheduler_ready._service.start_process.assert_called_once()


def test_reverse_scheduler_check_config_cron_change(
    reverse_scheduler_ready, mock_reverse_scheduler_global
):
    """check_config must reschedule the job when cron expression changes."""
    reverse_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="original_cron", batch_size=50
    )
    reverse_scheduler_ready._config_adapter.get_reverse_scheduler_config.return_value = (
        SchedulerConfig(enabled=True, cron="0 0 * * *", batch_size=50)
    )

    reverse_scheduler_ready.check_config()

    mock_reverse_scheduler_global.reschedule_job.assert_called_once()
    args, kwargs = mock_reverse_scheduler_global.reschedule_job.call_args
    assert args[0] == "reverse_sync_job"
    assert reverse_scheduler_ready._config.cron == "0 0 * * *"


def test_reverse_scheduler_check_config_batch_size_change(
    reverse_scheduler_ready, mock_reverse_scheduler_global
):
    """check_config must update service.batch_size when batch_size changes."""
    reverse_scheduler_ready._config = SchedulerConfig(
        enabled=True, cron="same_cron", batch_size=50
    )
    reverse_scheduler_ready._config_adapter.get_reverse_scheduler_config.return_value = (
        SchedulerConfig(enabled=True, cron="same_cron", batch_size=100)
    )

    reverse_scheduler_ready.check_config()

    assert reverse_scheduler_ready._config.batch_size == 100


def test_reverse_scheduler_check_config_exception_does_not_propagate(reverse_scheduler_ready):
    """check_config must not propagate exceptions — scheduler must keep running."""
    reverse_scheduler_ready._config_adapter.get_reverse_scheduler_config.side_effect = (
        Exception("SSM unavailable")
    )

    # Must not raise
    reverse_scheduler_ready.check_config()


def test_reverse_scheduler_start(reverse_scheduler_ready, mock_reverse_scheduler_global):
    """start() must register the main job and the polling job, then start the scheduler."""
    from app.tests.conftest import ORIGINAL_REVERSE_START

    reverse_scheduler_ready._config = SchedulerConfig(
        enabled=False, cron="* * * * *", batch_size=50
    )

    ORIGINAL_REVERSE_START(reverse_scheduler_ready)

    mock_reverse_scheduler_global.start.assert_called_once()
    assert mock_reverse_scheduler_global.add_job.call_count >= 2


def test_reverse_scheduler_stop(reverse_scheduler_ready, mock_reverse_scheduler_global):
    """stop() must call scheduler.shutdown()."""
    reverse_scheduler_ready.stop()

    mock_reverse_scheduler_global.shutdown.assert_called_once()
