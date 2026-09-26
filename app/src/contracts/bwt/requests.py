from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Enums — valores definidos pelo contrato OpenAPI
# ---------------------------------------------------------------------------

class AccountType(str, Enum):
    B2C = "B2C"
    AGENCY = "AGENCY"
    COMPANY = "COMPANY"


class DealOrigin(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    WHATSAPP = "WHATSAPP"
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    WEBSITE = "WEBSITE"
    APPLICATION = "APPLICATION"
    OTHER = "OTHER"


class DealStage(str, Enum):
    NEW_DEAL = "NEW_DEAL"
    CONTACTED = "CONTACTED"
    QUOTE = "QUOTE"
    QUOTE_SENT = "QUOTE_SENT"
    FINISHED = "FINISHED"
    LOST = "LOST"


class DealLostReason(str, Enum):
    NOT_INTERESTED = "NOT_INTERESTED"
    FUTURE_INTEREST = "FUTURE_INTEREST"
    PROPOSAL_DECLINED = "PROPOSAL_DECLINED"


# ---------------------------------------------------------------------------
# Shared value objects
# ---------------------------------------------------------------------------

class PhonePayload(BaseModel):
    """Objeto Phone enviado nas requisições ao BWT (POST /sales/accounts/{id}/contacts/)."""

    country_code: str = "+55"
    """Código do país — ex.: '+55'. Máx. 3 caracteres."""

    number: str
    """Número local sem código do país — ex.: '11999998888'. Máx. 12 caracteres."""


# ---------------------------------------------------------------------------
# /auth/login/  (POST)
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Payload de autenticação — POST /auth/login/."""

    email: str
    password: str
    scope: Optional[str] = None


# ---------------------------------------------------------------------------
# /sales/accounts/  (POST)
# ---------------------------------------------------------------------------

class CreateAccountRequest(BaseModel):
    """Payload de criação de Account — POST /sales/accounts/."""

    name: str
    type: AccountType = AccountType.B2C


# ---------------------------------------------------------------------------
# /sales/accounts/{account_id}/contacts/  (POST)
# ---------------------------------------------------------------------------

class CreateContactRequest(BaseModel):
    """Payload de criação de Contact vinculado a um Account — POST /sales/accounts/{id}/contacts/."""

    name: str
    email: str
    phone: PhonePayload
    document: Optional[str] = "-"
    is_foreign: bool = False


# ---------------------------------------------------------------------------
# /sales/deals/  (POST)
# ---------------------------------------------------------------------------

class CreateDealRequest(BaseModel):
    """Payload de criação de Deal — POST /sales/deals/."""

    contact: str
    """ID do Contact (enviado como string conforme comportamento do adapter)."""

    account: str
    """ID do Account (enviado como string conforme comportamento do adapter)."""

    origin: DealOrigin = DealOrigin.WHATSAPP


# ---------------------------------------------------------------------------
# /sales/deals/{id}/update-deal-status/  (POST)
# ---------------------------------------------------------------------------

class UpdateDealStatusRequest(BaseModel):
    """Payload de atualização de estágio do Deal — POST /sales/deals/{id}/update-deal-status/.

    ``lost_reason`` e ``lost_reason_notes`` são obrigatórios quando ``stage == DealStage.LOST``.
    """

    stage: DealStage


# ---------------------------------------------------------------------------
# /sales/deals/{id}/set-responsible/  (POST)
# ---------------------------------------------------------------------------

class SetDealResponsibleRequest(BaseModel):
    """Payload para atribuir responsável a um Deal — POST /sales/deals/{id}/set-responsible/."""

    responsible: int
    """ID do CompanyUser que passará a ser responsável pelo Deal."""
