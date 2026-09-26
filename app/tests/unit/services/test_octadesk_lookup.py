from unittest.mock import MagicMock

from app.src.domain.entities.contact import Contact
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.services.octadesk_lookup import OctadeskLookup


def test_has_contact_database_hit():
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)

    lookup = OctadeskLookup(mock_octadesk, mock_contact_repo)

    # Database returns a contact
    db_contact = Contact(
        id="c-uuid-123",
        name="Alice",
        phone="5511999999999",
        email="alice@example.com",
        deal_id="",
        octadesk_id="octa-alice-123",
    )
    mock_contact_repo.find_by_phone.return_value = db_contact

    # Execute
    res = lookup.has_contact("5511999999999")

    # Assertions
    assert res == "octa-alice-123"
    mock_contact_repo.find_by_phone.assert_called_with("5511999999999")
    mock_octadesk.get_contacts_by_phone.assert_not_called()


def test_has_contact_database_miss_api_hit():
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)

    lookup = OctadeskLookup(mock_octadesk, mock_contact_repo)

    # Database returns None
    mock_contact_repo.find_by_phone.return_value = None
    # Octadesk API returns contact list
    mock_octadesk.get_contacts_by_phone.return_value = [{"id": "octa-api-456"}]

    # Execute
    res = lookup.has_contact("5511999999999")

    # Assertions
    assert res == "octa-api-456"
    mock_contact_repo.find_by_phone.assert_called()
    mock_octadesk.get_contacts_by_phone.assert_called_with("5511999999999")


def test_has_contact_miss_all():
    mock_octadesk = MagicMock(spec=OctadeskPort)
    mock_contact_repo = MagicMock(spec=ContactRepositoryPort)

    lookup = OctadeskLookup(mock_octadesk, mock_contact_repo)

    # Both return None/empty
    mock_contact_repo.find_by_phone.return_value = None
    mock_octadesk.get_contacts_by_phone.return_value = []

    # Execute
    res = lookup.has_contact("5511999999999")

    # Assertions
    assert res is None

def test_all_phones_11_digits():
    lookup = OctadeskLookup(MagicMock(), MagicMock())
    phones = lookup.all_phones("11999998888")
    assert phones == ["11999998888", "1199998888"]


def test_all_phones_10_digits():
    lookup = OctadeskLookup(MagicMock(), MagicMock())
    phones = lookup.all_phones("1199998888")
    assert phones == ["11999998888", "1199998888"]
