import pytest
from app.src.domain.entities.agent import Agent
from app.src.domain.entities.chat import Chat
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.entities.scheduler_config import SchedulerConfig
from app.src.domain.entities.template_configuration import TemplateConfiguration

# ── Agent ──────────────────────────────────────────────────────────────────


class TestAgent:
    def test_from_dict(self):
        data = {
            "id": "a1",
            "name": "Agent Name",
            "email": "agent@test.com",
            "key": "KEY_123",
        }
        agent = Agent.from_dict(data)
        assert agent.id == "a1"
        assert agent.name == "Agent Name"
        assert agent.email == "agent@test.com"
        assert agent.key == "KEY_123"

    def test_dataclass_equality(self):
        a1 = Agent(id="a1", name="A", email="a@a.com", key="KEY_123")
        a2 = Agent(id="a1", name="A", email="a@a.com", key="KEY_123")
        assert a1 == a2


# ── Chat ───────────────────────────────────────────────────────────────────


class TestChat:
    def test_from_dict_with_status(self):
        data = {"id": "chat-1", "status": "open"}
        chat = Chat.from_dict(data)
        assert chat.id == "chat-1"
        assert chat.status == "open"

    def test_from_dict_without_status(self):
        data = {"id": "chat-2"}
        chat = Chat.from_dict(data)
        assert chat.id == "chat-2"
        assert chat.status is None

    def test_from_dict_with_timestamps(self):
        from datetime import datetime
        now = datetime.now()
        data = {"id": "chat-3", "created_at": now, "updated_at": now}
        chat = Chat.from_dict(data)
        assert chat.created_at == now
        assert chat.updated_at == now

    def test_timestamps_default_none(self):
        data = {"id": "chat-4"}
        chat = Chat.from_dict(data)
        assert chat.created_at is None
        assert chat.updated_at is None


# ── DealStage ──────────────────────────────────────────────────────────────


class TestDealStage:
    def test_from_dict(self):
        data = {"id": "s1", "nickname": "SC"}
        stage = DealStage.from_dict(data)
        assert stage.id == "s1"
        assert stage.nickname == "SC"

    def test_from_dict_no_nickname(self):
        data = {"id": "s2"}
        stage = DealStage.from_dict(data)
        assert stage.id == "s2"
        assert stage.nickname is None


# ── Pipeline ───────────────────────────────────────────────────────────────


class TestPipeline:
    def test_from_dict(self):
        data = {
            "id": "pipe-1",
            "name": "Brasileiros em Mendoza",
            "deal_stages": [
                {"id": "s1", "nickname": "SC"},
                {"id": "s2", "nickname": "NR"},
            ],
        }
        pipeline = Pipeline.from_dict(data)
        assert pipeline.id == "pipe-1"
        assert pipeline.name == "Brasileiros em Mendoza"
        assert len(pipeline.deal_stages) == 2
        assert pipeline.deal_stages[0].id == "s1"

    def test_from_dict_no_stages(self):
        data = {"id": "pipe-2", "name": "Empty Pipeline"}
        pipeline = Pipeline.from_dict(data)
        assert pipeline.deal_stages == []

    def test_get_stage_by_nickname_found(self):
        pipeline = Pipeline(
            id="p1",
            name="Test",
            deal_stages=[
                DealStage(id="s1", nickname="SC"),
                DealStage(id="s2", nickname="NR"),
            ],
        )
        stage = pipeline.get_stage_by_nickname("SC")
        assert stage is not None
        assert stage.id == "s1"

    def test_get_stage_by_nickname_not_found(self):
        pipeline = Pipeline(id="p1", name="Test", deal_stages=[])
        assert pipeline.get_stage_by_nickname("CF") is None


# ── SchedulerConfig ────────────────────────────────────────────────────────


class TestSchedulerConfig:
    def test_from_dict(self):
        data = {"enabled": True, "cron": "*/5 * * * *", "batch_size": 50}
        config = SchedulerConfig.from_dict(data)
        assert config.enabled is True
        assert config.cron == "*/5 * * * *"
        assert config.batch_size == 50

    def test_dataclass_equality(self):
        c1 = SchedulerConfig(enabled=True, cron="* * * * *", batch_size=10)
        c2 = SchedulerConfig(enabled=True, cron="* * * * *", batch_size=10)
        assert c1 == c2


# ── TemplateConfiguration ──────────────────────────────────────────────────


class TestTemplateConfiguration:
    def test_from_dict(self):
        agent_data = {
            "id": "a1",
            "name": "Agent",
            "email": "agent@test.com",
            "key": "KEY_123",
        }
        data = {
            "phone": "+5512991344987",
            "template": "698b79c0ef5524949f9ae3cc",
            "write_enabled": False,
            "agent": agent_data,
        }
        config = TemplateConfiguration.from_dict("Pipeline A", data)
        assert config.phone == "+5512991344987"
        assert config.template == "698b79c0ef5524949f9ae3cc"
        assert config.write_enabled is False
        assert config.agent.id == "a1"
        assert config.agent.name == "Agent"
        assert config.agent.email == "agent@test.com"
        assert config.agent.key == "KEY_123"

    def test_from_dict_missing_agent_raises(self):
        data = {"phone": "code", "template": "id", "write_enabled": True}
        with pytest.raises(ValueError, match="Missing 'agent' configuration"):
            TemplateConfiguration.from_dict("Pipeline A", data)

    def test_to_dict(self):
        agent = Agent(
            id="a1", name="Agent", email="agent@test.com", key="KEY_123"
        )
        config = TemplateConfiguration(
            phone="code", template="id", write_enabled=False, agent=agent
        )
        result = config.to_dict()
        assert result == {"phone": "code", "template": "id", "write_enabled": False}
        assert "agent" not in result  # agent is NOT exposed in to_dict

    def test_write_enabled_defaults_to_false(self):
        data = {
            "phone": "code",
            "template": "id",
            "agent": {
                "id": "a1",
                "name": "A",
                "email": "a@a.com",
                "key": "KEY_123",
            },
        }
        config = TemplateConfiguration.from_dict("P", data)
        assert config.write_enabled is False

