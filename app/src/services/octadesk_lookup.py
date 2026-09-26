from app.src.contracts.octadesk.contact_response import OctadeskContactResponse
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.ports.octadesk_port import OctadeskPort


class OctadeskLookup:
    def __init__(
        self, octadesk: OctadeskPort, contact_repo: ContactRepositoryPort | None = None
    ):
        self._octadesk = octadesk
        self._contact_repo = contact_repo

    def all_phones(self, full_phone: str) -> list[str]:
        old_phone_format = full_phone[-8:]
        phone_without_9 = full_phone[:2] + old_phone_format
        if len(full_phone) == 10:
            full_phone = full_phone[:2] + "9" + old_phone_format
        
        return [full_phone, phone_without_9]

    def has_chat(self, full_phone: str) -> bool:
        for phone in self.all_phones(full_phone):
            chats = self._octadesk.get_chats_by_phone(phone)
            if chats is not None and len(chats) > 0:
                return True
        return False

    def get_existing_chat_id(self, full_phone: str) -> str | None:
        for phone in self.all_phones(full_phone):
            chats = self._octadesk.get_chats_by_phone(phone)
            if chats is not None and len(chats) > 0:
                return chats[0].get("id")
        return None  # pragma: no cover

    def has_contact(self, full_phone: str) -> str | None:
        # 1. Database-first lookup
        if self._contact_repo:
            for phone in self.all_phones(full_phone):
                contact = self._contact_repo.find_by_phone(phone)
                if contact and contact.octadesk_id:
                    return contact.octadesk_id

        # 2. Fallback to API lookup
        for phone in self.all_phones(full_phone):
            contacts = self._octadesk.get_contacts_by_phone(phone)
            if contacts is not None and len(contacts) > 0:
                validated = [
                    OctadeskContactResponse.model_validate(c) for c in contacts
                ]
                return validated[0].id
        return None
