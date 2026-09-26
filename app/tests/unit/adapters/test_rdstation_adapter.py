import httpx
import pytest
from app.src.adapters.outbounds.rdstation import RDStationAdapter
from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.pipeline import Pipeline


@pytest.fixture
def adapter():
    return RDStationAdapter(token="test_token")


def test_rdstation_http_status_error(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/users.*").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(IntegrationError):
        adapter.get_users()


def test_rdstation_request_error(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/users.*").side_effect = httpx.RequestError(
        "Network error"
    )
    with pytest.raises(IntegrationError):
        adapter.get_users()


def test_rdstation_get_users(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/users(\?|$)").mock(
        return_value=httpx.Response(200, json={"users": []})
    )
    assert adapter.get_users() == {"users": []}


def test_rdstation_get_campaigns(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/campaigns.*").mock(
        return_value=httpx.Response(200, json={"campaigns": []})
    )
    assert adapter.get_campaigns("1") == {"campaigns": []}


def test_rdstation_get_custom_fields(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/custom_fields.*").mock(
        return_value=httpx.Response(200, json={"fields": []})
    )
    assert adapter.get_custom_fields("1") == {"fields": []}


def test_rdstation_get_user(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/users/u1.*").mock(
        return_value=httpx.Response(200, json={"user": {}})
    )
    assert adapter.get_user("u1") == {"user": {}}


def test_rdstation_get_contacts(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/contacts.*").mock(
        return_value=httpx.Response(200, json={"contacts": []})
    )
    assert adapter.get_contacts("1") == {"contacts": []}
    assert adapter.get_contacts() == {"contacts": []}


def test_rdstation_get_products(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/products.*").mock(
        return_value=httpx.Response(200, json={"products": []})
    )
    assert adapter.get_products("1") == {"products": []}
    assert adapter.get_products() == {"products": []}


def test_rdstation_get_tasks(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/tasks.*").mock(
        return_value=httpx.Response(200, json={"tasks": []})
    )
    assert adapter.get_tasks("1") == {"tasks": []}
    assert adapter.get_tasks() == {"tasks": []}


def test_rdstation_get_deals(mock_rdstation_api, adapter, load_fixture):
    deals_data = load_fixture("rdstation", "deals")
    mock_rdstation_api.get(url__regex=r".*/deals(\?token.*|$)").mock(
        return_value=httpx.Response(200, json=deals_data)
    )
    assert adapter.get_deals("1", "s1") == deals_data
    assert adapter.get_deals() == deals_data


def test_rdstation_get_deal_lost_reasons(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/deal_lost_reasons.*").mock(
        return_value=httpx.Response(200, json={"reasons": []})
    )
    assert adapter.get_deal_lost_reasons("1") == {"reasons": []}
    assert adapter.get_deal_lost_reasons(None) == {"reasons": []}


def test_rdstation_get_deal_stages(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/deal_stages.*").mock(
        return_value=httpx.Response(200, json={"stages": []})
    )
    assert adapter.get_deal_stages("1") == {"stages": []}
    assert adapter.get_deal_stages() == {"stages": []}


def test_rdstation_get_deal_pipelines(mock_rdstation_api, adapter):
    pipeline_data = [
        {
            "id": "p1",
            "name": "Pipeline A",
            "deal_stages": [{"id": "s1", "nickname": "SC"}],
        }
    ]
    mock_rdstation_api.get(url__regex=r".*/deal_pipelines.*").mock(
        return_value=httpx.Response(200, json=pipeline_data)
    )
    result = adapter.get_deal_pipelines("1")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Pipeline)
    assert result[0].id == "p1"
    assert result[0].name == "Pipeline A"
    assert result[0].deal_stages[0].id == "s1"

    result_no_page = adapter.get_deal_pipelines()
    assert isinstance(result_no_page, list)


def test_rdstation_get_deal_sources(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/deal_sources.*").mock(
        return_value=httpx.Response(200, json={"sources": []})
    )
    assert adapter.get_deal_sources("1") == {"sources": []}
    assert adapter.get_deal_sources() == {"sources": []}


def test_rdstation_put_deal(mock_rdstation_api, adapter):
    mock_rdstation_api.put(url__regex=r".*/deals/d1.*").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    assert adapter.put_deal("d1", "s1") == {"success": True}
    assert adapter.put_deal("d1", "s1", seller_name="Seller", source="Octadesk") == {"success": True}


def test_rdstation_get_deal(mock_rdstation_api, adapter):
    mock_rdstation_api.get(url__regex=r".*/deals/d1.*").mock(
        return_value=httpx.Response(200, json={"id": "d1"})
    )
    assert adapter.get_deal("d1") == {"id": "d1"}


def test_rdstation_post_deal(mock_rdstation_api, adapter):
    mock_rdstation_api.post(url__regex=r".*/deals\?.*").mock(
        return_value=httpx.Response(200, json={"id": "d2"})
    )
    assert adapter.post_deal("s1", "Contact", "11999998888") == {"id": "d2"}

