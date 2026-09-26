from unittest.mock import MagicMock
import pytest

from app.src.contracts.bwt.requests import DealStage
from app.src.domain.entities.bwt_sync_result import BWTSyncResult
from app.src.domain.entities.chat import Chat
from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal import Deal
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.bwt_port import BWTPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.octadesk_lookup import OctadeskLookup
from app.src.services.workflows.bwt_reverse_sync_service import BWTReverseSyncService
from app.src.services.workflows.rd_station_reverse_sync_service import (
    RDStationReverseSyncService,
)
from app.src.services.workflows.reverse_sync_workflow import ReverseSyncWorkflow


@pytest.fixture
def mock_bwt_port():
    mock = MagicMock(spec=BWTPort)
    mock.search_accounts.return_value = MagicMock(results=[])
    mock.get_account_contacts.return_value = MagicMock(results=[])
    mock.get_contacts_by_phone.return_value = MagicMock(count=0, results=[])
    mock.create_account.return_value = MagicMock(id=123, name="Account Name")
    mock.create_contact.return_value = MagicMock(id=456)

    mock_deals_response = MagicMock()
    mock_deals_response.count = 0
    mock_deals_response.next = None
    mock_deals_response.results = []
    mock.get_deals.return_value = mock_deals_response

    mock.create_deal.return_value = MagicMock(id=789, stage=DealStage.NEW_DEAL)
    mock.get_company_users.return_value = MagicMock(results=[MagicMock(id=999)])
    return mock


@pytest.fixture
def mock_octadesk():
    return MagicMock(spec=OctadeskPort)


@pytest.fixture
def mock_rdstation():
    return MagicMock(spec=RDStationPort)


@pytest.fixture
def mock_contact_repo():
    return MagicMock(spec=ContactRepositoryPort)


@pytest.fixture
def mock_deal_repo():
    return MagicMock(spec=DealRepositoryPort)


@pytest.fixture
def mock_chat_repo():
    return MagicMock(spec=ChatRepositoryPort)


@pytest.fixture
def mock_lookup(mock_octadesk, mock_contact_repo):
    return OctadeskLookup(mock_octadesk, mock_contact_repo)


def _build_workflow(
    mock_lookup,
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
):
    return ReverseSyncWorkflow(
        octadesk_lookup=mock_lookup,
        rd_sync=RDStationReverseSyncService(mock_rdstation, mock_deal_repo),
        bwt_sync=BWTReverseSyncService(),
        contact_repo=mock_contact_repo,
        deal_repo=mock_deal_repo,
        chat_repo=mock_chat_repo,
    )


def test_reverse_sync_workflow_new_contact_new_deal(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-100",
        "contact": {
            "name": "Maria Silva",
            "email": "maria@test.com",
            "phoneContacts": [{"number": "11999998888"}],
        },
    }

    mock_contact_repo.find_by_phone.return_value = None
    mock_contact_repo.save.side_effect = lambda c: Contact(
        id="c-100", name=c.name, phone=c.phone, email=c.email
    )
    mock_chat_repo.find_by_octadesk_id.return_value = None
    mock_rdstation.get_contacts.return_value = {"contacts": []}
    mock_rdstation.post_deal.return_value = {
        "id": "deal-rd-100",
        "deal_source": {"name": "Octadesk"},
        "campaign": {"name": "Camp1"},
    }

    workflow.execute(
        chat=chat_input,
        seller="Vendedor 1",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor"
    )

    # save é chamado ao menos uma vez na criação do contato (e uma segunda em _persist_bwt_ids)
    mock_contact_repo.save.assert_called()
    mock_chat_repo.save.assert_called_once()
    mock_rdstation.post_deal.assert_called_once_with(
        stage_id="stage-epv",
        contact_name="Maria Silva",
        phone="11999998888",
    )
    mock_rdstation.put_deal.assert_called_once_with(
        deal_id="deal-rd-100",
        stage_id="stage-epv",
        seller_name="Vendedor 1",
        source="Octadesk"
    )
    # deal_repo.save é chamado ao menos uma vez no sync RD (e uma segunda em _persist_bwt_ids)
    mock_deal_repo.save.assert_called()
    mock_bwt_port.create_account.assert_called_once()


