from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TagPipelineBinding:
    tag_name: str
    pipeline_name: str
    scope: str


@dataclass(frozen=True)
class AgentSellerConfiguration:
    agent_id: str | None
    seller: str
    supervisor: str
    pipeline_name: str | None = None
    scope: str | None = None
    pipelines_by_tag: tuple[TagPipelineBinding, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentSellerConfiguration":
        agent = data.get("agent", {})
        agent_id = None
        if agent:
            agent_id = agent.get("id")
        seller = data.get("seller", "")
        supervisor = data.get("supervisor", "")
        if "pipelines_by_tag" in data:
            bindings = tuple(
                TagPipelineBinding(
                    tag_name=entry["tag_name"],
                    pipeline_name=entry["pipeline"],
                    scope=entry["scope"],
                )
                for entry in data["pipelines_by_tag"]
            )
            return cls(agent_id=agent_id, seller=seller, supervisor=supervisor, pipelines_by_tag=bindings)

        return cls(
            agent_id=agent_id,
            seller=seller,
            supervisor=supervisor,
            pipeline_name=data.get("pipeline"),
            scope=data.get("scope"),
        )

    @property
    def has_agent_id(self) -> bool:
        return bool(self.agent_id)
