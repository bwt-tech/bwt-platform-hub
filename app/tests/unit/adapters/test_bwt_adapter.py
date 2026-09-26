import httpx
import pytest
from pydantic import ValidationError
import json

from app.src.adapters.outbounds.bwt import BWTAdapter
from app.src.contracts.bwt.requests import AccountType, DealOrigin, DealStage, PhonePayload
from app.src.contracts.bwt.responses import (
    AccountContactResponse,
    AccountContactsResponse,
    DealsQueryResponse,
    DealQueryResponse,
    AccountResponse,
    AccountsResponse,
    CompanyUsersResponse,
    CreateDealResponse,
    LoginResponse,
)
from app.src.core.exceptions import IntegrationError

BWT_BASE_URL = "https://api.homolog.brasileiroswinetours.com.br"


@pytest.fixture
def bwt_adapter():
    return BWTAdapter(
        base_url=BWT_BASE_URL,
        email="miguel@b2bit.company",
        password="b2bit123",
        scope="b2bit",
        token="test_jwt_token",
    )


def test_bwt_login_missing_credentials():
    adapter = BWTAdapter(email="", password="")
    with pytest.raises(IntegrationError, match="Email and password are required"):
        adapter.login()


def test_bwt_login_success(mock_bwt_api):
    mock_bwt_api.post("/auth/login/").mock(
        return_value=httpx.Response(
            200,
            json={
                "user": {"id": 3, "email": "miguel@b2bit.company"},
                "tokens": {"access": "new_access_token", "refresh": "refresh_token"},
            },
        )
    )
    adapter = BWTAdapter(
        base_url=BWT_BASE_URL, email="miguel@b2bit.company", password="b2bit123"
    )
    res = adapter.login()
    assert isinstance(res, LoginResponse)
    assert res.tokens.access == "new_access_token"
    assert adapter._token == "new_access_token"


def test_bwt_login_no_access_token(mock_bwt_api):
    mock_bwt_api.post("/auth/login/").mock(
        return_value=httpx.Response(200, json={"tokens": {}})
    )
    adapter = BWTAdapter(
        base_url=BWT_BASE_URL, email="miguel@b2bit.company", password="b2bit123"
    )
    with pytest.raises(IntegrationError, match="no access token was returned"):
        adapter.login()


def test_bwt_http_status_error(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/accounts/?search=Venancio").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    with pytest.raises(IntegrationError, match="HTTP Status error: 404"):
        bwt_adapter.search_accounts("Venancio")


def test_bwt_request_error(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/accounts/?search=Venancio").side_effect = httpx.RequestError(
        "Connection error"
    )
    with pytest.raises(IntegrationError, match="HTTP Request failed: Connection error"):
        bwt_adapter.search_accounts("Venancio")


def test_bwt_empty_response(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/auth/company-users/?fields=id,name,is_active&search=Miguel").mock(
        return_value=httpx.Response(200, text="")
    )
    with pytest.raises(ValidationError):
        bwt_adapter.get_company_users("Miguel")


def test_bwt_request_custom_headers(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/auth/company-users/?fields=id,name,is_active&search=test").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )
    raw = bwt_adapter._request(
        "GET",
        "/auth/company-users/?fields=id,name,is_active&search=test",
        headers={"X-Custom-Header": "custom"},
    )
    assert raw == {"count": 0, "results": []}


def test_bwt_auto_login_on_request(mock_bwt_api):
    mock_bwt_api.post("/auth/login/").mock(
        return_value=httpx.Response(
            200, json={"user": {"id": 1, "email": "x@x.com"}, "tokens": {"access": "auto_token"}}
        )
    )
    mock_bwt_api.get("/auth/company-users/?fields=id,name,is_active&search=auto").mock(
        return_value=httpx.Response(200, json={"count": 1, "results": [{"id": 1, "name": "Auto", "is_active": True}]})
    )
    adapter = BWTAdapter(
        base_url=BWT_BASE_URL, email="miguel@b2bit.company", password="b2bit123"
    )
    res = adapter.get_company_users("auto")
    assert adapter._token == "auto_token"
    assert isinstance(res, CompanyUsersResponse)
    assert res.count == 1


def test_bwt_search_accounts(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/accounts/?search=Venancio").mock(
        return_value=httpx.Response(200, json=[{"id": 27, "name": "M Venancio"}])
    )
    res = bwt_adapter.search_accounts("Venancio")
    assert isinstance(res, AccountsResponse)
    assert res.results[0].id == 27
    assert res.results[0].name == "M Venancio"


def test_bwt_create_account(mock_bwt_api, bwt_adapter):
    mock_bwt_api.post("/sales/accounts/").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 27,
                "name": "M Venancio",
                "document": None,
                "type": "B2C",
                "net_fare_percentage": "0.00",
            },
        )
    )
    res = bwt_adapter.create_account("M Venancio", AccountType.B2C)
    assert isinstance(res, AccountResponse)
    assert res.id == 27
    assert res.name == "M Venancio"


def test_bwt_create_contact_phone_string(mock_bwt_api, bwt_adapter):
    mock_bwt_api.post("/sales/accounts/27/contacts/").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 35,
                "name": "M Venancio",
                "email": "newemail@email.com",
                "document": "111111",
                "phone": {"id": 182, "country_code": "+55", "number": "11222223333"},
                "account": {"id": 27, "name": "M Venancio"},
            },
        )
    )
    res = bwt_adapter.create_contact(
        account_id=27,
        name="M Venancio",
        email="newemail@email.com",
        phone="11222223333",
    )
    assert isinstance(res, AccountContactResponse)
    assert res.id == 35
    assert res.email == "newemail@email.com"


