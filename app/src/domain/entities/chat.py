from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Chat:
    id: str
    status: str | None = None
    octadesk_id: str | None = None
    channel: str | None = None
    contact_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chat":
        return cls(
            id=data["id"],
            status=data.get("status"),
            octadesk_id=data.get("octadesk_id") or data["id"],
            channel=data.get("channel"),
            contact_id=data.get("contact_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
