from typing import Any

from app.src.domain.entities.deal import Deal


class DealFactory:
    """Factory para construção de Deal a partir de payloads da RD Station."""

    @staticmethod
    def from_rd_deal_with_contact(
        deal_dict: dict[str, Any], rd_contact: dict[str, Any]
    ) -> Deal:
        enriched = {**deal_dict, "contacts": [rd_contact]}
        return Deal.from_dict(enriched)