def test_bwt_create_contact_phone_dict(mock_bwt_api, bwt_adapter):
    from app.src.contracts.bwt.requests import PhonePayload

    mock_bwt_api.post("/sales/accounts/27/contacts/").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 35,
                "name": "M Venancio",
                "email": "newemail@email.com",
                "phone": {"id": 182, "country_code": "+55", "number": "11222223333"},
            },
        )
    )
    res = bwt_adapter.create_contact(
        account_id=27,
        name="M Venancio",
        email="newemail@email.com",
        phone=PhonePayload(country_code="+55", number="11222223333"),
    )
    assert isinstance(res, AccountContactResponse)
    assert res.id == 35


def test_bwt_create_deal(mock_bwt_api, bwt_adapter):
    mock_bwt_api.post("/sales/deals/").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 47,
                "contact": {
                    "id": 35,
                    "name": "Test Contact",
                    "email": "test@example.com",
                    "document": "-",
                    "phone": {"id": 10, "country_code": "+55", "number": "11999999999"},
                    "address": None,
                    "zip_code": None,
                    "is_foreign": False,
                },
                "account": {
                    "id": 27,
                    "name": "Test Account",
                    "document": None,
                    "type": "B2C",
                },
                "responsible": {"id": 103, "name": "BWT | Tecnologia"},
                "stage": "NEW_DEAL",
                "origin": "WHATSAPP",
                "description": None,
                "contact_info": {
                    "id": 35,
                    "name": "Test Contact",
                    "email": "test@example.com",
                    "document": "-",
                    "phone": {"id": 10, "country_code": "+55", "number": "11999999999"},
                    "is_foreign": False,
                },
                "categories": [],
                "lost_reason": None,
                "lost_reason_notes": None,
                "finished_at": None,
                "created": "2026-08-07T17:05:14.790461-03:00",
                "modified": "2026-08-07T17:05:14.790461-03:00",
            },
        )
    )
    res = bwt_adapter.create_deal(contact_id=35, account_id=27, origin=DealOrigin.WHATSAPP)
    assert isinstance(res, CreateDealResponse)
    assert res.id == 47
    assert res.stage == DealStage.NEW_DEAL
    assert res.contact.id == 35
    assert res.account.id == 27


def test_bwt_update_deal_status(mock_bwt_api, bwt_adapter):
    route = mock_bwt_api.post("/sales/deals/47/update-deal-status/").mock(
        return_value=httpx.Response(
            200, json={"id": 47, "stage": "CONTACTED"}
        )
    )
    bwt_adapter.update_deal_status(deal_id=47, stage=DealStage.CONTACTED)

    sent_payload = json.loads(route.calls.last.request.content)
    assert sent_payload == {"stage": "CONTACTED"}


def test_bwt_get_company_users(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/auth/company-users/?fields=id,name,is_active&search=Miguel").mock(
        return_value=httpx.Response(
            200, json={"count": 1, "results": [{"id": 3, "name": "Miguel", "is_active": True}]}
        )
    )
    res = bwt_adapter.get_company_users("Miguel")
    assert isinstance(res, CompanyUsersResponse)
    assert res.count == 1
    assert res.results[0].name == "Miguel"
    assert res.results[0].is_active == True
    assert res.results[0].id == 3


def test_bwt_set_deal_responsible(mock_bwt_api, bwt_adapter):
    mock_bwt_api.post("/sales/deals/47/set-responsible/").mock(
        return_value=httpx.Response(
            200, json={"id": 47, "responsible": {"id": 61, "name": "João Elias"}}
        )
    )
    bwt_adapter.set_deal_responsible(deal_id=47, responsible_id=61)

def test_bwt_get_deals(mock_bwt_api, bwt_adapter):
    payload = """{
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
            "id": 49,
            "account": {
                "id": 28,
                "name": "Rosilene L",
                "document": null,
                "type": "B2C"
            },
            "responsible": {
                "id": 4,
                "name": "Supervisor Vendas",
                "avatar": null
            },
            "stage": "NEW_DEAL",
            "origin": "WHATSAPP",
            "description": null,
            "created": "2026-07-31T16:42:55.675145-03:00",
            "modified": "2026-07-31T16:42:55.675145-03:00",
            "contact_info": {
                "id": 37,
                "name": "Rosilene L",
                "email": "4499117670@octachat.com",
                "document": null,
                "phone": {
                "id": 184,
                "country_code": "+55",
                "number": "4499117670"
                },
                "is_foreign": false
            },
            "categories": [],
            "lost_reason": null,
            "lost_reason_notes": null,
            "finished_at": null
            }
        ]
        }"""

    mock_bwt_api.get("/sales/deals/?account=123&page=1").mock(
        return_value=httpx.Response(
            200, json=json.loads(payload)
        )
    )
    res = bwt_adapter.get_deals(account_id="123", page=1)
    assert isinstance(res, DealsQueryResponse)
    assert res.count == 1
    assert isinstance(res.results[0], DealQueryResponse)
    deal = res.results[0]
    assert deal.stage == DealStage.NEW_DEAL
    assert deal.origin == DealOrigin.WHATSAPP


def test_bwt_get_account_contacts(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/accounts/27/contacts/").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )
    res = bwt_adapter.get_account_contacts(27)
    assert isinstance(res, AccountContactsResponse)


def test_bwt_get_contacts_by_phone(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/contacts/?search=11999998888").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )
    res = bwt_adapter.get_contacts_by_phone("11999998888")
    assert isinstance(res, AccountContactsResponse)


def test_bwt_get_contacts(mock_bwt_api, bwt_adapter):
    mock_bwt_api.get("/sales/accounts/?search=test").mock(
        return_value=httpx.Response(200, json={"count": 0, "results": []})
    )
    res = bwt_adapter.get_contacts("test")
    assert isinstance(res, AccountContactsResponse)