def test_reverse_sync_workflow_existing_contact_update_deal(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-200",
        "contact": {
            "name": "João Souza",
            "email": "joao@test.com",
            "phoneContacts": [{"number": "11988887777"}],
        },
    }

    existing_contact = Contact(
        id="c-200", name="João Souza", phone="11988887777", email="joao@test.com"
    )
    mock_contact_repo.find_by_phone.return_value = existing_contact
    mock_chat_repo.find_by_octadesk_id.return_value = Chat(
        id="chat-id-200", octadesk_id="chat-200"
    )

    rd_contact = {
        "id": "rd-c-200",
        "name": "João Souza",
        "phones": [{"phone": "11988887777"}],
        "emails": [{"email": "joao@test.com"}],
        "deals": [{"id": "rd-deal-200"}],
    }
    mock_rdstation.get_contacts.return_value = {"contacts": [rd_contact]}

    rd_deal_raw = {
        "id": "rd-deal-200",
        "name": "Negócio 200",
        "deal_source": {"name": "Site"},
        "deal_stage": {"nickname": "SC"},
    }
    mock_rdstation.get_deal.return_value = rd_deal_raw
    mock_deal_repo.find_by_rdstation_id.return_value = None

    workflow.execute(
        chat=chat_input,
        seller="Vendedor 2",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor"
    )

    assert mock_rdstation.get_deal.called
    mock_rdstation.put_deal.assert_called_once_with(
        deal_id="rd-deal-200",
        stage_id="stage-epv",
        seller_name="Vendedor 2",
    )
    mock_rdstation.post_deal.assert_not_called()


def test_reverse_sync_workflow_final_status_creates_new_deal(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-300",
        "contact": {
            "name": "Carlos Lima",
            "email": "carlos@test.com",
            "phoneContacts": [{"number": "11977776666"}],
        },
    }

    existing_contact = Contact(
        id="c-300", name="Carlos Lima", phone="11977776666", email="carlos@test.com"
    )
    mock_contact_repo.find_by_phone.return_value = existing_contact
    mock_chat_repo.find_by_octadesk_id.return_value = Chat(
        id="chat-id-300", octadesk_id="chat-300"
    )

    rd_contact = {
        "id": "rd-c-300",
        "name": "Carlos Lima",
        "phones": [{"phone": "11977776666"}],
        "emails": [{"email": "carlos@test.com"}],
        "deals": [{"id": "rd-deal-300"}],
    }
    mock_rdstation.get_contacts.return_value = {"contacts": [rd_contact]}

    rd_deal_raw = {
        "id": "rd-deal-300",
        "name": "Negócio 300",
        "deal_source": {"name": "Site"},
        "deal_stage": {"nickname": "NR"},
    }
    mock_rdstation.get_deal.return_value = rd_deal_raw
    mock_deal_repo.find_by_rdstation_id.return_value = Deal(
        deal_id="rd-deal-300",
        name="Negócio 300",
        phone="11977776666",
        email="carlos@test.com",
        deal_source_name="Site",
        deal_campaign_name="",
        rdstation_id="rd-deal-300",
    )

    mock_rdstation.post_deal.return_value = {
        "id": "rd-deal-301-new",
        "deal_source": {"name": "Site"},
        "campaign": {"name": ""},
    }

    workflow.execute(
        chat=chat_input,
        seller="Vendedor 3",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor"
    )

    mock_rdstation.post_deal.assert_called_once()


