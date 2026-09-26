from app.src.domain.entities.contact import Contact


def test_contact_initialization():
    contact = Contact(
        name="Test User", phone="5511999999999", email="test@example.com", deal_id="123"
    )
    assert contact.name == "Test User"
    assert contact.phone == "5511999999999"
    assert contact.email == "test@example.com"
    assert contact.deal_id == "123"
    assert contact.chat_response is None


def test_contact_to_dict():
    contact = Contact(
        name="Test User",
        phone="5511999999999",
        email="test@example.com",
        deal_id="123",
        chat_response={"id": "chat123"},
    )
    contact_dict = contact.to_dict()
    assert contact_dict == {
        "name": "Test User",
        "phone": "5511999999999",
        "email": "test@example.com",
        "deal_id": "123",
        "chat_response": {"id": "chat123"},
    }


def test_contact_timestamps_default_none():
    contact = Contact(
        name="Test", phone="5511999999999", email="test@example.com", deal_id="123"
    )
    assert contact.created_at is None
    assert contact.updated_at is None


def test_contact_with_timestamps():
    from datetime import datetime
    now = datetime.now()
    contact = Contact(
        name="Test",
        phone="5511999999999",
        email="test@example.com",
        deal_id="123",
        created_at=now,
        updated_at=now,
    )
    assert contact.created_at == now
    assert contact.updated_at == now
