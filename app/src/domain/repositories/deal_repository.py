from abc import ABC, abstractmethod

from app.src.domain.entities.deal import Deal


class DealRepositoryPort(ABC):
    @abstractmethod
    def save(self, deal: Deal) -> Deal:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_id(self, deal_id: str) -> Deal | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_rdstation_id(self, rdstation_id: str) -> Deal | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_contact_id(self, contact_id: str) -> Deal | None:
        pass  # pragma: no cover

    def find_by_contact_id_and_rd_station_id(self, contact_id: str, rdstation_id: str) -> Deal | None:
        pass  # pragma: no cover

    @abstractmethod
    def find_by_bwt_deal_id(self, bwt_deal_id: int) -> Deal | None:
        pass  # pragma: no cover
