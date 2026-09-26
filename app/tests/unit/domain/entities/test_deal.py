import pytest
from app.src.domain.entities.deal import Deal


def test_deal_normalization():
    phone = Deal.normalize_phone("(11) 99999-9999")
    assert phone == "11999999999"


def test_deal_validation_success():
    deal_dict = {
        "contacts": [
            {
                "phones": [{"phone": "11999999999"}],
                "emails": [{"email": "test@example.com"}],
            }
        ]
    }
    Deal.validate_prerequisites(deal_dict)  # Should not raise


def test_deal_validation_failure():
    deal_dict = {"contacts": []}
    with pytest.raises(ValueError, match="Prerequisites not met"):
        Deal.validate_prerequisites(deal_dict)


def test_deal_from_dict():
    deal_dict = {
        "id": "123",
        "name": "Test Deal",
        "contacts": [
            {
                "phones": [{"phone": "(11) 99999-9999"}],
                "emails": [{"email": "test@example.com"}],
            }
        ],
        "deal_source": {"name": "source"},
        "campaign": {"name": "campaign"},
    }
    deal = Deal.from_dict(deal_dict)
    assert deal.deal_id == "123"
    assert deal.name == "Test Deal"
    assert deal.phone == "11999999999"
    assert deal.email == "test@example.com"
    assert deal.deal_source_name == "source"
    assert deal.deal_campaign_name == "campaign"


def test_deal_to_contact():
    deal = Deal(
        deal_id="123",
        name="Test Deal",
        phone="11999999999",
        email="test@example.com",
        deal_source_name="source",
        deal_campaign_name="campaign",
    )
    contact = deal.to_contact()
    assert contact.name == "Test Deal"
    assert contact.phone == "11999999999"
    assert contact.email == "test@example.com"
    assert contact.deal_id == "123"


def test_deal_timestamps_default_none():
    deal = Deal(
        deal_id="123",
        name="Test Deal",
        phone="11999999999",
        email="test@example.com",
        deal_source_name="source",
        deal_campaign_name="campaign",
    )
    assert deal.created_at is None
    assert deal.updated_at is None


def test_deal_with_timestamps():
    from datetime import datetime
    now = datetime.now()
    deal = Deal(
        deal_id="123",
        name="Test Deal",
        phone="11999999999",
        email="test@example.com",
        deal_source_name="source",
        deal_campaign_name="campaign",
        created_at=now,
        updated_at=now,
    )
    assert deal.created_at == now
    assert deal.updated_at == now
