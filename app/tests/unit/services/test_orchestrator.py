from unittest.mock import MagicMock

from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.orchestrator import OrchestratorService

PIPELINE_FIXTURE = [
    Pipeline(
        id="pipe-1",
        name="Brasileiros em Mendoza",
        deal_stages=[
            DealStage(id="s1", nickname="SC"),
            DealStage(id="s2", nickname="NR"),
            DealStage(id="s3", nickname="CF"),
        ],
    )
]

TEMPLATES_FIXTURE = {
    "templates": {
        "Brasileiros em Mendoza": {
            "phone": "code",
            "template": "id",
            "write_enabled": False,
            "agent": {
                "id": "agent-1",
                "name": "Test Agent",
                "email": "agent@test.com",
                "key": "KEY_MENDOZA",
            },
        }
    }
}


def _make_deal_payload(deal_id, name="User", phone="999", email="u@e.com"):
    return {
        "id": deal_id,
        "name": name,
        "contacts": [{"phones": [{"phone": phone}], "emails": [{"email": email}]}],
        "deal_source": {"name": "Test Source"},
        "campaign": {"name": "Test Campaign"},
    }


def test_orchestrator_sets_octadesk_api_key_per_pipeline(monkeypatch):
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_rdstation = MagicMock(spec=RDStationPort)

    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: TEMPLATES_FIXTURE)

    service = OrchestratorService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
    )

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_FIXTURE
    mock_rdstation.get_deals.return_value = {"deals": []}

    service.start_process()

    mock_octadesk.set_api_key.assert_called_once_with("KEY_MENDOZA")


def test_orchestrator_resolves_ssm_key_path(monkeypatch):
    from app.src.ports.config_port import ConfigPort

    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_rdstation = MagicMock(spec=RDStationPort)
    mock_config = MagicMock(spec=ConfigPort)
    mock_config.get_parameter.return_value = "SECRET_KEY_FROM_SSM"

    ssm_templates = {
        "templates": {
            "Brasileiros em Mendoza": {
                "phone": "code",
                "template": "id",
                "write_enabled": False,
                "agent": {
                    "id": "agent-1",
                    "name": "Test Agent",
                    "email": "agent@test.com",
                    "key": "/bwt/octadesk/keys/mendoza",
                },
            }
        }
    }

    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: ssm_templates)

    service = OrchestratorService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        config_port=mock_config,
    )

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_FIXTURE
    mock_rdstation.get_deals.return_value = {"deals": []}

    service.start_process()

    mock_config.get_parameter.assert_called_once_with("/bwt/octadesk/keys/mendoza")
    mock_octadesk.set_api_key.assert_called_once_with("SECRET_KEY_FROM_SSM")



def test_orchestrator_saves_entities_to_repositories(monkeypatch):
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_rdstation = MagicMock(spec=RDStationPort)
    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)
    mock_deal_repo = MagicMock(spec=DealRepositoryPort)
    mock_chat_repo = MagicMock(spec=ChatRepositoryPort)

    # Bypass recurring-no-answer so the new-contact workflow is executed
    monkeypatch.setattr(
        "app.src.services.workflows.recurring_no_answer_checker.RecurringNoAnswerChecker.is_recurring",
        lambda self, name, phone, stage: False,
    )

    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: TEMPLATES_FIXTURE)

    service = OrchestratorService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        contact_repo=mock_contact_repo,
        deal_repo=mock_deal_repo,
        chat_repo=mock_chat_repo,
    )

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_FIXTURE
    mock_rdstation.get_deals.return_value = {
        "deals": [
            _make_deal_payload("deal_new", "Alice", "11999999999", "alice@example.com")
        ]
    }

    # No existing contact in DB or API
    mock_contact_repo.find_by_phone.return_value = None
    mock_octadesk.get_contacts_by_phone.return_value = []
    mock_octadesk.get_chats_by_phone.return_value = []
    mock_octadesk.post_contacts.return_value = {"id": "octa-alice"}

    # contact_repo.save returns an updated Contact with an id
    saved_contact = Contact(
        id="c-uuid-alice",
        name="Alice",
        phone="11999999999",
        email="alice@example.com",
        deal_id="deal_new",
        octadesk_id="octa-alice",
    )
    mock_contact_repo.save.return_value = saved_contact

    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "room-123"}}
    }

    # Execute
    service.start_process()

    # Verify that contact, deal, and chat were saved to repository adapters
    assert mock_contact_repo.save.call_count == 1
    assert mock_deal_repo.save.call_count == 1
    assert mock_chat_repo.save.call_count == 1


def test_orchestrator_handles_recurring_no_answer(monkeypatch):
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_rdstation = MagicMock(spec=RDStationPort)
    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)
    mock_deal_repo = MagicMock(spec=DealRepositoryPort)
    mock_chat_repo = MagicMock(spec=ChatRepositoryPort)

    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: TEMPLATES_FIXTURE)

    service = OrchestratorService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        contact_repo=mock_contact_repo,
        deal_repo=mock_deal_repo,
        chat_repo=mock_chat_repo,
    )
    service._recurring_checker = MagicMock()
    service._recurring_checker.is_recurring.return_value = True

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_FIXTURE
    mock_rdstation.get_deals.return_value = {
        "deals": [
            _make_deal_payload("deal_rec", "Bob", "11988888888", "bob@example.com")
        ]
    }

    service.start_process()

    # Workflow skipped for recurring lead
    assert mock_contact_repo.save.call_count == 0
    assert service._recurring_checker.is_recurring.called



