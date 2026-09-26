"""Unit tests for OctadeskContactResponse Pydantic contract (T025)."""

import pytest
from pydantic import ValidationError

from app.src.contracts.octadesk.contact_response import (
    OctadeskContactResponse,
    OctadeskCustomField,
    OctadeskPhoneContact,
)


def test_contact_response_minimal_valid():
    """Only 'id' is required."""
    data = {"id": "c-abc-123"}
    contact = OctadeskContactResponse.model_validate(data)
    assert contact.id == "c-abc-123"
    assert contact.name is None
    assert contact.email is None
    assert contact.phoneContacts == []
    assert contact.customFields == []


def test_contact_response_full_payload():
    """Full Octadesk contact payload is mapped correctly."""
    data = {
        "id": "c-full-001",
        "name": "Alice Full",
        "email": "alice@full.com",
        "phoneContacts": [
            {
                "number": "11999999999",
                "countryCode": "BR",
                "type": "mobile",
                "main": True,
            }
        ],
        "customFields": [{"id": "cf-1", "value": "custom_val"}],
    }
    contact = OctadeskContactResponse.model_validate(data)
    assert contact.id == "c-full-001"
    assert contact.name == "Alice Full"
    assert contact.email == "alice@full.com"
    assert len(contact.phoneContacts) == 1
    assert contact.phoneContacts[0].number == "11999999999"
    assert contact.phoneContacts[0].countryCode == "BR"
    assert contact.phoneContacts[0].main is True
    assert len(contact.customFields) == 1
    assert contact.customFields[0].id == "cf-1"
    assert contact.customFields[0].value == "custom_val"


def test_contact_response_missing_id_raises():
    """Pydantic must raise ValidationError when 'id' is absent."""
    with pytest.raises(ValidationError):
        OctadeskContactResponse.model_validate({"name": "No ID"})


def test_phone_contact_minimal():
    """OctadeskPhoneContact requires only 'number'."""
    phone = OctadeskPhoneContact.model_validate({"number": "55119"})
    assert phone.number == "55119"
    assert phone.countryCode is None


def test_custom_field_all_none():
    """OctadeskCustomField can have all optional fields as None."""
    field = OctadeskCustomField.model_validate({})
    assert field.id is None
    assert field.value is None


def test_contact_response_list_of_contacts():
    """Validates a list of Octadesk contact responses (typical API list response)."""
    raw = [{"id": "c-1"}, {"id": "c-2", "name": "Bob"}]
    contacts = [OctadeskContactResponse.model_validate(c) for c in raw]
    assert len(contacts) == 2
    assert contacts[0].id == "c-1"
    assert contacts[1].name == "Bob"
