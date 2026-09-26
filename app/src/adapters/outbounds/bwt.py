from typing import Any, Dict, Optional, Union

import httpx
from loguru import logger

import curlify3

from app.src.config.settings import settings
from app.src.contracts.bwt.requests import (
    AccountType,
    CreateAccountRequest,
    CreateContactRequest,
    CreateDealRequest,
    DealLostReason,
    DealOrigin,
    DealStage,
    LoginRequest,
    PhonePayload,
    SetDealResponsibleRequest,
    UpdateDealStatusRequest,
)
from app.src.contracts.bwt.responses import (
    AccountContactResponse,
    AccountContactsResponse,
    AccountResponse,
    AccountsResponse,
    CompanyUsersResponse,
    CreateDealResponse,
    DealsQueryResponse,
    LoginResponse,
)
from app.src.core.exceptions import IntegrationError
from app.src.ports.bwt_port import BWTPort


class BWTAdapter(BWTPort):
    """Adapter for the BWT Platform REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        scope: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.bwt_url).rstrip("/")
        self.email = email or settings.bwt_email
        self.password = password or settings.bwt_password
        self.scope = scope
        self._token = token

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json; version=v1_web",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        if endpoint != "/auth/login/" and not self._token:
            self.login()

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            logger.info(f"BWT: Requesting {method} to {url}: {kwargs}")
            response = httpx.request(method, url, headers=headers, **kwargs)
            logger.info(f"BWT: response from {url}: CODE: {response.status_code}, payload: {response.text}")
            if response.status_code>=400:
                logger.error(f"BWT API ERROR: {response.text}")
                response.raise_for_status()
            if response.text:
                return response.json()
            return {}
        except httpx.RequestError as exc:
            logger.error(f"BWT API RequestError: {exc}")
            raise IntegrationError(f"HTTP Request failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            curl_command = curlify3.to_curl(exc.response.request)

            logger.error(
                f"BWT API HTTPStatusError: {exc.response.status_code} - {exc.response.text}"
            )
            logger.error(f"CURL: {curl_command}")
            raise IntegrationError(
                f"HTTP Status error: {exc.response.status_code}"
            ) from exc

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> LoginResponse:
        login_email = email or self.email
        login_password = password or self.password
        login_scope = scope or self.scope

        if not login_email or not login_password:
            raise IntegrationError("Email and password are required for BWT authentication.")

        request = LoginRequest(
            email=login_email,
            password=login_password,
            scope=login_scope,
        )

        raw = self._request("POST", "/auth/login/", json=request.model_dump(exclude_none=True))

        tokens = raw.get("tokens", {})
        access_token = tokens.get("access")
        if not access_token:
            raise IntegrationError("BWT authentication succeeded but no access token was returned.")

        self._token = access_token
        return LoginResponse.model_validate(raw)

    def get_company_users(self, search_term: str) -> CompanyUsersResponse:
        raw = self._request(
            "GET", f"/auth/company-users/?fields=id,name,is_active&search={search_term}"
        )
        return CompanyUsersResponse.model_validate(raw)

    # ------------------------------------------------------------------
    # Accounts
    # ------------------------------------------------------------------

    def search_accounts(self, search_term: str) -> AccountsResponse:
        raw = self._request("GET", f"/sales/accounts/?search={search_term}")
        return AccountsResponse.model_validate(raw)

    def get_account_contacts(
        self, account_id: Union[int, str]
    ) -> AccountContactsResponse:
        raw = self._request("GET", f"/sales/accounts/{account_id}/contacts/")
        return AccountContactsResponse.model_validate(raw)

    def get_contacts_by_phone(
        self, phone: str
    ) -> AccountContactsResponse:
        raw = self._request("GET", f"/sales/contacts/?search={phone}")
        return AccountContactsResponse.model_validate(raw)

    def get_contacts(
        self, search: str
    ) -> AccountContactsResponse:
        raw = self._request("GET", f"/sales/accounts/?search={search}")
        return AccountContactsResponse.model_validate(raw)

    def create_account(
        self,
        name: str,
        account_type: AccountType = AccountType.B2C,
    ) -> AccountResponse:
        request = CreateAccountRequest(name=name, type=account_type)
        raw = self._request("POST", "/sales/accounts/", json=request.model_dump())
        return AccountResponse.model_validate(raw)

    def create_contact(
        self,
        account_id: Union[int, str],
        name: str,
        email: str,
        phone: Union[PhonePayload, str],
        is_foreign: bool = False,
    ) -> AccountContactResponse:
        phone_payload = (
            PhonePayload(country_code="+55", number=phone)
            if isinstance(phone, str)
            else phone
        )

        request = CreateContactRequest(
            name=name,
            email=email,
            phone=phone_payload,
            is_foreign=is_foreign,
        )

        raw = self._request(
            "POST",
            f"/sales/accounts/{account_id}/contacts/",
            json=request.model_dump(exclude_none=True),
        )
        return AccountContactResponse.model_validate(raw)

    # ------------------------------------------------------------------
    # Deals
    # ------------------------------------------------------------------

    def get_deals(self, account_id:str, page:int = 1)-> DealsQueryResponse:
        raw = self._request("GET", f"/sales/deals/?account={account_id}&page={page}")
        return DealsQueryResponse.model_validate(raw)

    def get_deal(self, deal_id:str)-> CreateDealResponse: # pragma: no cover
        raw = self._request("GET", f"/sales/deals/{deal_id}/")
        return CreateDealResponse.model_validate(raw)

    def create_deal(
        self,
        contact_id: Union[int, str],
        account_id: Union[int, str],
        origin: DealOrigin = DealOrigin.WHATSAPP,
    ) -> CreateDealResponse:
        request = CreateDealRequest(
            contact=str(contact_id),
            account=str(account_id),
            origin=origin,
        )
        raw = self._request("POST", "/sales/deals/", json=request.model_dump())
        return CreateDealResponse.model_validate(raw)


    def update_deal_status(
        self,
        deal_id: str,
        stage: DealStage
    ) -> None:
        request = UpdateDealStatusRequest(
            stage=stage
        )
        self._request(
            "POST",
            f"/sales/deals/{deal_id}/update-deal-status/",
            json=request.model_dump(mode='json'),
        )

    def set_deal_responsible(
        self, deal_id: str,  responsible_id: int
    ) -> None:
        request = SetDealResponsibleRequest(responsible=responsible_id)
        self._request(
            "POST",
            f"/sales/deals/{deal_id}/set-responsible/",
            json=request.model_dump(mode='json'),
        )
