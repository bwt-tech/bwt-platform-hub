import uuid
from app.src.core.datetime_utils import get_now

from app.src.adapters.database.models import ChatModel
from app.src.domain.entities.chat import Chat
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from sqlalchemy.orm import Session


class SQLAlchemyChatRepositoryAdapter(ChatRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: ChatModel) -> Chat:
        return Chat(
            id=str(model.id),
            status="active",
            octadesk_id=model.octadesk_id,
            channel=model.channel,
            contact_id=str(model.contact_id) if model.contact_id else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, chat: Chat) -> Chat:
        # Check if chat.id is a valid UUID, otherwise generate one
        try:
            chat_id = uuid.UUID(chat.id) if chat.id else uuid.uuid4()
        except (ValueError, TypeError):
            chat_id = uuid.uuid4()

        contact_uuid = uuid.UUID(chat.contact_id) if chat.contact_id else None

        model = self.session.query(ChatModel).filter_by(id=chat_id).first()
        if not model and chat.octadesk_id:
            model = (
                self.session.query(ChatModel)
                .filter_by(octadesk_id=chat.octadesk_id)
                .first()
            )

        created_at = chat.created_at or get_now()

        if not model:
            model = ChatModel(
                id=chat_id,
                octadesk_id=chat.octadesk_id or chat.id,
                channel=chat.channel or "whatsapp",
                contact_id=contact_uuid,
                created_at=created_at,
            )
            self.session.add(model)
        else:
            if chat.octadesk_id:
                model.octadesk_id = chat.octadesk_id
            if chat.channel:
                model.channel = chat.channel
            if contact_uuid:
                model.contact_id = contact_uuid
            if chat.created_at:
                model.created_at = chat.created_at

        self.session.flush()
        return self._to_domain(model)

    def find_by_id(self, chat_id: str) -> Chat | None:
        try:
            uid = uuid.UUID(chat_id)
        except (ValueError, TypeError):
            return None
        model = self.session.query(ChatModel).filter_by(id=uid).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_octadesk_id(self, octadesk_id: str) -> Chat | None:
        model = self.session.query(ChatModel).filter_by(octadesk_id=octadesk_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_contact_id(self, contact_id: str) -> Chat | None:
        try:
            contact_uuid = uuid.UUID(contact_id)
        except (ValueError, TypeError):
            return None
        model = self.session.query(ChatModel).filter_by(contact_id=contact_uuid).first()
        if not model:
            return None
        return self._to_domain(model)
