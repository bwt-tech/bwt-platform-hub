import pytest

from app.src.domain.entities.agent_seller_configuration import AgentSellerConfiguration
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.services.pipeline_scope_resolver import PipelineScopeResolver


PIPELINES = [
    Pipeline(
        id="p-1",
        name="Brasileiros em Mendoza",
        deal_stages=[DealStage(id="s-1", nickname="EPV")],
    ),
    Pipeline(
        id="p-2",
        name="Brasileiros em Salta",
        deal_stages=[DealStage(id="s-2", nickname="EPV")],
    ),
    Pipeline(
        id="p-3",
        name="Serra Gaúcha",
        deal_stages=[DealStage(id="s-3", nickname="EPV")],
    ),
]


def test_resolve_fixed_pipeline_and_scope():
    config = AgentSellerConfiguration.from_dict(
        {
            "agent": {"id": "agent-1"},
            "seller": "Andrele",
            "pipeline": "Brasileiros em Mendoza",
            "scope": "SBM",
        }
    )
    resolver = PipelineScopeResolver()

    context = resolver.resolve(config, chat={}, pipelines=PIPELINES)

    assert context is not None
    assert context.pipeline.name == "Brasileiros em Mendoza"
    assert context.scope == "SBM"


def test_resolve_pipeline_by_tag():
    config = AgentSellerConfiguration.from_dict(
        {
            "agent": {"id": "agent-2"},
            "seller": "Maria Castro",
            "pipelines_by_tag": [
                {"tag_name": "Salta", "pipeline": "Brasileiros em Salta", "scope": "SBS"},
                {"tag_name": "1 - Serra Gaúcha", "pipeline": "Serra Gaúcha", "scope": "SG"},
            ],
        }
    )
    chat = {"tags": [{"name": "Salta"}]}
    resolver = PipelineScopeResolver()

    context = resolver.resolve(config, chat, PIPELINES)

    assert context is not None
    assert context.pipeline.name == "Brasileiros em Salta"
    assert context.scope == "SBS"


def test_resolve_returns_none_when_pipeline_not_found():
    config = AgentSellerConfiguration.from_dict(
        {
            "agent": {"id": "agent-1"},
            "seller": "Andrele",
            "pipeline": "Pipeline Inexistente",
            "scope": "SBM",
        }
    )
    resolver = PipelineScopeResolver()

    assert resolver.resolve(config, chat={}, pipelines=PIPELINES) is None


def test_resolve_skips_tag_when_pipeline_not_found():
    config = AgentSellerConfiguration.from_dict(
        {
            "agent": {"id": "agent-2"},
            "seller": "Maria Castro",
            "pipelines_by_tag": [
                {
                    "tag_name": "Salta",
                    "pipeline": "Pipeline Inexistente",
                    "scope": "SBS",
                },
                {
                    "tag_name": "Salta",
                    "pipeline": "Brasileiros em Salta",
                    "scope": "SBS",
                },
            ],
        }
    )
    chat = {"tags": [{"name": "Salta"}]}
    resolver = PipelineScopeResolver()

    context = resolver.resolve(config, chat, PIPELINES)

    assert context is not None
    assert context.pipeline.name == "Brasileiros em Salta"

    config = AgentSellerConfiguration.from_dict(
        {
            "agent": {"id": "agent-2"},
            "seller": "Maria Castro",
            "pipelines_by_tag": [
                {"tag_name": "Salta", "pipeline": "Brasileiros em Salta", "scope": "SBS"},
            ],
        }
    )
    chat = {"tags": [{"name": "Outra Tag"}]}
    resolver = PipelineScopeResolver()

    assert resolver.resolve(config, chat, PIPELINES) is None
