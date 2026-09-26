from typing import Any

from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal import Deal
from app.src.domain.factories.deal_factory import DealFactory
from app.src.domain.policies.deal_status_policy import (
    WITH_SELLER,
    DealStatusPolicy,
)
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.rdstation_port import RDStationPort


class RDStationReverseSyncService:
    """Sincroniza contatos e negociações com a RD Station no fluxo reverso."""

    def __init__(
        self,
        rdstation_port: RDStationPort,
        deal_repo: DealRepositoryPort | None = None,
    ):
        self._rdstation = rdstation_port
        self._deal_repo = deal_repo

    def sync_deals(
        self,
        contact: Contact,
        contact_name: str,
        contact_phone: str,
        contact_email: str,
        seller: str,
        with_seller_stage_id: str,
    ) -> None:
        rd_contacts = self._fetch_rd_contacts(contact_phone)
        create_new_deal = len(rd_contacts) == 0

        for rd_contact in rd_contacts:
            create_new_deal = self._process_rd_contact_deals(
                rd_contact=rd_contact,
                contact=contact,
                seller=seller,
                with_seller_stage_id=with_seller_stage_id,
                create_new_deal=create_new_deal,
            )
            if not create_new_deal and self._has_active_rd_deal(rd_contact):
                break

        if create_new_deal:
            self._create_new_rd_deal(
                contact=contact,
                contact_name=contact_name,
                contact_phone=contact_phone,
                contact_email=contact_email,
                seller=seller,
                with_seller_stage_id=with_seller_stage_id,
            )

    def _fetch_rd_contacts(self, contact_phone: str) -> list[dict[str, Any]]:
        response = self._rdstation.get_contacts(phone=contact_phone)
        if not response:
            return []
        return response.get("contacts", [])

    def _process_rd_contact_deals(
        self,
        rd_contact: dict[str, Any],
        contact: Contact,
        seller: str,
        with_seller_stage_id: str,
        create_new_deal: bool,
    ) -> bool:
        for contact_deal in rd_contact.get("deals", []):
            deal_dict = self._rdstation.get_deal(deal_id=contact_deal["id"])
            deal = DealFactory.from_rd_deal_with_contact(deal_dict, rd_contact)
            self._persist_deal_if_missing(deal, contact)

            if DealStatusPolicy.should_update_to_with_seller(deal.deal_status):
                self._update_deal_to_with_seller(
                    deal, seller, with_seller_stage_id
                )
                return False

            if DealStatusPolicy.is_final(deal.deal_status):
                create_new_deal = True

            if DealStatusPolicy.is_in_progress(deal.deal_status):
                return False

        return create_new_deal

    def _persist_deal_if_missing(self, deal: Deal, contact: Contact) -> None:
        if not self._deal_repo or not deal.rdstation_id:
            return
        existing_deal = self._deal_repo.find_by_rdstation_id(deal.rdstation_id)
        if existing_deal is None:
            deal.contact_id = contact.id
            self._deal_repo.save(deal)

    def _update_deal_to_with_seller(
        self, deal: Deal, seller: str, with_seller_stage_id: str
    ) -> None:
        self._rdstation.put_deal(
            deal_id=deal.rdstation_id,
            stage_id=with_seller_stage_id,
            seller_name=seller,
        )
        deal.deal_status = WITH_SELLER
        if self._deal_repo:
            self._deal_repo.save(deal)

    @staticmethod
    def _has_active_rd_deal(rd_contact: dict[str, Any]) -> bool:
        return any(
            DealStatusPolicy.is_active_in_rd(
                deal.get("deal_stage", {}).get("nickname", "")
            )
            for deal in rd_contact.get("deals", [])
        )

    def _create_new_rd_deal(
        self,
        contact: Contact,
        contact_name: str,
        contact_phone: str,
        contact_email: str,
        seller: str,
        with_seller_stage_id: str,
    ) -> None:
        deal_response = self._rdstation.post_deal(
            stage_id=with_seller_stage_id,
            contact_name=contact_name,
            phone=contact_phone,
        )
        new_deal_id = deal_response["id"]
        self._rdstation.put_deal(
            deal_id=new_deal_id,
            stage_id=with_seller_stage_id,
            seller_name=seller,
            source="Octadesk"
        )
        new_deal = Deal(
            deal_id=new_deal_id,
            name=contact_name,
            phone=contact_phone,
            email=contact_email,
            deal_source_name=deal_response.get("deal_source", {}).get("name", ""),
            deal_campaign_name=deal_response.get("campaign", {}).get("name", ""),
            rdstation_id=new_deal_id,
            deal_status=WITH_SELLER,
            contact_id=contact.id,
        )
        if self._deal_repo:
            self._deal_repo.save(new_deal)