def test_reverse_sync_workflow_in_progress_no_new_deal(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-400",
        "contact": {
            "name": "Ana Clara",
            "email": "ana@test.com",
            "phoneContacts": [{"number": "11966665555"}],
        },
    }

    existing_contact = Contact(
        id="c-400", name="Ana Clara", phone="11966665555", email="ana@test.com"
    )
    mock_contact_repo.find_by_phone.return_value = existing_contact
    mock_chat_repo.find_by_octadesk_id.return_value = Chat(
        id="chat-id-400", octadesk_id="chat-400"
    )

    rd_contact = {
        "id": "rd-c-400",
        "name": "Ana Clara",
        "phones": [{"phone": "11966665555"}],
        "emails": [{"email": "ana@test.com"}],
        "deals": [{"id": "rd-deal-400", "deal_stage": {"nickname": "EPV"}}],
    }
    mock_rdstation.get_contacts.return_value = {"contacts": [rd_contact]}

    rd_deal_raw = {
        "id": "rd-deal-400",
        "name": "Negócio 400",
        "deal_source": {"name": "Site"},
        "deal_stage": {"nickname": "EPV"},
    }
    mock_rdstation.get_deal.return_value = rd_deal_raw
    mock_deal_repo.find_by_rdstation_id.return_value = None

    workflow.execute(
        chat=chat_input,
        seller="Vendedor 4",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor"
    )

    mock_rdstation.post_deal.assert_not_called()


def test_persist_bwt_ids_updates_contact_with_bwt_ids(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    """Verifica que contact.bwt_account_id e contact.bwt_contact_id são persistidos."""
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-500",
        "contact": {
            "name": "Luiza Fraga",
            "email": "luiza@test.com",
            "phoneContacts": [{"number": "11944443333"}],
        },
    }

    saved_contact = Contact(id="c-500", name="Luiza Fraga", phone="11944443333", email="luiza@test.com")
    mock_contact_repo.find_by_phone.return_value = None
    mock_contact_repo.save.return_value = saved_contact
    mock_chat_repo.find_by_octadesk_id.return_value = None
    mock_rdstation.get_contacts.return_value = {"contacts": []}
    mock_rdstation.post_deal.return_value = {
        "id": "rd-deal-500",
        "deal_source": {"name": "Octadesk"},
        "campaign": {"name": ""},
    }

    # BWT port returns fixed IDs
    mock_bwt_port.create_account.return_value = MagicMock(id=111, name="Luiza Fraga")
    mock_bwt_port.create_contact.return_value = MagicMock(id=222)
    mock_bwt_port.create_deal.return_value = MagicMock(id=333, stage=DealStage.NEW_DEAL)
    mock_bwt_port.get_company_users.return_value = MagicMock(results=[])
    mock_deal_repo.find_by_contact_id.return_value = Deal(
        deal_id="rd-deal-500",
        name="Luiza Fraga",
        phone="11944443333",
        email="luiza@test.com",
        deal_source_name="Octadesk",
        deal_campaign_name="",
        id="d-500",
        rdstation_id="rd-deal-500",
    )

    workflow.execute(
        chat=chat_input,
        seller="Vendedor 5",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor",
    )

    # contact_repo.save deve ter sido chamado ao menos 2x:
    # 1x na criação do contato, 1x na persistência dos IDs BWT
    assert mock_contact_repo.save.call_count >= 2

    # último save do contact deve ter os IDs BWT preenchidos
    last_saved_contact = mock_contact_repo.save.call_args_list[-1].args[0]
    assert last_saved_contact.bwt_account_id == 111
    assert last_saved_contact.bwt_contact_id == 222


