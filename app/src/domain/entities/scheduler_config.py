from dataclasses import dataclass
from typing import Any


@dataclass
class SchedulerConfig:
    enabled: bool
    cron: str
    batch_size: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchedulerConfig":
        return cls(
            enabled=data["enabled"],
            cron=data["cron"],
            batch_size=data["batch_size"],
        )
