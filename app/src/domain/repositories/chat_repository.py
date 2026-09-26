from abc import ABC, abstractmethod

from app.src.domain.entities.chat import Chat


class ChatRepositoryPort(ABC):
    @abstractmethod
    def save(self, chat: Chat) -> Chat:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_id(self, chat_id: str) -> Chat | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_octadesk_id(self, octadesk_id: str) -> Chat | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_contact_id(self, contact_id: str) -> Chat | None:
        pass # pragma: no cover
