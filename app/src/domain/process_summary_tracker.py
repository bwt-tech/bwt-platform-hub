from typing import Any

from app.src.domain.entities.contact import Contact


class ProcessSummaryTracker:
    def __init__(self, pipeline_name: str):
        self._summary: dict[str, Any] = {
            "pipeline": pipeline_name,
            "deals_processed": 0,
            "contacts_created": 0,
            "contacts_created_data": [],
            "contacts_existing": 0,
            "contacts_existing_data": [],
            "chats_started": 0,
            "chats_started_data": [],
            "chats_not_started": 0,
            "chats_not_started_data": [],
            "chats_existing": 0,
            "chats_existing_data": [],
            "deals_moved": 0,
            "deals_moved_data": [],
            "deals_skipped": 0,
            "deals_skipped_data": [],
            "deals_failed": 0,
            "deals_failed_data": [],
            "contacts_with_recurring_no_answer": 0,
            "contacts_with_recurring_no_answer_data": [],
        }

    def record_contact_created(self, contact: Contact) -> None:
        self._summary["contacts_created"] += 1
        self._summary["contacts_created_data"].append(contact.to_dict())

    def record_contact_existing(self, contact: Contact) -> None:
        self._summary["contacts_existing"] += 1
        self._summary["contacts_existing_data"].append(contact.to_dict())

    def record_chat_started(self, contact: Contact) -> None:
        self._summary["chats_started"] += 1
        self._summary["chats_started_data"].append(contact.to_dict())

    def record_chat_not_started(self, contact: Contact) -> None:
        self._summary["chats_not_started"] += 1
        self._summary["chats_not_started_data"].append(contact.to_dict())

    def record_chat_existing(self, contact: Contact) -> None:
        self._summary["chats_existing"] += 1
        self._summary["chats_existing_data"].append(contact.to_dict())

    def record_recurring_no_answer(self, contact: Contact) -> None:
        self._summary["contacts_with_recurring_no_answer"] += 1
        self._summary["contacts_with_recurring_no_answer_data"].append(
            contact.to_dict()
        )

    def record_deal_failed(self, contact_data: dict[str, Any]) -> None:
        self._summary["deals_failed"] += 1
        self._summary["deals_failed_data"].append(contact_data)

    def record_deal_moved(self, contact: Contact) -> None:
        self._summary["deals_moved"] += 1
        self._summary["deals_moved_data"].append(contact.to_dict())

    def record_deal_processed(self) -> None:
        self._summary["deals_processed"] += 1

    def to_dict(self) -> dict[str, Any]:
        return self._summary
