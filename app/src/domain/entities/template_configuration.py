from dataclasses import dataclass
from typing import Any

from app.src.domain.entities.agent import Agent


@dataclass
class TemplateConfiguration:
    phone: str
    template: str
    write_enabled: bool
    agent: Agent

    @classmethod
    def from_dict(
        cls, pipeline_name: str, data: dict[str, Any]
    ) -> "TemplateConfiguration":
        agent_data = data.get("agent")
        if not agent_data:
            raise ValueError(
                f"Missing 'agent' configuration for pipeline '{pipeline_name}' in templates.yaml"
            )
        return cls(
            phone=data["phone"],
            template=data["template"],
            write_enabled=data.get("write_enabled", False),
            agent=Agent.from_dict(agent_data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Returns a dict representation compatible with the Octadesk adapter."""
        return {
            "phone": self.phone,
            "template": self.template,
            "write_enabled": self.write_enabled,
        }
