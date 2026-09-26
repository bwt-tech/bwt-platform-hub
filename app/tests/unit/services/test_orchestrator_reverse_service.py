from unittest.mock import MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.ports.bwt_port import BWTPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.agent_seller_config_loader import AgentSellerConfigLoader
import app.src.services.orchestrator_reverse as orchestrator_reverse_module
from app.src.services.orchestrator_reverse import OrchestratorReverseService


@pytest.fixture(autouse=True)
def clear_processed_set():
    """Limpa o set PROCESSED global antes de cada teste para garantir isolamento."""
    orchestrator_reverse_module.PROCESSED.clear()
    yield
    orchestrator_reverse_module.PROCESSED.clear()

PIPELINES_FIXTURE = [
    Pipeline(
        id="p-1",
        name="Brasileiros em Mendoza",
        deal_stages=[
            DealStage(id="stage-epv-1", nickname="EPV"),
        ],
    )
]

AGENTS2SELLER_FIXTURE = [
    {
        "agent": {
            "id": "agent-id-1",
            "name": "Andrele - Comercial",
        },
        "seller": "Andrele",
        "pipeline": "Brasileiros em Mendoza",
        "scope": "SBM",
    }
]


@pytest.fixture
def mock_octadesk():
    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    return MagicMock(spec=RDStationPort)


@pytest.fixture
def mock_bwt_port():
    return MagicMock(spec=BWTPort)


@pytest.fixture
def mock_bwt_factory(mock_bwt_port):
    factory = MagicMock()
    factory.create.return_value = mock_bwt_port
    return factory


def _build_reverse_service(
    mock_octadesk,
    mock_rdstation,
    monkeypatch,
    agents_fixture=None,
    mock_bwt_factory=None,
):
    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr(
        "yaml.safe_load",
        lambda _: agents_fixture if agents_fixture is not None else AGENTS2SELLER_FIXTURE,
    )
    return OrchestratorReverseService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        bwt_factory=mock_bwt_factory or MagicMock(),
    )


def test_orchestrator_reverse_start_process_success(
    mock_octadesk, mock_rdstation, mock_bwt_factory, monkeypatch
):
    service = _build_reverse_service(
        mock_octadesk, mock_rdstation, monkeypatch, mock_bwt_factory=mock_bwt_factory
    )
    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = [[
        {
            "id": "chat-1",
            "contact": {
                "name": "Cliente Teste",
                "email": "cliente@teste.com",
                "phoneContacts": [{"number": "11911112222"}],
            },
        }
    ],[]]
    mock_rdstation.get_contacts.return_value = {"contacts": []}
    mock_rdstation.post_deal.return_value = {
        "id": "deal-new-1",
        "deal_source": {"name": "Octadesk"},
        "campaign": {"name": ""},
    }

    service.start_process()
    mock_octadesk.get_chats_in_progress.assert_called()
    mock_bwt_factory.create.assert_called_once_with("SBM")


