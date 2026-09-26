from unittest.mock import MagicMock

import pytest
from app.src.domain.entities.agent import Agent
from app.src.domain.entities.deal import Deal
from app.src.domain.entities.template_configuration import TemplateConfiguration
from app.src.domain.process_summary_tracker import ProcessSummaryTracker
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.octadesk_lookup import OctadeskLookup
from app.src.services.workflows.existing_contact_workflow import ExistingContactWorkflow


@pytest.fixture
def mock_octadesk():
    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    return MagicMock(spec=RDStationPort)


@pytest.fixture
def mock_lookup():
    return MagicMock(spec=OctadeskLookup)


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


def test_existing_contact_workflow_no_chat(
    mock_octadesk, mock_rdstation, mock_lookup, tracker, deal, contact, configuration
):
    workflow = ExistingContactWorkflow(mock_octadesk, mock_rdstation, mock_lookup)

    mock_lookup.has_chat.return_value = False
    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "chat_123"}}
    }
    contacted_stage_id = "stage_123"

    workflow.execute(deal, contact, configuration, contacted_stage_id, "CF", tracker)

    assert tracker.to_dict()["contacts_existing"] == 1
    assert tracker.to_dict()["chats_started"] == 1
    mock_rdstation.put_deal.assert_called_once_with(deal.deal_id, contacted_stage_id)
    mock_octadesk.notify_agent.assert_called_once_with(
        "chat_123",
        "Cliente se inscreveu por landing page (RD). Não havia conversa prévia. Origem: Src. Campanha: Cmp",
        configuration.agent,
    )


def test_existing_contact_workflow_with_chat(
    mock_octadesk, mock_rdstation, mock_lookup, tracker, deal, contact, configuration
):
    workflow = ExistingContactWorkflow(mock_octadesk, mock_rdstation, mock_lookup)

    mock_lookup.has_chat.return_value = True
    mock_lookup.get_existing_chat_id.return_value = "chat_123"
    contacted_stage_id = "stage_123"

    workflow.execute(deal, contact, configuration, contacted_stage_id, "CF", tracker)

    assert tracker.to_dict()["contacts_existing"] == 1
    assert tracker.to_dict()["chats_existing"] == 1
    mock_octadesk.notify_agent.assert_called_once_with(
        "chat_123",
        "Cliente se inscreveu por landing page (RD). Origem: Src. Campanha: Cmp",
        configuration.agent,
    )
    mock_rdstation.put_deal.assert_called_once_with(deal.deal_id, contacted_stage_id)


def test_existing_contact_workflow_no_chat_with_repos(
    mock_octadesk, mock_rdstation, mock_lookup, tracker, deal, contact, configuration
):
    """Covers lines 53, 72, 83 — repo saves on the no-chat path."""
    from unittest.mock import MagicMock

    from app.src.domain.entities.contact import Contact
    from app.src.domain.repositories.chat_repository import ChatRepositoryPort
    from app.src.domain.repositories.contact_repository import ContactRepositoryPort
    from app.src.domain.repositories.deal_repository import DealRepositoryPort

    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)
    mock_deal_repo = MagicMock(spec=DealRepositoryPort)
    mock_chat_repo = MagicMock(spec=ChatRepositoryPort)

    saved_contact = Contact(
        id="c-uuid-1",
        name="Test Deal",
        phone="11999999999",
        email="test@ex.com",
        deal_id="123",
        octadesk_id="octa-1",
    )
    mock_contact_repo.save.return_value = saved_contact
    mock_lookup.has_contact.return_value = None
    mock_lookup.has_chat.return_value = False
    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "chat_new"}}
    }

    workflow = ExistingContactWorkflow(
        mock_octadesk,
        mock_rdstation,
        mock_lookup,
        contact_repo=mock_contact_repo,
        deal_repo=mock_deal_repo,
        chat_repo=mock_chat_repo,
    )
    workflow.execute(deal, contact, configuration, "stage_cf", "CF", tracker)

    mock_contact_repo.save.assert_called_once()
    mock_deal_repo.save.assert_called_once()
    mock_chat_repo.save.assert_called_once()


def test_existing_contact_workflow_with_chat_with_repos(
    mock_octadesk, mock_rdstation, mock_lookup, tracker, deal, contact, configuration
):
    """Covers lines 104, 115 — repo saves on the existing-chat path."""
    from unittest.mock import MagicMock

    from app.src.domain.entities.contact import Contact
    from app.src.domain.repositories.chat_repository import ChatRepositoryPort
    from app.src.domain.repositories.contact_repository import ContactRepositoryPort
    from app.src.domain.repositories.deal_repository import DealRepositoryPort

    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)
    mock_deal_repo = MagicMock(spec=DealRepositoryPort)
    mock_chat_repo = MagicMock(spec=ChatRepositoryPort)

    saved_contact = Contact(
        id="c-uuid-2",
        name="Test Deal",
        phone="11999999999",
        email="test@ex.com",
        deal_id="123",
        octadesk_id="octa-2",
    )
    mock_contact_repo.save.return_value = saved_contact
    mock_lookup.has_contact.return_value = "octa-2"
    mock_lookup.has_chat.return_value = True
    mock_lookup.get_existing_chat_id.return_value = "existing-chat-id"

    workflow = ExistingContactWorkflow(
        mock_octadesk,
        mock_rdstation,
        mock_lookup,
        contact_repo=mock_contact_repo,
        deal_repo=mock_deal_repo,
        chat_repo=mock_chat_repo,
    )
    workflow.execute(deal, contact, configuration, "stage_cf", "CF", tracker)

    mock_contact_repo.save.assert_called_once()
    mock_deal_repo.save.assert_called_once()
    mock_chat_repo.save.assert_called_once()
