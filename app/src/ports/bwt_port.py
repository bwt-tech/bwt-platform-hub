from abc import ABC, abstractmethod
from typing import Optional, Union

from app.src.contracts.bwt.requests import (
    AccountType,
    DealLostReason,
    DealOrigin,
    DealStage,
    PhonePayload,
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


class BWTPort(ABC):
    """Abstract interface for the BWT Platform integration."""

    @abstractmethod
    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> LoginResponse:  # pragma: no cover
        pass

    @abstractmethod
    def search_accounts(self, search_term: str) -> AccountsResponse:  # pragma: no cover
        pass

    @abstractmethod
    def get_account_contacts(
        self, account_id: Union[int, str]
    ) -> AccountContactsResponse:  # pragma: no cover
        pass

    @abstractmethod
    def get_contacts_by_phone(
        self, phone: str
    ) -> AccountContactsResponse: # pragma: no cover
        pass

    @abstractmethod
    def create_account(
        self,
        name: str,
        account_type: AccountType = AccountType.B2C,
    ) -> AccountResponse:  # pragma: no cover
        pass

    @abstractmethod
    def create_contact(
        self,
        account_id: Union[int, str],
        name: str,
        email: str,
        phone: Union[PhonePayload, str],
        document: Optional[str] = None,
        is_foreign: bool = False,
    ) -> AccountContactResponse:  # pragma: no cover
        pass

    @abstractmethod
    def get_deals(self, account_id:str, page:int = 1)-> DealsQueryResponse: # pragma: no cover
        pass

    @abstractmethod
    def get_deal(self, deal_id:str)-> CreateDealResponse: # pragma: no cover
        pass

    @abstractmethod
    def create_deal(
        self,
        contact_id: Union[int, str],
        account_id: Union[int, str],
        origin: DealOrigin = DealOrigin.WHATSAPP,
    ) -> CreateDealResponse:  # pragma: no cover
        pass

    @abstractmethod
    def update_deal_status(
        self,
        deal_id: Union[int, str],
        stage: DealStage,
        lost_reason: Optional[DealLostReason] = None,
        lost_reason_notes: Optional[str] = None,
    ) -> None:  # pragma: no cover
        pass

    @abstractmethod
    def get_company_users(self, search_term: str) -> CompanyUsersResponse:  # pragma: no cover
        pass

    @abstractmethod
    def set_deal_responsible(
        self, deal_id: Union[int, str], responsible_id: int
    ) -> None:  # pragma: no cover
        pass
