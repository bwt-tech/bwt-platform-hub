import uuid
from datetime import datetime

from app.src.adapters.database.models import (
    ChatModel,
    ContactInfoModel,
    ContactModel,
    DealModel,
)


def test_contact_model_and_relationships(db_session):
    contact_id = uuid.uuid4()
    contact = ContactModel(
        id=contact_id,
        name="John Doe",
        octadesk_id="octa-123",
        rdstation_id="rd-123",
    )
    db_session.add(contact)
    db_session.commit()

    info = ContactInfoModel(
        contact_id=contact_id,
        email="john@example.com",
        phone="5511999999999",
    )
    db_session.add(info)

    deal = DealModel(
        rdstation_id="deal-rd-123",
        contact_id=contact_id,
        deal_status="SC",
    )
    db_session.add(deal)

    chat = ChatModel(
        octadesk_id="chat-octa-123",
        channel="whatsapp",
        contact_id=contact_id,
    )
    db_session.add(chat)
    db_session.commit()

    # Query back
    saved_contact = db_session.query(ContactModel).filter_by(id=contact_id).first()
    assert saved_contact is not None
    assert saved_contact.name == "John Doe"
    assert saved_contact.octadesk_id == "octa-123"
    assert saved_contact.rdstation_id == "rd-123"

    assert saved_contact.info is not None
    assert saved_contact.info.email == "john@example.com"
    assert saved_contact.info.phone == "5511999999999"

    assert len(saved_contact.deals) == 1
    assert saved_contact.deals[0].rdstation_id == "deal-rd-123"
    assert saved_contact.deals[0].deal_status == "SC"

    assert len(saved_contact.chats) == 1
    assert saved_contact.chats[0].octadesk_id == "chat-octa-123"
    assert saved_contact.chats[0].channel == "whatsapp"


# --- Task 5.1: ChatModel timestamp tests ---


def test_chat_model_timestamps_persisted(db_session):
    now = datetime.now()
    chat = ChatModel(
        octadesk_id="chat-ts-001",
        channel="whatsapp",
        created_at=now,
        updated_at=now,
    )
    db_session.add(chat)
    db_session.commit()
    saved = db_session.query(ChatModel).filter_by(octadesk_id="chat-ts-001").first()
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_chat_model_timestamps_nullable(db_session):
    chat = ChatModel(
        octadesk_id="chat-no-ts-001",
        channel="whatsapp",
    )
    db_session.add(chat)
    db_session.commit()
    saved = db_session.query(ChatModel).filter_by(octadesk_id="chat-no-ts-001").first()
    # nullable=True means existing records without timestamps are valid
    assert saved is not None


# --- Task 5.2: ContactModel timestamp tests ---


def test_contact_model_timestamps_persisted(db_session):
    now = datetime.now()
    contact = ContactModel(
        name="Timestamp User",
        created_at=now,
        updated_at=now,
    )
    db_session.add(contact)
    db_session.commit()
    saved = db_session.query(ContactModel).filter_by(name="Timestamp User").first()
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_contact_model_timestamps_nullable(db_session):
    contact = ContactModel(
        name="No Timestamp User",
    )
    db_session.add(contact)
    db_session.commit()
    saved = db_session.query(ContactModel).filter_by(name="No Timestamp User").first()
    assert saved is not None


# --- Task 5.3: DealModel timestamp tests ---


def test_deal_model_timestamps_persisted(db_session):
    now = datetime.now()
    deal = DealModel(
        rdstation_id="ts-deal-001",
        deal_status="SC",
        created_at=now,
        updated_at=now,
    )
    db_session.add(deal)
    db_session.commit()
    saved = db_session.query(DealModel).filter_by(rdstation_id="ts-deal-001").first()
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_deal_model_timestamps_nullable(db_session):
    deal = DealModel(
        rdstation_id="no-ts-deal-001",
        deal_status="SC",
    )
    db_session.add(deal)
    db_session.commit()
    saved = db_session.query(DealModel).filter_by(rdstation_id="no-ts-deal-001").first()
    assert saved is not None


# ---------------------------------------------------------------------------
# add-db-indexes — verificar declaração de __table_args__ nos models
# ---------------------------------------------------------------------------


def test_deal_model_has_index_on_contact_id():
    """DealModel.__table_args__ deve declarar ix_deal_contact_id."""
    index_names = {idx.name for idx in DealModel.__table_args__ if hasattr(idx, "name")}
    assert "ix_deal_contact_id" in index_names


def test_deal_model_has_composite_index_contact_id_rdstation_id():
    """DealModel.__table_args__ deve declarar ix_deal_contact_id_rdstation_id."""
    index_names = {idx.name for idx in DealModel.__table_args__ if hasattr(idx, "name")}
    assert "ix_deal_contact_id_rdstation_id" in index_names


def test_deal_model_composite_index_covers_correct_columns():
    """O índice composto de DealModel deve cobrir as colunas contact_id e rdstation_id."""
    from sqlalchemy import Index

    composite = next(
        (idx for idx in DealModel.__table_args__ if isinstance(idx, Index) and idx.name == "ix_deal_contact_id_rdstation_id"),
        None,
    )
    assert composite is not None
    col_names = [expr.key for expr in composite.expressions]
    assert "contact_id" in col_names
    assert "rdstation_id" in col_names


def test_chat_model_has_index_on_contact_id():
    """ChatModel.__table_args__ deve declarar ix_chat_contact_id."""
    index_names = {idx.name for idx in ChatModel.__table_args__ if hasattr(idx, "name")}
    assert "ix_chat_contact_id" in index_names
