from unittest.mock import MagicMock

from app.src.adapters.database.models import ChatModel, ContactModel, DealModel
from app.src.adapters.database.repositories.chat_repository_adapter import (
    SQLAlchemyChatRepositoryAdapter,
)
from app.src.adapters.database.repositories.contact_repository_adapter import (
    SQLAlchemyContactRepositoryAdapter,
)
from app.src.adapters.database.repositories.deal_repository_adapter import (
    SQLAlchemyDealRepositoryAdapter,
)
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.orchestrator import OrchestratorService


def test_sync_persistence_happy(db_session, monkeypatch):
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_rdstation = MagicMock(spec=RDStationPort)

    # Bypass recurring-no-answer checker so contact processing runs
    monkeypatch.setattr(
        "app.src.services.workflows.recurring_no_answer_checker.RecurringNoAnswerChecker.is_recurring",
        lambda self, name, phone, stage: False,
    )

    contact_repo = SQLAlchemyContactRepositoryAdapter(db_session)
    deal_repo = SQLAlchemyDealRepositoryAdapter(db_session)
    chat_repo = SQLAlchemyChatRepositoryAdapter(db_session)

    templates = {
        "templates": {
            "Mendoza Pipeline": {
                "phone": "code",
                "template": "id",
                "write_enabled": False,
                "agent": {
                    "id": "agent-123",
                    "name": "Persist Agent",
                    "email": "agent@persist.com",
                    "key": "KEY_TEST",
                },
            }
        }
    }

    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: templates)

    service = OrchestratorService(
        octadesk_port=mock_octadesk,
        rdstation_port=mock_rdstation,
        contact_repo=contact_repo,
        deal_repo=deal_repo,
        chat_repo=chat_repo,
    )

    mock_rdstation.get_deal_pipelines.return_value = [
        Pipeline(
            id="pipe-123",
            name="Mendoza Pipeline",
            deal_stages=[
                DealStage(id="stage-sc", nickname="SC"),
                DealStage(id="stage-nr", nickname="NR"),
                DealStage(id="stage-cf", nickname="CF"),
            ],
        )
    ]

    deal_payload = {
        "id": "deal-ext-789",
        "name": "Jane Doe",
        "contacts": [
            {
                "phones": [{"phone": "5511977777777"}],
                "emails": [{"email": "jane@example.com"}],
            }
        ],
        "deal_source": {"name": "SEO"},
        "campaign": {"name": "Google Ads"},
    }
    mock_rdstation.get_deals.return_value = {"deals": [deal_payload]}

    mock_octadesk.get_contacts_by_phone.return_value = []
    mock_octadesk.get_chats_by_phone.return_value = []
    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "room-ext-888"}}
    }

    # Execute synchronization
    service.start_process()

    # Query DB to check persistence
    contacts = db_session.query(ContactModel).all()
    assert len(contacts) == 1
    assert contacts[0].name == "Jane Doe"
    assert contacts[0].info.email == "jane@example.com"
    assert contacts[0].info.phone == "11977777777"

    deals = db_session.query(DealModel).all()
    assert len(deals) == 1
    assert deals[0].rdstation_id == "deal-ext-789"
    assert (
        deals[0].deal_status == "CF"
    )  # contacted_nickname from CONTACTED constant

    chats = db_session.query(ChatModel).all()
    assert len(chats) == 1
    assert chats[0].octadesk_id == "room-ext-888"
