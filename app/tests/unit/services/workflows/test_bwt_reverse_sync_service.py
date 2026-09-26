from unittest.mock import MagicMock

from app.src.contracts.bwt.requests import DealStage
from app.src.domain.entities.bwt_sync_result import BWTSyncResult
from app.src.ports.bwt_port import BWTPort
from app.src.services.workflows.bwt_reverse_sync_service import BWTReverseSyncService


def _build_bwt_port(
    accounts=None,
    contacts=None,
    deals_pages=None,
    create_deal_stage=DealStage.NEW_DEAL,
    sellers=None,
):
    mock = MagicMock(spec=BWTPort)
    if contacts:
        mock.get_contacts_by_phone.return_value = MagicMock(
            count=len(contacts), results=contacts
        )
    else:
        mock.get_contacts_by_phone.return_value = MagicMock(count=0, results=[])

    mock.create_account.return_value = MagicMock(id=100, name="New Account")
    mock.create_contact.return_value = MagicMock(id=200)
    mock.create_deal.return_value = MagicMock(id=300, stage=create_deal_stage)
    mock.get_deal.return_value = MagicMock(id=300, stage=create_deal_stage)

    if deals_pages is None:
        empty_page = MagicMock(count=0, next=None, results=[])
        mock.get_deals.return_value = empty_page
    else:
        mock.get_deals.side_effect = deals_pages

    mock.get_company_users.return_value = MagicMock(results=sellers or [])
    return mock


def test_sync_creates_account_contact_and_deal_and_returns_bwt_sync_result():
    bwt_port = _build_bwt_port()
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Maria Silva",
        contact_email="maria@test.com",
        contact_phone="11999998888",
        seller="Vendedor",
        supervisor="Supervisor"
    )

    bwt_port.create_account.assert_called_once_with(name="Maria Silva")
    bwt_port.create_contact.assert_called_once()
    bwt_port.create_deal.assert_called_once()
    bwt_port.update_deal_status.assert_called_once_with(
        deal_id=300, stage=DealStage.CONTACTED
    )
    assert isinstance(result, BWTSyncResult)
    assert result.account_id == 100
    assert result.contact_id == 200
    assert result.deal_id == bwt_port.get_deal.return_value.id


def test_sync_reuses_existing_account_and_contact():
    account = MagicMock(id=10, name="João Souza")
    contact = MagicMock(id=20, accounts=[account])
    contact.phone.number = "11988887777"
    bwt_port = _build_bwt_port(accounts=[account], contacts=[contact])
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="João Souza",
        contact_email="joao@test.com",
        contact_phone="11988887777",
        seller="Vendedor",
        supervisor="Supervisor"
    )

    bwt_port.create_account.assert_not_called()
    bwt_port.create_contact.assert_not_called()
    assert result.account_id == 10
    assert result.contact_id == 20


def test_sync_reuses_active_deal_and_returns_deal_id():
    account = MagicMock(id=10, name="Ana Clara")
    contact = MagicMock(id=20, account=account)
    contact.phone.number = "11966665555"
    active_deal = MagicMock(id=500, stage=DealStage.CONTACTED)
    deals_page = MagicMock(count=1, next=None, results=[active_deal])
    bwt_port = _build_bwt_port(
        accounts=[account],
        contacts=[contact],
        deals_pages=[deals_page],
    )
    bwt_port.get_deal.return_value = MagicMock(id=500, stage=DealStage.CONTACTED)
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Ana Clara",
        contact_email="ana@test.com",
        contact_phone="11966665555",
        seller="Vendedor",
        supervisor="Supervisor"
    )

    bwt_port.create_deal.assert_not_called()
    bwt_port.update_deal_status.assert_not_called()
    assert result.deal_id == 500
    assert result.responsible_id is None


def test_sync_assigns_seller_and_returns_responsible_id():
    bwt_port = _build_bwt_port(sellers=[MagicMock(id=999, is_active=True)])
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Carlos",
        contact_email="carlos@test.com",
        contact_phone="11977776666",
        seller="Carlos Vendedor",
        supervisor="Supervisor"
    )

    bwt_port.set_deal_responsible.assert_called_once_with(
        deal_id=300, responsible_id=999
    )
    assert result.responsible_id == 999


def test_sync_skips_seller_assignment_and_returns_none_responsible_id():
    bwt_port = _build_bwt_port(
        sellers=[MagicMock(id=1, is_active=True), MagicMock(id=2, is_active=True)]
    )
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Carlos",
        contact_email="carlos@test.com",
        contact_phone="11977776666",
        seller="Carlos",
        supervisor="Supervisor"
    )

    bwt_port.set_deal_responsible.assert_not_called()
    assert result.responsible_id is None


def test_sync_assigns_supervisor_when_seller_not_found():
    bwt_port = _build_bwt_port()
    supervisor_user = MagicMock(id=888, is_active=True)

    def mock_company_users(search_term):
        if search_term == "Supervisor":
            return MagicMock(results=[supervisor_user])
        return MagicMock(results=[])

    bwt_port.get_company_users.side_effect = mock_company_users

    service = BWTReverseSyncService()
    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Carlos",
        contact_email="carlos@test.com",
        contact_phone="11977776666",
        seller="Unknown Seller",
        supervisor="Supervisor"
    )

    bwt_port.set_deal_responsible.assert_called_once_with(
        deal_id=300, responsible_id=888
    )
    assert result.responsible_id == 888


def test_sync_skips_status_advance_when_deal_stage_is_none():
    bwt_port = _build_bwt_port(create_deal_stage=None)
    service = BWTReverseSyncService()

    result = service.sync(
        bwt_port=bwt_port,
        contact_name="Pedro",
        contact_email="pedro@test.com",
        contact_phone="11955554444",
        seller="Vendedor",
        supervisor="Supervisor"
    )

    bwt_port.update_deal_status.assert_not_called()
    assert result.responsible_id is None


def test_sync_paginates_deals():
    page_one = MagicMock(count=1, next="page2", results=[])
    page_two = MagicMock(
        count=1,
        next=None,
        results=[MagicMock(id=400, stage=DealStage.QUOTE)],
    )
    bwt_port = _build_bwt_port(deals_pages=[page_one, page_two])
    service = BWTReverseSyncService()

    service.sync(
        bwt_port=bwt_port,
        contact_name="Pedro",
        contact_email="pedro@test.com",
        contact_phone="11955554444",
        seller="Vendedor",
        supervisor="Supervisor"
    )

    assert bwt_port.get_deals.call_count == 2
    bwt_port.create_deal.assert_not_called()
