"""
Functional test: verifies that the SyncronizerScheduler._execute() method
correctly wires repository adapters to the OrchestratorService and persists
synchronized contact, deal, and chat records to the local database.
"""
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from app.src.adapters.database.models import ChatModel, ContactModel, DealModel
from app.src.adapters.inbound.background.scheduler import SyncronizerScheduler
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.entities.scheduler_config import SchedulerConfig


def test_scheduler_execute_persists_to_database(db_session, monkeypatch):
    """
    Scenario: Successful synchronization persists records.
    WHEN the background scheduler runs _execute() with enabled=True
    THEN contact, deal, and chat records are persisted in the local database.
    """

    # --- Mock external dependencies ---
    mock_octadesk = MagicMock()
    mock_rdstation = MagicMock()

    # Bypass recurring-no-answer checker so new-contact workflow runs
    monkeypatch.setattr(
        "app.src.services.workflows.recurring_no_answer_checker.RecurringNoAnswerChecker.is_recurring",
        lambda self, name, phone, stage: False,
    )

    # --- Template config ---
    templates = {
        "templates": {
            "Test Pipeline": {
                "phone": "code",
                "template": "id",
                "write_enabled": False,
                "agent": {
                    "id": "agent-sched-001",
                    "name": "Scheduler Agent",
                    "email": "agent@scheduler.com",
                    "key": "KEY_TEST",
                },
            }
        }
    }
    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr("yaml.safe_load", lambda _: templates)

    # --- RD Station returns a single pipeline with one deal ---
    mock_rdstation.get_deal_pipelines.return_value = [
        Pipeline(
            id="pipe-sched-001",
            name="Test Pipeline",
            deal_stages=[
                DealStage(id="stage-sc", nickname="SC"),
                DealStage(id="stage-nr", nickname="NR"),
                DealStage(id="stage-cf", nickname="CF"),
            ],
        )
    ]
    mock_rdstation.get_deals.return_value = {
        "deals": [
            {
                "id": "deal-sched-999",
                "name": "Scheduler Contact",
                "contacts": [
                    {
                        "phones": [{"phone": "5512988881234"}],
                        "emails": [{"email": "scheduler@test.com"}],
                    }
                ],
                "deal_source": {"name": "Website"},
                "campaign": {"name": "Campaign A"},
            }
        ]
    }

    # --- Octadesk: no existing contacts or chats, chat creation succeeds ---
    mock_octadesk.get_contacts_by_phone.return_value = []
    mock_octadesk.get_chats_by_phone.return_value = []
    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "room-sched-001"}}
    }

    # --- Wire get_session to yield our in-memory test db_session ---
    @contextmanager
    def mock_get_session():
        yield db_session

    # --- Build scheduler with all external adapters mocked ---
    with patch(
        "app.src.adapters.inbound.background.scheduler.AWSParameterStoreAdapter"
    ) as mock_param_class, patch(
        "app.src.adapters.inbound.background.scheduler.OctadeskAdapter",
        return_value=mock_octadesk,
    ), patch(
        "app.src.adapters.inbound.background.scheduler.RDStationAdapter",
        return_value=mock_rdstation,
    ), patch(
        "app.src.adapters.inbound.background.scheduler.AWSS3Adapter"
    ), patch(
        "app.src.adapters.inbound.background.scheduler.get_session",
        new=mock_get_session,
    ):
        mock_param_instance = MagicMock()
        mock_param_instance.get_scheduler_config.return_value = SchedulerConfig(
            enabled=True, cron="* * * * *", batch_size=50
        )
        mock_param_class.return_value = mock_param_instance

        SyncronizerScheduler._instance = None
        scheduler = SyncronizerScheduler()
        scheduler._config = SchedulerConfig(enabled=True, cron="* * * * *", batch_size=50)
        # _skip_scheduler_init bypasses __init__, so wire ports and adapters manually
        scheduler._octadesk = mock_octadesk
        scheduler._rdstation = mock_rdstation
        scheduler._config_adapter = mock_param_instance
        scheduler.s3_adapter = MagicMock()

        # Execute the sync loop
        scheduler._execute()

        SyncronizerScheduler._instance = None

    # --- Assert DB persistence ---
    contacts = db_session.query(ContactModel).all()
    assert len(contacts) == 1
    assert contacts[0].name == "Scheduler Contact"
    assert contacts[0].info.email == "scheduler@test.com"
    assert contacts[0].info.phone == "12988881234"

    deals = db_session.query(DealModel).all()
    assert len(deals) == 1
    assert deals[0].rdstation_id == "deal-sched-999"

    chats = db_session.query(ChatModel).all()
    assert len(chats) == 1
    assert chats[0].octadesk_id == "room-sched-001"
