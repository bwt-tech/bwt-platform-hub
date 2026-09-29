import uuid
from datetime import datetime

from app.src.adapters.database.connection import Base
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.src.core.datetime_utils import get_now

class ContactModel(Base):
    __tablename__ = "contact"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    octadesk_id = Column(String(255), unique=True, nullable=True)
    rdstation_id = Column(String(255), unique=True, nullable=True)
    bwt_account_id = Column(Integer, unique=True, nullable=True)
    bwt_contact_id = Column(Integer, unique=True, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        default=get_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    info = relationship(
        "ContactInfoModel",
        uselist=False,
        back_populates="contact",
        cascade="all, delete-orphan",
    )
    deals = relationship("DealModel", back_populates="contact")
    chats = relationship("ChatModel", back_populates="contact")


class ContactInfoModel(Base):
    __tablename__ = "contact_info"

    contact_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contact.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)

    contact = relationship("ContactModel", back_populates="info")

    __table_args__ = (
        UniqueConstraint("email", "phone", name="uq_contact_info_email_phone"),
    )


class DealModel(Base):
    __tablename__ = "deal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rdstation_id = Column(String(255), unique=True, nullable=True)
    contact_id = Column(
        UUID(as_uuid=True), ForeignKey("contact.id", ondelete="SET NULL"), nullable=True
    )
    deal_status = Column(String(50), nullable=False)
    bwt_deal_id = Column(Integer, unique=True, nullable=True)
    bwt_responsible_id = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        default=get_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    contact = relationship("ContactModel", back_populates="deals")

    __table_args__ = (
        Index("ix_deal_contact_id", "contact_id"),
        Index("ix_deal_contact_id_rdstation_id", "contact_id", "rdstation_id"),
    )


class ChatModel(Base):
    __tablename__ = "chat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    octadesk_id = Column(String(255), unique=True, nullable=False)
    channel = Column(String(50), nullable=False)
    contact_id = Column(
        UUID(as_uuid=True), ForeignKey("contact.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        default=get_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    contact = relationship("ContactModel", back_populates="chats")

    __table_args__ = (
        Index("ix_chat_contact_id", "contact_id"),
    )
