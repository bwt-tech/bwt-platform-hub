from typing import Any, Optional

from app.src.domain.entities.bwt_sync_result import BWTSyncResult
from app.src.domain.entities.chat import Chat
from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal import Deal
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.bwt_port import BWTPort
from app.src.services.octadesk_lookup import OctadeskLookup
from app.src.services.workflows.bwt_reverse_sync_service import BWTReverseSyncService
from app.src.services.workflows.rd_station_reverse_sync_service import (
    RDStationReverseSyncService,
)

WITH_SELLER = "EPV"


class ReverseSyncWorkflow:
    """Coordena persistência local, sync RD Station e sync BWT para um chat."""

    def __init__(
        self,
        octadesk_lookup: OctadeskLookup,
        rd_sync: RDStationReverseSyncService,
        bwt_sync: BWTReverseSyncService,
        contact_repo: Optional[ContactRepositoryPort] = None,
        deal_repo: Optional[DealRepositoryPort] = None,
        chat_repo: Optional[ChatRepositoryPort] = None,
    ):
        self._octadesk_lookup = octadesk_lookup
        self._rd_sync = rd_sync
        self._bwt_sync = bwt_sync
        self._contact_repo = contact_repo
        self._deal_repo = deal_repo
        self._chat_repo = chat_repo

    def execute(
        self,
        chat: dict[str, Any],
        seller: str,
        supervisor: str,
        with_seller_stage_id: str,
        bwt_port: BWTPort,
    ) -> None:
        contact_data = self._extract_contact_data(chat)
        contact = self._persist_contact_and_chat(chat["id"], contact_data)

        self._rd_sync.sync_deals(
            contact=contact,
            contact_name=contact_data["name"],
            contact_phone=contact_data["phone"],
            contact_email=contact_data["email"],
            seller=seller,
            with_seller_stage_id=with_seller_stage_id,
        )

        bwt_result: BWTSyncResult = self._bwt_sync.sync(
            bwt_port=bwt_port,
            contact_name=contact_data["name"],
            contact_email=contact_data["email"],
            contact_phone=contact_data["phone"],
            seller=seller,
            supervisor=supervisor
        )

        self._persist_bwt_ids(contact=contact, bwt_result=bwt_result)

    def _extract_contact_data(self, chat: dict[str, Any]) -> dict[str, str]:
        contact_phone = chat["contact"]["phoneContacts"][0]["number"]
        return {
            "name": chat["contact"]["name"],
            "email": chat["contact"]["email"],
            "phone": Deal.normalize_phone(contact_phone),
        }

    def _persist_contact_and_chat(
        self, chat_id: str, contact_data: dict[str, str]
    ) -> Contact:
        contact = self._find_or_create_contact(contact_data)
        self._ensure_chat_exists(chat_id, contact)
        return contact

    def _find_or_create_contact(self, contact_data: dict[str, str]) -> Contact:
        contact_phone = contact_data["phone"]
        all_phones = self._octadesk_lookup.all_phones(contact_phone)

        if self._contact_repo:
            for phone in all_phones:
                existing_contact = self._contact_repo.find_by_phone(phone)
                if existing_contact:
                    return existing_contact

        contact = Contact(
            name=contact_data["name"],
            phone=contact_phone,
            email=contact_data["email"],
        )
        if self._contact_repo:
            return self._contact_repo.save(contact)
        return contact

    def _ensure_chat_exists(self, chat_id: str, contact: Contact) -> None:
        if not self._chat_repo:
            return
        existing_chat = self._chat_repo.find_by_octadesk_id(octadesk_id=chat_id)
        if existing_chat is not None:
            return
        chat_entity = Chat(
            id="",
            status="active",
            octadesk_id=chat_id,
            channel="whatsapp",
            contact_id=contact.id,
        )
        self._chat_repo.save(chat_entity)

    def _persist_bwt_ids(self, contact: Contact, bwt_result: BWTSyncResult) -> None:
        """Persiste os IDs BWT no Contact e no Deal associado."""
        if not self._contact_repo:
            return

        contact.bwt_account_id = bwt_result.account_id
        contact.bwt_contact_id = bwt_result.contact_id
        updated_contact = self._contact_repo.save(contact)

        if not self._deal_repo:
            return

        deal = self._deal_repo.find_by_contact_id(updated_contact.id) if updated_contact.id else None
        if deal is None:
            return

        deal.bwt_deal_id = bwt_result.deal_id
        deal.bwt_responsible_id = bwt_result.responsible_id
        self._deal_repo.save(deal)