def test_persist_bwt_ids_updates_deal_with_bwt_ids(
    mock_rdstation,
    mock_contact_repo,
    mock_deal_repo,
    mock_chat_repo,
    mock_lookup,
    mock_bwt_port,
):
    """Verifica que deal.bwt_deal_id e deal.bwt_responsible_id são persistidos."""
    workflow = _build_workflow(
        mock_lookup, mock_rdstation, mock_contact_repo, mock_deal_repo, mock_chat_repo
    )

    chat_input = {
        "id": "chat-600",
        "contact": {
            "name": "Ricardo Alves",
            "email": "ricardo@test.com",
            "phoneContacts": [{"number": "11933332222"}],
        },
    }

    saved_contact = Contact(id="c-600", name="Ricardo Alves", phone="11933332222", email="ricardo@test.com")
    mock_contact_repo.find_by_phone.return_value = None
    mock_contact_repo.save.return_value = saved_contact
    mock_chat_repo.find_by_octadesk_id.return_value = None
    mock_rdstation.get_contacts.return_value = {"contacts": []}
    mock_rdstation.post_deal.return_value = {
        "id": "rd-deal-600",
        "deal_source": {"name": "Octadesk"},
        "campaign": {"name": ""},
    }

    seller_user = MagicMock(id=888, is_active=True)
    mock_bwt_port.create_account.return_value = MagicMock(id=444, name="Ricardo Alves")
    mock_bwt_port.create_contact.return_value = MagicMock(id=555)
    mock_bwt_port.create_deal.return_value = MagicMock(id=666, stage=DealStage.NEW_DEAL)
    # get_deal is called by _resolve_or_create_active_deal; must return id=666 and NEW_DEAL stage
    mock_bwt_port.get_deal.return_value = MagicMock(id=666, stage=DealStage.NEW_DEAL)
    mock_bwt_port.get_company_users.return_value = MagicMock(results=[seller_user])

    existing_deal = Deal(
        deal_id="rd-deal-600",
        name="Ricardo Alves",
        phone="11933332222",
        email="ricardo@test.com",
        deal_source_name="Octadesk",
        deal_campaign_name="",
        id="d-600",
        rdstation_id="rd-deal-600",
    )
    mock_deal_repo.find_by_contact_id.return_value = existing_deal

    workflow.execute(
        chat=chat_input,
        seller="Ricardo Vendedor",
        with_seller_stage_id="stage-epv",
        bwt_port=mock_bwt_port,
        supervisor="Supervisor",
    )

    # deal_repo.save deve ter sido chamado ao menos 2x:
    # 1x no sync RD Station, 1x na persistência dos IDs BWT
    assert mock_deal_repo.save.call_count >= 2

    # último save do deal deve ter os IDs BWT preenchidos
    last_saved_deal = mock_deal_repo.save.call_args_list[-1].args[0]
    assert last_saved_deal.bwt_deal_id == 666
    assert last_saved_deal.bwt_responsible_id == 888


def test_persist_bwt_ids_handles_missing_repos_and_deal():
    contact = Contact(id="c-999", name="Test", phone="11900000000", email="test@test.com")
    bwt_result = BWTSyncResult(account_id=1, contact_id=2, deal_id=3, responsible_id=4)

    # 1. No contact_repo
    workflow_no_contact_repo = ReverseSyncWorkflow(
        octadesk_lookup=MagicMock(),
        rd_sync=MagicMock(),
        bwt_sync=MagicMock(),
        contact_repo=None,
        deal_repo=MagicMock(),
        chat_repo=MagicMock(),
    )
    workflow_no_contact_repo._persist_bwt_ids(contact, bwt_result)

    # 2. No deal_repo
    mock_c_repo = MagicMock()
    mock_c_repo.save.return_value = contact
    workflow_no_deal_repo = ReverseSyncWorkflow(
        octadesk_lookup=MagicMock(),
        rd_sync=MagicMock(),
        bwt_sync=MagicMock(),
        contact_repo=mock_c_repo,
        deal_repo=None,
        chat_repo=MagicMock(),
    )
    workflow_no_deal_repo._persist_bwt_ids(contact, bwt_result)
    mock_c_repo.save.assert_called_once()

    # 3. Deal not found
    mock_d_repo = MagicMock()
    mock_d_repo.find_by_contact_id.return_value = None
    workflow_no_deal = ReverseSyncWorkflow(
        octadesk_lookup=MagicMock(),
        rd_sync=MagicMock(),
        bwt_sync=MagicMock(),
        contact_repo=mock_c_repo,
        deal_repo=mock_d_repo,
        chat_repo=MagicMock(),
    )
    workflow_no_deal._persist_bwt_ids(contact, bwt_result)
    mock_d_repo.save.assert_not_called()


