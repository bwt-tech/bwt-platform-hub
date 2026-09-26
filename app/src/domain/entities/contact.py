from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Contact:
    name: str
    phone: str
    email: str
    deal_id: Optional[str] = None
    chat_response: dict | None = None
    id: str | None = None
    octadesk_id: str | None = None
    rdstation_id: str | None = None
    bwt_account_id: int | None = None
    bwt_contact_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "deal_id": self.deal_id,
        }
        if self.chat_response is not None:
            data["chat_response"] = self.chat_response
        return data
