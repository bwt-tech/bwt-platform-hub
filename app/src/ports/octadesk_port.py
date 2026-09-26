from abc import ABC, abstractmethod

from app.src.domain.entities.agent import Agent


class OctadeskPort(ABC):
    """Abstract interface for the Octadesk integration."""

    @abstractmethod
    def set_api_key(self, api_key):  # pragma: no cover
        pass

    @abstractmethod
    def check(self):  # pragma: no cover
        pass

    @abstractmethod
    def get_chats(self):  # pragma: no cover
        pass

    @abstractmethod
    def get_chats_in_progress(self, page, agent_id: str):  # pragma: no cover
        pass

    @abstractmethod
    def get_chats_by_phone(self, phone):  # pragma: no cover
        pass

    @abstractmethod
    def get_chat_numbers(self):  # pragma: no cover
        pass

    @abstractmethod
    def get_events(self, chat_id):  # pragma: no cover
        pass

    @abstractmethod
    def get_messages(self, chat_id):  # pragma: no cover
        pass

    @abstractmethod
    def post_contacts(self, email, name, phone):  # pragma: no cover
        pass

    @abstractmethod
    def get_contacts_by_phone(self, phone):  # pragma: no cover
        pass

    @abstractmethod
    def get_templates(self):  # pragma: no cover
        pass

    @abstractmethod
    def start_chat(self, contact: dict, configuration: dict):  # pragma: no cover
        pass

    @abstractmethod
    def notify_agent(
        self, chat_id: str, message: str, agent: Agent
    ):  # pragma: no cover
        pass
