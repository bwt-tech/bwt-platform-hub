from unittest.mock import MagicMock
from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal import Deal
from app.src.services.workflows.rd_station_reverse_sync_service import RDStationReverseSyncService


def test_rd_station_reverse_sync_service_none_response_and_missing_rdstation_id():
    mock_rd = MagicMock()
    mock_rd.get_contacts.return_value = None

    service = RDStationReverseSyncService(rdstation_port=mock_rd, deal_repo=None)
    contact = Contact(id="c-1", name="Test", phone="11999998888", email="test@test.com")

    # Tests _fetch_rd_contacts returning [] on None response, creating a new deal
    mock_rd.post_deal.return_value = {
        "id": "new-rd-deal",
        "deal_source": {"name": "Octadesk"},
        "campaign": {"name": "Camp"},
    }

    service.sync_deals(
        contact=contact,
        contact_name="Test",
        contact_phone="11999998888",
        contact_email="test@test.com",
        seller="Seller",
        with_seller_stage_id="stage-1",
    )

    mock_rd.post_deal.assert_called_once()


def test_persist_deal_if_missing_when_rdstation_id_none_or_no_repo():
    mock_rd = MagicMock()
    service_no_repo = RDStationReverseSyncService(rdstation_port=mock_rd, deal_repo=None)
    contact = Contact(id="c-1", name="Test", phone="11999998888", email="test@test.com")
    deal_no_id = Deal(
        deal_id="d-1",
        name="Deal",
        phone="11999998888",
        email="test@test.com",
        deal_source_name="Source",
        deal_campaign_name="Camp",
        rdstation_id="",
    )

    # Should return early without error when deal_repo is None
    service_no_repo._persist_deal_if_missing(deal_no_id, contact)

    # Should return early when rdstation_id is empty
    mock_repo = MagicMock()
    service_with_repo = RDStationReverseSyncService(rdstation_port=mock_rd, deal_repo=mock_repo)
    service_with_repo._persist_deal_if_missing(deal_no_id, contact)
    mock_repo.find_by_rdstation_id.assert_not_called()
