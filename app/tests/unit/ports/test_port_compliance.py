import pytest
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort


def test_octadesk_port_is_abc():
    """Verify OctadeskPort cannot be instantiated and has the required abstract methods."""
    with pytest.raises(TypeError) as exc_info:
        OctadeskPort()

    error_msg = str(exc_info.value)
    expected_methods = [
        "check",
        "get_chats",
        "get_chats_by_phone",
        "get_chat_numbers",
        "get_events",
        "get_messages",
        "post_contacts",
        "get_contacts_by_phone",
        "get_templates",
        "start_chat",
    ]
    for method in expected_methods:
        assert (
            method in error_msg
        ), f"Expected abstract method {method} not found in TypeError"


def test_rdstation_port_is_abc():
    """Verify RDStationPort cannot be instantiated and has the required abstract methods."""
    with pytest.raises(TypeError) as exc_info:
        RDStationPort()

    error_msg = str(exc_info.value)
    expected_methods = [
        "get_users",
        "get_campaigns",
        "get_custom_fields",
        "get_user",
        "get_contacts",
        "get_products",
        "get_tasks",
        "get_deals",
        "get_deal_lost_reasons",
        "get_deal_stages",
        "get_deal_pipelines",
        "get_deal_sources",
        "put_deal",
    ]
    for method in expected_methods:
        assert (
            method in error_msg
        ), f"Expected abstract method {method} not found in TypeError"
