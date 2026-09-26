import pytest
from app.src.domain.entities.contact import Contact
from app.src.domain.process_summary_tracker import ProcessSummaryTracker


@pytest.fixture
def contact():
    return Contact(
        name="Test", phone="11999999999", email="test@test.com", deal_id="123"
    )


def test_summary_tracker_initialization():
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    summary = tracker.to_dict()
    assert summary["deals_processed"] == 0
    assert summary["contacts_created"] == 0
    assert summary["contacts_existing"] == 0
    assert summary["chats_started"] == 0
    assert summary["chats_not_started"] == 0
    assert summary["chats_existing"] == 0
    assert summary["contacts_with_recurring_no_answer"] == 0
    assert summary["deals_failed"] == 0
    assert summary["deals_moved"] == 0


def test_summary_tracker_record_contact_created(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_contact_created(contact)
    assert tracker.to_dict()["contacts_created"] == 1
    assert tracker.to_dict()["contacts_created_data"] == [contact.to_dict()]


def test_summary_tracker_record_deal_processed():
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_deal_processed()
    assert tracker.to_dict()["deals_processed"] == 1


def test_summary_tracker_multiple_records(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_contact_existing(contact)
    tracker.record_chat_started(contact)
    tracker.record_deal_moved(contact)

    summary = tracker.to_dict()
    assert summary["contacts_existing"] == 1
    assert summary["contacts_existing_data"] == [contact.to_dict()]
    assert summary["chats_started"] == 1
    assert summary["chats_started_data"] == [contact.to_dict()]
    assert summary["deals_moved"] == 1
    assert summary["deals_moved_data"] == [contact.to_dict()]


def test_summary_tracker_record_chat_not_started(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_chat_not_started(contact)
    assert tracker.to_dict()["chats_not_started"] == 1
    assert tracker.to_dict()["chats_not_started_data"] == [contact.to_dict()]


def test_summary_tracker_record_chat_existing(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_chat_existing(contact)
    assert tracker.to_dict()["chats_existing"] == 1
    assert tracker.to_dict()["chats_existing_data"] == [contact.to_dict()]


def test_summary_tracker_record_recurring_no_answer(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_recurring_no_answer(contact)
    assert tracker.to_dict()["contacts_with_recurring_no_answer"] == 1
    assert tracker.to_dict()["contacts_with_recurring_no_answer_data"] == [contact.to_dict()]


def test_summary_tracker_record_deal_failed(contact):
    tracker = ProcessSummaryTracker(pipeline_name="BWT")
    tracker.record_deal_failed({"error": "test"})
    assert tracker.to_dict()["deals_failed"] == 1
    assert tracker.to_dict()["deals_failed_data"] == [{"error": "test"}]

