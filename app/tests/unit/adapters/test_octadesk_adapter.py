import httpx
import pytest
from app.src.adapters.outbounds.octadesk import OctadeskAdapter
from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.agent import Agent


@pytest.fixture
def adapter():
    return OctadeskAdapter(api_key="test_key", base_url="https://api.octadesk.example")


def test_octadesk_check_success(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/auth/check.*").mock(
        return_value=httpx.Response(200)
    )
    adapter.check()


def test_octadesk_fail_fast_on_error(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/auth/check.*").side_effect = (
        httpx.RequestError("Network error")
    )
    with pytest.raises(IntegrationError):
        adapter.check()


def test_octadesk_http_status_error(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/auth/check.*").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(IntegrationError):
        adapter.check()


def test_octadesk_get_chats(mock_octadesk_api, adapter, load_fixture):
    chats_data = load_fixture("octadesk", "chats")
    mock_octadesk_api.get(url__regex=r".*/chat\?.*").mock(
        return_value=httpx.Response(200, json=chats_data)
    )
    assert adapter.get_chats() == chats_data


def test_octadesk_get_chats_by_phone(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat\?.*phone.*").mock(
        return_value=httpx.Response(200, json={"chats": []})
    )
    assert adapter.get_chats_by_phone("+5511999999999") == {"chats": []}


def test_octadesk_get_chat_numbers(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat/numbers.*").mock(
        return_value=httpx.Response(200, json={"numbers": []})
    )
    assert adapter.get_chat_numbers() == {"numbers": []}


def test_octadesk_get_events(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat/chat_123/events.*").mock(
        return_value=httpx.Response(200, json={"events": []})
    )
    assert adapter.get_events("chat_123") == {"events": []}


def test_octadesk_get_messages(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat/chat_123/messages.*").mock(
        return_value=httpx.Response(200, json={"messages": []})
    )
    assert adapter.get_messages("chat_123") == {"messages": []}


def test_octadesk_post_contacts(mock_octadesk_api, adapter):
    mock_octadesk_api.post(url__regex=r".*/contacts.*").mock(
        return_value=httpx.Response(200, json={"id": "c_123"})
    )
    assert adapter.post_contacts("test@test.com", "Test", "11999999999") == {
        "id": "c_123"
    }


def test_octadesk_get_contacts_by_phone(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/contacts\?.*").mock(
        return_value=httpx.Response(200, json=[{"id": "c_123"}])
    )
    assert adapter.get_contacts_by_phone("11999999999") == [{"id": "c_123"}]


def test_octadesk_get_templates(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat/templates-message.*").mock(
        return_value=httpx.Response(200, json={"templates": []})
    )
    assert adapter.get_templates() == {"templates": []}


def test_octadesk_start_chat(mock_octadesk_api, adapter):
    mock_octadesk_api.post(url__regex=r".*/chat/send-template.*").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    contact = {"phone": "11999999999", "name": "Test User", "email": "test@test.com"}
    assert adapter.start_chat(contact, {"phone": "code", "template": "id"}) == {
        "success": True
    }


def test_octadesk_request_error_logging(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/auth/check.*").mock(
        return_value=httpx.Response(400, text="Error detail")
    )
    with pytest.raises(IntegrationError):
        adapter.check()


def test_octadesk_notify_agent(mock_octadesk_api, adapter):
    mock_octadesk_api.post(url__regex=r".*/chat/chat_123/messages.*").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    agent = Agent(
        id="agent-1", name="Test Agent", email="agent@test.com", key="KEY_TEST"
    )
    result = adapter.notify_agent("chat_123", "Hello!", agent)
    assert result == {"ok": True}


def test_octadesk_set_api_key(adapter):
    adapter.set_api_key("new_api_key")
    assert adapter.api_key == "new_api_key"


def test_octadesk_get_contacts(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/contacts$").mock(
        return_value=httpx.Response(200, json=[])
    )
    assert adapter.get_contacts() == []


def test_octadesk_get_contacts_by_id(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/contacts/c_123.*").mock(
        return_value=httpx.Response(200, json={"id": "c_123"})
    )
    assert adapter.get_contacts_by_id("c_123") == {"id": "c_123"}


def test_octadesk_get_chats_in_progress(mock_octadesk_api, adapter):
    mock_octadesk_api.get(url__regex=r".*/chat\?.*").mock(
        return_value=httpx.Response(200, json=[])
    )
    assert adapter.get_chats_in_progress(page=1, agent_id="agent-1") == []


