from unittest.mock import MagicMock

import pytest
from app.src.domain.entities.agent import Agent
from app.src.domain.entities.deal import Deal
from app.src.domain.entities.template_configuration import TemplateConfiguration
from app.src.domain.process_summary_tracker import ProcessSummaryTracker
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.workflows.new_contact_workflow import NewContactWorkflow


@pytest.fixture
def mock_octadesk():
    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    return MagicMock(spec=RDStationPort)


@pytest.fixture
def tracker():
    return ProcessSummaryTracker(pipeline_name="BWT")


@pytest.fixture
def deal():
    return Deal(
        deal_id="123",
        name="Test Deal",
        phone="11999999999",
        email="test@ex.com",
        deal_source_name="Src",
        deal_campaign_name="Cmp",
    )


@pytest.fixture
def contact(deal):
    return deal.to_contact()


@pytest.fixture
def configuration():
    return TemplateConfiguration(
        phone="code",
        template="id",
        write_enabled=False,
        agent=Agent(
            id="agent-1", name="Test Agent", email="agent@test.com", key="KEY_TEST"
        ),
    )


def test_new_contact_workflow_success(
    mock_octadesk, mock_rdstation, tracker, deal, contact, configuration
):
    workflow = NewContactWorkflow(mock_octadesk, mock_rdstation)

    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "chat_123"}}
    }
    contacted_stage_id = "stage_123"
    initial_contact_dict = contact.to_dict()

    workflow.execute(deal, contact, configuration, contacted_stage_id, "CF", tracker)

    mock_octadesk.post_contacts.assert_called_once_with(
        contact.email, contact.name, contact.phone
    )
    mock_octadesk.start_chat.assert_called_once_with(
        initial_contact_dict, configuration.to_dict()
    )
    mock_octadesk.notify_agent.assert_called_once_with(
        "chat_123",
        "Novo contato criado pelo funil de vendas da RD. Origem: Src. Campanha: Cmp",
        configuration.agent,
    )
    mock_rdstation.put_deal.assert_called_once_with(deal.deal_id, contacted_stage_id)

    assert tracker.to_dict()["contacts_created"] == 1
    assert tracker.to_dict()["chats_started"] == 1
