from abc import ABC, abstractmethod
from typing import Optional

from app.src.domain.entities.pipeline import Pipeline


class RDStationPort(ABC):
    """Abstract interface for the RDStation integration."""

    @abstractmethod
    def get_users(self):  # pragma: no cover
        pass

    @abstractmethod
    def get_campaigns(self, page):  # pragma: no cover
        pass

    @abstractmethod
    def get_custom_fields(self, page):  # pragma: no cover
        pass

    @abstractmethod
    def get_user(self, id):  # pragma: no cover
        pass

    @abstractmethod
    def get_contacts(self, page_id: Optional[str] = None, phone: Optional[str] = None, start_date:Optional[str] = None):  # pragma: no cover
        pass

    @abstractmethod
    def get_products(self, page=None):  # pragma: no cover
        pass

    @abstractmethod
    def get_tasks(self, page=None):  # pragma: no cover
        pass

    @abstractmethod
    def get_deals(
        self,
        page_id: str | None = None,
        deal_stage_id: str | None = None,
        start_date: str | None = None,
        name: str | None = None
    ):  # pragma: no cover
        pass

    @abstractmethod
    def get_deal_lost_reasons(self, page):  # pragma: no cover
        pass

    @abstractmethod
    def get_deal_stages(self, page=None):  # pragma: no cover
        pass

    @abstractmethod
    def get_deal_pipelines(self, page=None) -> list[Pipeline]:  # pragma: no cover
        pass

    @abstractmethod
    def get_deal_sources(self, page=None):  # pragma: no cover
        pass

    @abstractmethod
    def get_deal(self, deal_id: Optional[str] ): # pragma: no cover
        pass

    @abstractmethod
    def put_deal(self, deal_id, stage_id, seller_name:Optional[str] = None, source:Optional[str] = None):  # pragma: no cover
        pass

    @abstractmethod
    def post_deal(self, stage_id:str, contact_name:str, phone:str, seller_name:str): # pragma: no cover
        pass
