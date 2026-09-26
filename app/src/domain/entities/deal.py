import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.src.domain.entities.contact import Contact


@dataclass
class Deal:
    deal_id: str
    name: str
    phone: str
    email: str
    deal_source_name: str
    deal_campaign_name: str
    id: str | None = None
    rdstation_id: str | None = None
    contact_id: str | None = None
    deal_status: str | None = None
    bwt_deal_id: int | None = None
    bwt_responsible_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, deal: dict[str, Any]) -> "Deal":
        cls.validate_prerequisites(deal)

        contacts = deal.get("contacts", [])
        if contacts:
            phones = contacts[0].get("phones")
            emails = contacts[0].get("emails")
        deal_id = deal.get("id")
        return cls(
            deal_id=deal_id,
            name=deal.get("name", "Unknown"),
            phone=cls.normalize_phone(phones[0]["phone"]),
            email=emails[0]["email"] if emails else "not_defined",
            deal_source_name=deal["deal_source"]["name"],
            deal_campaign_name=deal.get("campaign",{}).get("name",""),
            rdstation_id=deal_id,
            deal_status=(deal.get("deal_stage") or {}).get("nickname"),
        )

    @staticmethod
    def validate_prerequisites(deal: dict[str, Any]) -> None:
        contacts = deal.get("contacts", [])
        if contacts:
            phones = contacts[0].get("phones")
            if phones:
                return
        raise ValueError("Prerequisites not met")

    @staticmethod
    def normalize_phone(phone: str) -> str:
        return re.sub(r"\-|\s|\(|\)", "", phone)[-11:]

    def to_contact(self) -> Contact:
        return Contact(
            name=self.name,
            phone=self.phone,
            email=self.email,
            deal_id=self.deal_id,
        )
