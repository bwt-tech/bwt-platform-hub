from dataclasses import dataclass
from typing import Any


@dataclass
class DealStage:
    id: str
    nickname: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DealStage":
        return cls(
            id=data["id"],
            nickname=data.get("nickname"),
        )
