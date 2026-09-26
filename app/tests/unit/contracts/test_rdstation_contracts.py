import pytest
from pydantic import ValidationError

from app.src.contracts.rdstation.responses import (
    RDStationDeal,
    RDStationDealPipeline,
    RDStationDealWrapper,
)


def test_rdstation_deal_pipeline_valid():
    payload = {
        "id": "pipeline_123",
        "name": "Sales",
        "deal_stages": [{"id": "stage_1", "nickname": "SC"}],
    }
    obj = RDStationDealPipeline(**payload)
    assert obj.id == "pipeline_123"
    assert obj.deal_stages[0].nickname == "SC"


def test_rdstation_deal_pipeline_invalid():
    with pytest.raises(ValidationError):
        RDStationDealPipeline(id="123")  # Missing required fields


def test_rdstation_deal_valid():
    payload = {
        "id": "deal_123",
        "name": "Big Deal",
        "contacts": [
            {
                "name": "Contact 1",
                "emails": [{"email": "c1@test.com"}],
                "phones": [{"phone": "11999999999"}],
            }
        ],
    }
    obj = RDStationDeal(**payload)
    assert obj.contacts[0].phones[0].phone == "11999999999"


def test_rdstation_deal_wrapper_valid():
    payload = {"deals": [{"id": "deal_123", "name": "Big Deal", "contacts": []}]}
    obj = RDStationDealWrapper(**payload)
    assert len(obj.deals) == 1
