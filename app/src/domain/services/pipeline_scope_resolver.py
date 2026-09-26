from dataclasses import dataclass
from typing import Any

from app.src.domain.entities.agent_seller_configuration import AgentSellerConfiguration
from app.src.domain.entities.pipeline import Pipeline


@dataclass(frozen=True)
class PipelineScopeContext:
    pipeline: Pipeline
    scope: str


class PipelineScopeResolver:
    """Resolve pipeline e escopo BWT a partir da configuração do agente e tags do chat."""

    def resolve(
        self,
        agent_config: AgentSellerConfiguration,
        chat: dict[str, Any],
        pipelines: list[Pipeline],
    ) -> PipelineScopeContext | None:
        if agent_config.pipeline_name and agent_config.scope:
            pipeline = self._find_pipeline(pipelines, agent_config.pipeline_name)
            if pipeline is None:
                return None
            return PipelineScopeContext(
                pipeline=pipeline, scope=agent_config.scope
            )

        for binding in agent_config.pipelines_by_tag:
            if not self._chat_has_tag(chat, binding.tag_name):
                continue
            pipeline = self._find_pipeline(pipelines, binding.pipeline_name)
            if pipeline is None:
                continue
            return PipelineScopeContext(pipeline=pipeline, scope=binding.scope)

        return None

    @staticmethod
    def _find_pipeline(
        pipelines: list[Pipeline], pipeline_name: str
    ) -> Pipeline | None:
        return next((p for p in pipelines if p.name == pipeline_name), None)

    @staticmethod
    def __is_tag(tag, tag_name) -> bool:
        return ("name" in tag and tag.get("name") == tag_name) or (tag == tag_name)

    @staticmethod
    def _chat_has_tag(chat: dict[str, Any], tag_name: str) -> bool:
        tags = chat.get("tags", [])
        return any(PipelineScopeResolver.__is_tag(tag, tag_name) for tag in tags)
