from dataclasses import dataclass, field
from typing import Any

from app.src.domain.entities.deal_stage import DealStage


@dataclass
class Pipeline:
    id: str
    name: str
    deal_stages: list[DealStage] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pipeline":
        return cls(
            id=data["id"],
            name=data["name"],
            deal_stages=[DealStage.from_dict(s) for s in data.get("deal_stages", [])],
        )

    def get_stage_by_nickname(self, nickname: str) -> DealStage | None:
        return next((s for s in self.deal_stages if s.nickname == nickname), None)
