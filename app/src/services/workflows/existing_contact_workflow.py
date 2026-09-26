from loguru import logger

from app.src.domain.entities.chat import Chat
from app.src.domain.entities.contact import Contact
from app.src.domain.entities.deal import Deal
from app.src.domain.entities.template_configuration import TemplateConfiguration
from app.src.domain.process_summary_tracker import ProcessSummaryTracker
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.octadesk_lookup import OctadeskLookup


class ExistingContactWorkflow:
    def __init__(
        self,
        octadesk: OctadeskPort,
        rdstation: RDStationPort,
        lookup: OctadeskLookup,
        contact_repo: ContactRepositoryPort | None = None,
        deal_repo: DealRepositoryPort | None = None,
        chat_repo: ChatRepositoryPort | None = None,
    ):
        self._octadesk = octadesk
        self._rdstation = rdstation
        self._lookup = lookup
        self._contact_repo = contact_repo
        self._deal_repo = deal_repo
        self._chat_repo = chat_repo

    def execute(
        self,
        deal: Deal,
        contact: Contact,
        configuration: TemplateConfiguration,
        contacted_stage_id: str,
        contacted_nickname: str,
        tracker: ProcessSummaryTracker,
    ) -> None:
        logger.info(
            f"Existing octadesk contact: '{contact.name}' '{contact.phone}' '{contact.email}' "
        )
        tracker.record_contact_existing(contact)

        # Lookup or database check
        if not contact.octadesk_id:
            octadesk_id = self._lookup.has_contact(contact.phone)
            if octadesk_id and isinstance(octadesk_id, str):
                contact.octadesk_id = octadesk_id

        if self._contact_repo:
            contact = self._contact_repo.save(contact)

        if not self._lookup.has_chat(contact.phone):
            chat_response = self._octadesk.start_chat(
                contact.to_dict(), configuration.to_dict()
            )
            result = chat_response["response"]["result"]
            chat_id = result["roomKey"]
            logger.info(f"https://app.octadesk.com/chat/{chat_id}/all")
            self._octadesk.notify_agent(
                chat_id,
                f"Cliente se inscreveu por landing page (RD). Não havia conversa prévia. Origem: {deal.deal_source_name}. Campanha: {deal.deal_campaign_name}",
                configuration.agent,
            )
            contact.chat_response = chat_response
            tracker.record_chat_started(contact)

            # Save Deal
            deal.contact_id = contact.id
            deal.deal_status = contacted_nickname
            if self._deal_repo:
                deal = self._deal_repo.save(deal)

            # Save Chat
            chat = Chat(
                id="",
                status="active",
                octadesk_id=chat_id,
                channel="whatsapp",
                contact_id=contact.id,
            )
            if self._chat_repo:
                self._chat_repo.save(chat)

            self._rdstation.put_deal(deal.deal_id, contacted_stage_id)
            return

        logger.info(
            f"[EXISTING CONTACT] Has a chat in progress '{contact.name}' '{contact.phone}' '{contact.email}'"
        )
        existing_chat_id = self._lookup.get_existing_chat_id(contact.phone)
        if existing_chat_id:
            logger.info(f"https://app.octadesk.com/chat/{existing_chat_id}/all")
            self._octadesk.notify_agent(
                existing_chat_id,
                f"Cliente se inscreveu por landing page (RD). Origem: {deal.deal_source_name}. Campanha: {deal.deal_campaign_name}",
                configuration.agent,
            )

            # Save Deal
            deal.contact_id = contact.id
            deal.deal_status = contacted_nickname
            if self._deal_repo:
                deal = self._deal_repo.save(deal)

            # Save Chat
            chat = Chat(
                id="",
                status="active",
                octadesk_id=existing_chat_id,
                channel="whatsapp",
                contact_id=contact.id,
            )
            if self._chat_repo:
                self._chat_repo.save(chat)

        self._rdstation.put_deal(deal.deal_id, contacted_stage_id)
        tracker.record_chat_existing(contact)
