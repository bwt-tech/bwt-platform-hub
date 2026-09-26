from dataclasses import dataclass
from typing import Any


@dataclass
class Agent:
    id: str
    name: str
    email: str
    key: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            key=data["key"],
        )