def test_orchestrator_reverse_get_pipelines_failure(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_reverse_service(mock_octadesk, mock_rdstation, monkeypatch)
    mock_rdstation.get_deal_pipelines.side_effect = IntegrationError("API offline")

    service.start_process()
    mock_octadesk.get_chats_in_progress.assert_not_called()


def test_orchestrator_reverse_yaml_load_failure(monkeypatch):
    monkeypatch.setattr("builtins.open", MagicMock(side_effect=OSError("File missing")))
    loader = AgentSellerConfigLoader()
    agents = loader.load()
    assert agents == []


def test_orchestrator_reverse_missing_with_seller_stage(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_reverse_service(mock_octadesk, mock_rdstation, monkeypatch)
    pipeline_no_epv = [
        Pipeline(id="p-1", name="Brasileiros em Mendoza", deal_stages=[])
    ]
    mock_rdstation.get_deal_pipelines.return_value = pipeline_no_epv
    mock_octadesk.get_chats_in_progress.side_effect = [[
        {
            "id": "chat-1",
            "contact": {
                "name": "Cliente Teste",
                "email": "cliente@teste.com",
                "phoneContacts": [{"number": "11911112222"}],
            },
        }
    ],[]]
    mock_wf = MagicMock()
    service._reverse_sync_workflow = mock_wf

    service.start_process()
    mock_wf.execute.assert_not_called()


def test_orchestrator_reverse_get_chats_in_progress_integration_error(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_reverse_service(mock_octadesk, mock_rdstation, monkeypatch)
    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = IntegrationError("Octadesk timeout")

    service.start_process()


def test_orchestrator_reverse_workflow_error_handlers(
    mock_octadesk, mock_rdstation, mock_bwt_factory, monkeypatch
):
    service = _build_reverse_service(
        mock_octadesk, mock_rdstation, monkeypatch, mock_bwt_factory=mock_bwt_factory
    )
    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = [[
        {
            "id": "chat-err-1",
            "contact": {
                "name": "Err Contact 1",
                "email": "err1@test.com",
                "phoneContacts": [{"number": "11911110001"}],
            },
        },
        {
            "id": "chat-err-2",
            "contact": {
                "name": "Err Contact 2",
                "email": "err2@test.com",
                "phoneContacts": [{"number": "11911110002"}],
            },
        },
        {
            "id": "chat-err-3",
            "contact": {
                "name": "Err Contact 3",
                "email": "err3@test.com",
                "phoneContacts": [{"number": "11911110003"}],
            },
        },
    ],[]]

    mock_wf = MagicMock()
    mock_wf.execute.side_effect = [
        IntegrationError("API Err"),
        SQLAlchemyError("DB Err"),
        ValueError("Unexpected Err"),
    ]
    service._reverse_sync_workflow = mock_wf

    service.start_process()
    assert mock_wf.execute.call_count == 3


# --- batch_size Tests ---

CHATS_BATCH_FIXTURE = [
    {"id": f"chat-{i}", "contact": {"name": f"C{i}", "email": f"c{i}@t.com", "phoneContacts": [{"number": f"1191111000{i}"}]}}
    for i in range(5)
]


def test_orchestrator_reverse_batch_size_zero_processes_all_chats(
    mock_octadesk, mock_rdstation, mock_bwt_factory, monkeypatch
):
    """batch_size=0 (default) must not limit the number of chats processed."""
    service = _build_reverse_service(
        mock_octadesk, mock_rdstation, monkeypatch, mock_bwt_factory=mock_bwt_factory
    )
    assert service.batch_size == 0

    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = [CHATS_BATCH_FIXTURE,[]]

    mock_wf = MagicMock()
    service._reverse_sync_workflow = mock_wf

    service.start_process()

    # All 5 chats should be processed (no truncation)
    assert mock_wf.execute.call_count == 5


def test_orchestrator_reverse_batch_size_n_limits_chats(
    mock_octadesk, mock_rdstation, mock_bwt_factory, monkeypatch
):
    """batch_size=N must truncate chats to at most N per cycle."""
    service = _build_reverse_service(
        mock_octadesk, mock_rdstation, monkeypatch, mock_bwt_factory=mock_bwt_factory
    )
    service.batch_size = 2

    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = [CHATS_BATCH_FIXTURE,[]]

    mock_wf = MagicMock()
    service._reverse_sync_workflow = mock_wf

    service.start_process()

    # Only 2 out of 5 chats should be processed
    assert mock_wf.execute.call_count == 2


def test_orchestrator_reverse_batch_size_log_emitted(
    mock_octadesk, mock_rdstation, mock_bwt_factory, monkeypatch, caplog
):
    """A log message must be emitted when the batch_size limit is applied."""
    import logging

    service = _build_reverse_service(
        mock_octadesk, mock_rdstation, monkeypatch, mock_bwt_factory=mock_bwt_factory
    )
    service.batch_size = 3

    mock_rdstation.get_deal_pipelines.return_value = PIPELINES_FIXTURE
    mock_octadesk.get_chats_in_progress.side_effect = [CHATS_BATCH_FIXTURE,[]]

    mock_wf = MagicMock()
    service._reverse_sync_workflow = mock_wf

    import loguru

    log_messages = []
    handler_id = loguru.logger.add(lambda msg: log_messages.append(msg), level="INFO")
    try:
        service.start_process()
    finally:
        loguru.logger.remove(handler_id)

    assert any("3" in m and ("Limiting" in m or "limit" in m.lower()) for m in log_messages)
