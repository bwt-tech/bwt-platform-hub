from abc import ABC, abstractmethod

from app.src.domain.entities.contact import Contact


class ContactRepositoryPort(ABC):
    @abstractmethod
    def save(self, contact: Contact) -> Contact:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_id(self, contact_id: str) -> Contact | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_phone(self, phone: str) -> Contact | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_email(self, email: str) -> Contact | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_octadesk_id(self, octadesk_id: str) -> Contact | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_bwt_contact_id(self, bwt_contact_id: int) -> Contact | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_bwt_account_id(self, bwt_account_id: int) -> Contact | None:
        pass  # pragma: no cover
