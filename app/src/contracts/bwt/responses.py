from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator

from app.src.contracts.bwt.requests import DealLostReason, DealOrigin, DealStage  # noqa: F401


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

class PhoneContact(BaseModel):
    """Objeto Phone retornado nas respostas do BWT."""

    id: int
    country_code: str
    number: str


class AddressContact(BaseModel):
    """Objeto Address retornado nas respostas do BWT."""

    id: int
    info: str


# ---------------------------------------------------------------------------
# /auth/login/  response
# ---------------------------------------------------------------------------

class TokensResponse(BaseModel):
    """Par de tokens JWT retornado pelo login."""

    access: str
    refresh: Optional[str] = None


class LoginUserResponse(BaseModel):
    """Dados básicos do usuário retornados junto ao login."""

    id: int
    email: str
    name: Optional[str] = None


class LoginResponse(BaseModel):
    """Resposta completa de POST /auth/login/."""

    user: LoginUserResponse
    tokens: TokensResponse


# ---------------------------------------------------------------------------
# /auth/company-users/  response
# ---------------------------------------------------------------------------

class CompanyUserResponse(BaseModel):
    """Usuário interno da empresa (company user)."""

    id: int
    name: str
    is_active:bool


class CompanyUsersResponse(BaseModel):
    """Resposta paginada de GET /auth/company-users/."""

    count: int
    results: List[CompanyUserResponse]


# ---------------------------------------------------------------------------
# /sales/accounts/  response
# ---------------------------------------------------------------------------

class AccountResponse(BaseModel):
    """Dados de um Account retornado pelo BWT."""

    id: int
    name: str
    document: Optional[str] = None
    type: Optional[str] = None

class AccountsResponse(BaseModel):
    """Resposta de GET /sales/accounts.

    A API pode retornar uma lista direta ou um objeto paginado com 'results'.
    O model_validator normaliza ambos os formatos.
    """

    count: Optional[int] = None
    results: List[AccountResponse]

    @model_validator(mode="before")
    @classmethod
    def _normalize(cls, value: Any) -> Dict[str, Any]:
        if isinstance(value, list):
            return {"count": len(value), "results": value}
        return value


# ---------------------------------------------------------------------------
# /sales/accounts/{id}/contacts/  response
# ---------------------------------------------------------------------------

class AccountContactResponse(BaseModel):
    """Dados de um Contact vinculado a um Account."""

    id: int
    name: str
    email: Optional[str] = None
    document: Optional[str] = None
    phone: Optional[PhoneContact] = None
    address: Optional[AddressContact] = None
    zip_code: Optional[str] = None
    is_foreign: bool = False
    accounts: Optional[list[AccountResponse]] = None


class AccountContactsResponse(BaseModel):
    """Resposta paginada de GET /sales/accounts/{id}/contacts."""

    count: Optional[int] = None
    results: List[AccountContactResponse]


# ---------------------------------------------------------------------------
# /sales/deals/  response
# ---------------------------------------------------------------------------

class SimplifiedUserResponse(BaseModel):
    """Usuário simplificado retornado como 'responsible' no Deal."""

    id: int
    name: str


class ContactInfoResponse(BaseModel):
    """Sub-objeto retornado no campo 'contact_info' da resposta de POST /sales/deals/."""

    id: int
    name: str
    email: Optional[str] = None
    document: Optional[str] = None
    phone: Optional[PhoneContact] = None
    is_foreign: bool = False


class CreateDealResponse(BaseModel):
    """Payload retornado por POST /sales/deals/.

    A API BWT retorna objetos expandidos para 'contact', 'account' e
    'contact_info' neste endpoint — não IDs primitivos.
    """

    id: int
    contact: Optional[AccountContactResponse] = None
    account: Optional[AccountResponse] = None
    responsible: Optional[SimplifiedUserResponse] = None
    stage: Optional[DealStage] = None
    origin: Optional[DealOrigin] = None
    description: Optional[str] = None
    contact_info: Optional[ContactInfoResponse] = None
    categories: Optional[List[Any]] = None
    lost_reason: Optional[DealLostReason] = None
    lost_reason_notes: Optional[str] = None
    finished_at: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None


class DealQueryResponse(BaseModel):
    """Dados resumidos de um Deal retornado na listagem paginada."""

    id: int
    stage: Optional[DealStage] = None
    origin: Optional[DealOrigin] = None
    responsible: Optional[SimplifiedUserResponse] = None


class DealsQueryResponse(BaseModel):
    """Resposta paginada de GET /sales/deals/."""

    count: Optional[int] = None
    results: Optional[List[DealQueryResponse]] = None
    next: Optional[str] = None
