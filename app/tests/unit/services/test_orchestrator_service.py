from unittest.mock import MagicMock

import pytest

import app.src.config.settings as s
from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.agent import Agent
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.orchestrator import PROCESSED, OrchestratorService

s = MagicMock()


@pytest.fixture(autouse=True)
def clear_processed_set():
    """Clear the global PROCESSED set before each test to avoid cross-test contamination."""
    PROCESSED.clear()
    yield
    PROCESSED.clear()


AGENT_FIXTURE = Agent(
    id="agent-1", name="Test Agent", email="agent@test.com", key="KEY_TEST"
)

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
                "key": "KEY_TEST",
            },
        }
    }
}

PIPELINE_WITH_STAGES = [
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


@pytest.fixture
def mock_octadesk():
    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    return MagicMock(spec=RDStationPort)


def _build_service(mock_octadesk, mock_rdstation, monkeypatch, templates=None):
    """Helper to build an OrchestratorService with mocked YAML loading."""
    monkeypatch.setattr("builtins.open", MagicMock())
    monkeypatch.setattr(
        "yaml.safe_load",
        lambda _: templates if templates is not None else TEMPLATES_FIXTURE,
    )
    return OrchestratorService(
        octadesk_port=mock_octadesk, rdstation_port=mock_rdstation
    )


def _make_deal(deal_id, name="User", phone="999", email="u@e.com"):
    """Helper to build a minimal deal dict."""
    return {
        "id": deal_id,
        "name": name,
        "contacts": [{"phones": [{"phone": phone}], "emails": [{"email": email}]}],
        "deal_source": {"name": "Test Source"},
        "campaign": {"name": "Test Campaign"},
    }


def test_orchestrator_resilient_iteration(mock_octadesk, mock_rdstation, monkeypatch):
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {
                "deals": [
                    _make_deal("deal1", "User 1", "111", "1@1.com"),
                    _make_deal("deal2", "User 2", "222", "2@2.com"),
                    {"id": "deal3_bad_req", "contacts": []},
                    _make_deal("deal4_old_chat", "User 4", "444", "4@4.com"),
                    _make_deal("deal5_no_chat", "User 5", "555", "5@5.com"),
                ]
            }
        elif deal_stage_id == "s2":
            return {
                "deals": [
                    _make_deal("deal6_recurring", "User 1", "111", "1@1.com"),
                    {"id": "bad_req_in_no_answer", "contacts": []},
                ]
            }
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals

    def mock_get_contacts_by_phone(phone):
        if phone == "222":
            raise IntegrationError("Timeout")
        elif phone in ("111", "444"):
            # phone 111 and 444 are existing contacts in Octadesk
            return [{"id": f"c_{phone}"}]
        return []

    mock_octadesk.get_contacts_by_phone.side_effect = mock_get_contacts_by_phone

    # phone "111" and "444" have existing chats — no start_chat triggered
    # phone "555" has no chats — triggers start_chat
    def mock_get_chats(phone=None):
        if phone in ("111", "444"):
            return [{"id": f"chat_{phone}"}]
        return []

    mock_octadesk.get_chats_by_phone.side_effect = mock_get_chats
    mock_octadesk.start_chat.return_value = {"response": {"result": {"roomKey": "123"}}}

    service.start_process()

    calls = mock_octadesk.start_chat.call_args_list
    assert len(calls) == 1
    assert calls[0][0][0]["phone"] == "555"
    assert calls[0][0][0]["deal_id"] == "deal5_no_chat"
    assert calls[0][0][1] == {"phone": "code", "template": "id", "write_enabled": False}



def test_orchestrator_get_deal_pipelines_fails(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_service(
        mock_octadesk, mock_rdstation, monkeypatch, TEMPLATES_FIXTURE["templates"]
    )
    mock_rdstation.get_deal_pipelines.side_effect = IntegrationError("API error")

    service.start_process()  # Should exit early returning None


def test_orchestrator_get_deals_fails_on_no_contact(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_service(
        mock_octadesk, mock_rdstation, monkeypatch, TEMPLATES_FIXTURE["templates"]
    )
    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    def side_effect(deal_stage_id=None):
        if deal_stage_id == "s1":
            raise IntegrationError("API error")
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = side_effect

    service.start_process()  # Should log error and continue without crash


def test_orchestrator_is_recurring_no_answer_fails(
    mock_octadesk, mock_rdstation, monkeypatch
):
    service = _build_service(
        mock_octadesk, mock_rdstation, monkeypatch, TEMPLATES_FIXTURE["templates"]
    )
    mock_rdstation.get_deals.side_effect = IntegrationError("API")
    result = service._is_recurring_no_answer("Test", "123", DealStage(id="s1"))
    assert result is False


def test_yaml_load_failure(mock_octadesk, mock_rdstation, monkeypatch):
    monkeypatch.setattr("builtins.open", MagicMock(side_effect=OSError("File missing")))
    service = OrchestratorService(
        octadesk_port=mock_octadesk, rdstation_port=mock_rdstation
    )
    assert service.templates == {}


def test_orchestrator_no_answer_adapter_error_on_matching_deal(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """Covers: IntegrationError inside the NO_ANSWER loop
    when put_deal raises an adapter error on a matching phone."""
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    no_answer_deal = _make_deal("na_deal", "User X", "888", "x@x.com")

    mock_rdstation.get_deals.return_value = {"deals": [no_answer_deal]}
    mock_rdstation.put_deal.side_effect = IntegrationError("put_deal failed")

    result = service._is_recurring_no_answer("User X", "888", DealStage(id="s2"))
    assert result is False
    mock_rdstation.put_deal.assert_called_once()


def test_orchestrator_new_contact_chat_confirmed(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """New contact: post_contacts + start_chat called. put_deal called."""
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    new_deal = _make_deal("deal_new", "New User", "777", "new@u.com")

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [new_deal]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = []  # No existing contact
    mock_octadesk.get_chats_by_phone.side_effect = [[], [], [{"id": "chat_777"}]]
    mock_octadesk.start_chat.return_value = {"response": {"result": {"roomKey": "123"}}}

    service.start_process()

    mock_octadesk.post_contacts.assert_called_once_with("new@u.com", "New User", "777")
    calls = mock_octadesk.start_chat.call_args_list
    assert len(calls) == 1
    assert calls[0][0][0]["phone"] == "777"
    assert calls[0][0][0]["deal_id"] == "deal_new"
    assert calls[0][0][1] == {"phone": "code", "template": "id", "write_enabled": False}
    mock_rdstation.put_deal.assert_called_once_with("deal_new", "s3")

    # Assert dynamic agent was passed to notify_agent
    notify_calls = mock_octadesk.notify_agent.call_args_list
    assert len(notify_calls) == 1
    assert notify_calls[0][0][2].id == "agent-1"
    assert notify_calls[0][0][2].name == "Test Agent"
    assert notify_calls[0][0][2].email == "agent@test.com"


def test_orchestrator_new_contact_chat_not_confirmed(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """New contact: post_contacts + start_chat called. put_deal IS called."""
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    new_deal = _make_deal("deal_noconf", "Ghost User", "321", "ghost@u.com")

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [new_deal]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = []  # No existing contact
    mock_octadesk.get_chats_by_phone.return_value = []  # No chats at any point
    mock_octadesk.start_chat.return_value = {"response": {"result": {"roomKey": "123"}}}

    service.start_process()

    mock_octadesk.post_contacts.assert_called_once_with(
        "ghost@u.com", "Ghost User", "321"
    )
    calls = mock_octadesk.start_chat.call_args_list
    assert len(calls) == 1
    assert calls[0][0][0]["phone"] == "321"
    assert calls[0][0][0]["deal_id"] == "deal_noconf"
    assert calls[0][0][1] == {"phone": "code", "template": "id", "write_enabled": False}
    mock_rdstation.put_deal.assert_called_once_with("deal_noconf", "s3")


def test_orchestrator_existing_contact_with_existing_chat(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """Existing contact with an active chat: start_chat NOT called, put_deal IS called."""
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    existing_deal = _make_deal("deal_existing", "Old User", "999", "old@u.com")

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [existing_deal]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = [
        {"id": "c_999"}
    ]  # Contact exists
    mock_octadesk.get_chats_by_phone.return_value = [{"id": "chat_999"}]  # Chat exists

    service.start_process()

    mock_octadesk.start_chat.assert_not_called()
    mock_rdstation.put_deal.assert_called_once_with("deal_existing", "s3")

    # Assert dynamic agent was passed
    notify_calls = mock_octadesk.notify_agent.call_args_list
    assert len(notify_calls) == 1
    assert notify_calls[0][0][2].id == "agent-1"


def test_orchestrator_existing_contact_no_chat_starts_chat(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """Existing contact but no active chat: start_chat called, put_deal called."""
    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    existing_deal = _make_deal("deal_nochat", "Quiet User", "888", "quiet@u.com")

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [existing_deal]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = [
        {"id": "c_888"}
    ]  # Contact exists
    mock_octadesk.get_chats_by_phone.return_value = []
    mock_octadesk.start_chat.return_value = {
        "response": {"result": {"roomKey": "chat_888"}}
    }

    service.start_process()

    mock_octadesk.start_chat.assert_called_once()
    mock_rdstation.put_deal.assert_called_once_with("deal_nochat", "s3")
    mock_octadesk.notify_agent.assert_called_once_with(
        "chat_888",
        "Cliente se inscreveu por landing page (RD). Não havia conversa prévia. Origem: Test Source. Campanha: Test Campaign",
        AGENT_FIXTURE,
    )


def test_orchestrator_missing_template_configuration(
    mock_octadesk, mock_rdstation, monkeypatch
):
    """When templates dict is loaded but the expected template key is missing."""
    service = _build_service(
        mock_octadesk,
        mock_rdstation,
        monkeypatch,
        {
            "templates": {
                "SomeOtherTemplate": {
                    "phone": "x",
                    "template": "y",
                    "write_enabled": False,
                    "agent": {"id": "a", "name": "A", "email": "a@a.com"},
                }
            }
        },
    )

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    deal = _make_deal("deal_no_tpl", "No Tpl", "666", "n@t.com")

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [deal]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = []

    # Should NOT crash — ValueError is caught and logged as a warning
    service.start_process()
    mock_octadesk.post_contacts.assert_not_called()


def test_has_chats(mock_octadesk, mock_rdstation, monkeypatch):

    service = _build_service(
        mock_octadesk,
        mock_rdstation,
        monkeypatch,
        {
            "templates": {
                "SomeOtherTemplate": {
                    "phone": "x",
                    "template": "y",
                    "write_enabled": False,
                    "agent": {"id": "a", "name": "A", "email": "a@a.com"},
                }
            }
        },
    )
    deal = {"contacts": [{"phones": [{"phone": "+55 (12) 9 8163-1736"}]}]}
    phone = service._get_phone(deal)
    service._has_chat(phone)

    assert phone == "12981631736"


def test_orchestrator_sqlalchemy_error_handling(
    mock_octadesk, mock_rdstation, monkeypatch
):
    from sqlalchemy.exc import SQLAlchemyError

    service = _build_service(mock_octadesk, mock_rdstation, monkeypatch)
    service._new_contact_workflow = MagicMock()
    service._new_contact_workflow.execute.side_effect = SQLAlchemyError("DB failure")

    mock_rdstation.get_deal_pipelines.return_value = PIPELINE_WITH_STAGES

    def mock_get_deals(deal_stage_id=None):
        if deal_stage_id == "s1":
            return {"deals": [_make_deal("deal_db_err", "DB Error", "777", "err@db.com")]}
        return {"deals": []}

    mock_rdstation.get_deals.side_effect = mock_get_deals
    mock_octadesk.get_contacts_by_phone.return_value = []

    # Should catch SQLAlchemyError and record deal failed without crashing
    service.start_process()


