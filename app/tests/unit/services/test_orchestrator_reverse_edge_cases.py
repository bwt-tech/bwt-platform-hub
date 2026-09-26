import pytest
from unittest.mock import MagicMock

from app.src.domain.entities.agent_seller_configuration import AgentSellerConfiguration
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.services.orchestrator_reverse import OrchestratorReverseService


def test_orchestrator_skips_agent_without_id(mock_octadesk, mock_rdstation):
    service = OrchestratorReverseService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
    )
    config_loader = MagicMock()
    config_loader.load.return_value = [
        AgentSellerConfiguration(agent_id=None, seller="Roberta", supervisor="João")
    ]
    service._config_loader = config_loader
    mock_rdstation.get_deal_pipelines.return_value = []

    service.start_process()

    mock_octadesk.get_chats_in_progress.assert_not_called()


def test_orchestrator_skips_chat_when_scope_not_resolved(
    mock_octadesk, mock_rdstation, mock_bwt_factory
):
    service = OrchestratorReverseService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        bwt_factory=mock_bwt_factory,
    )
    config_loader = MagicMock()
    config_loader.load.return_value = [
        AgentSellerConfiguration(
            agent_id="agent-1",
            seller="Maria",
            pipeline_name="Pipeline Inexistente",
            scope="SBM",
            supervisor="José"
        )
    ]
    service._config_loader = config_loader
    mock_rdstation.get_deal_pipelines.return_value = [
        Pipeline(id="p-1", name="Outro Pipeline", deal_stages=[])
    ]
    mock_octadesk.get_chats_in_progress.side_effect = [[{"id": "chat-1"}],[]]
    mock_wf = MagicMock()
    service._reverse_sync_workflow = mock_wf

    service.start_process()

    mock_wf.execute.assert_not_called()


@pytest.fixture
def mock_octadesk():
    from app.src.ports.octadesk_port import OctadeskPort

    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    from app.src.ports.rdstation_port import RDStationPort

    return MagicMock(spec=RDStationPort)


@pytest.fixture
def mock_bwt_factory():
    from app.src.ports.bwt_port import BWTPort

    factory = MagicMock()
    factory.create.return_value = MagicMock(spec=BWTPort)
    return factory
