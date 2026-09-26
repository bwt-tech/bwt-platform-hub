import pytest
from pydantic import ValidationError

from app.src.contracts.octadesk.requests import (
    OctadeskChatStartRequest,
    OctadeskContactCreateRequest,
)


def test_octadesk_contact_create_request_valid():
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "phoneContacts": [{"number": "11999999999", "countryCode": "55"}],
    }
    obj = OctadeskContactCreateRequest(**payload)
    assert obj.name == "Test User"
    assert obj.phoneContacts[0].countryCode == "55"


def test_octadesk_contact_create_request_invalid():
    with pytest.raises(ValidationError):
        OctadeskContactCreateRequest(
            name="Test User"
        )  # missing email and phoneContacts


def test_octadesk_chat_start_request_valid():
    payload = {
        "origin": {"contact": {"channel": "whatsapp", "code": "+5511999999999"}},
        "target": {"contact": {"channel": "whatsapp", "code": "+5511888888888"}},
        "content": {"templateMessage": {"id": "template_123"}},
    }
    obj = OctadeskChatStartRequest(**payload)
    assert obj.origin.contact.channel == "whatsapp"
    assert obj.content.templateMessage.id == "template_123"


def test_octadesk_chat_start_request_invalid():
    with pytest.raises(ValidationError):
        OctadeskChatStartRequest(origin={}, target={}, content={})
