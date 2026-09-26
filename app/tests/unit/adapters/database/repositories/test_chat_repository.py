from app.src.adapters.database.repositories.chat_repository_adapter import (
    SQLAlchemyChatRepositoryAdapter,
)
from app.src.domain.entities.chat import Chat


def test_chat_repository_save_and_find(db_session):
    repo = SQLAlchemyChatRepositoryAdapter(db_session)

    chat = Chat(
        id="chat-local-id",
        status="active",
        octadesk_id="room-ext-123",
        channel="whatsapp",
        contact_id=None,
    )

    # Test save
    saved = repo.save(chat)
    assert saved.id is not None
    assert saved.octadesk_id == "room-ext-123"
    assert saved.channel == "whatsapp"

    # Test find_by_id
    found = repo.find_by_id(saved.id)
    assert found is not None
    assert found.octadesk_id == "room-ext-123"

    # Test find_by_octadesk_id
    found_octa = repo.find_by_octadesk_id("room-ext-123")
    assert found_octa is not None
    assert found_octa.id == saved.id


def test_chat_repository_find_not_found(db_session):
    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    assert repo.find_by_id("non-existent-id") is None  # invalid UUID
    assert repo.find_by_octadesk_id("non-existent-octa") is None


def test_chat_repository_find_by_id_valid_uuid_not_found(db_session):
    """Covers line 60: valid UUID that doesn't exist returns None."""
    import uuid

    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    assert repo.find_by_id(str(uuid.uuid4())) is None


def test_chat_repository_update_existing(db_session):
    """Covers lines 43-48: updating an existing chat record."""
    import uuid

    repo = SQLAlchemyChatRepositoryAdapter(db_session)

    chat = Chat(
        id="",
        status="active",
        octadesk_id="room-upd-001",
        channel="whatsapp",
        contact_id=None,
    )
    saved = repo.save(chat)

    # Save again with same octadesk_id — triggers update branch (covers lines 43-46)
    # Also passes a valid contact_id UUID to cover line 48
    contact_uuid = str(uuid.uuid4())
    updated_chat = Chat(
        id=saved.id,
        status="active",
        octadesk_id="room-upd-001",
        channel="instagram",  # changed channel
        contact_id=contact_uuid,  # sets model.contact_id (line 48)
    )
    updated = repo.save(updated_chat)

    assert updated.channel == "instagram"
    assert updated.octadesk_id == "room-upd-001"


def test_chat_repository_timestamp_mapping(db_session):
    from datetime import datetime
    from app.src.adapters.database.models import ChatModel

    now = datetime.now()
    model = ChatModel(
        octadesk_id="chat-ts-repo-001",
        channel="whatsapp",
        created_at=now,
        updated_at=now,
    )
    db_session.add(model)
    db_session.commit()

    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    found = repo.find_by_id(str(model.id))
    assert found is not None
    assert found.created_at is not None
    assert found.updated_at is not None

    found_octa = repo.find_by_octadesk_id("chat-ts-repo-001")
    assert found_octa is not None
    assert found_octa.created_at is not None
    assert found_octa.updated_at is not None


def test_chat_repository_timestamp_mapping_none(db_session):
    import uuid
    from app.src.adapters.database.models import ChatModel

    model = ChatModel(
        id=uuid.uuid4(),
        octadesk_id="chat-no-ts-repo-001",
        channel="whatsapp",
    )
    model.created_at = None
    model.updated_at = None

    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    domain_chat = repo._to_domain(model)
    assert domain_chat.created_at is None
    assert domain_chat.updated_at is None


def test_chat_repository_created_at_persistence(db_session):
    from datetime import datetime
    from app.src.core.datetime_utils import get_timezone, get_now
    repo = SQLAlchemyChatRepositoryAdapter(db_session)

    # 1. Save with explicit created_at
    explicit_dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=get_timezone())
    chat_explicit = Chat(
        id="",
        status="active",
        octadesk_id="chat-explicit-ts",
        channel="whatsapp",
        contact_id=None,
        created_at=explicit_dt,
    )
    saved_explicit = repo.save(chat_explicit)
    # Compare tz-naive equivalents
    saved_explicit_naive = saved_explicit.created_at.replace(tzinfo=None) if saved_explicit.created_at.tzinfo else saved_explicit.created_at
    assert saved_explicit_naive == explicit_dt.replace(tzinfo=None)

    # 2. Save without created_at (should fall back to current local/configured time)
    chat_implicit = Chat(
        id="",
        status="active",
        octadesk_id="chat-implicit-ts",
        channel="whatsapp",
        contact_id=None,
        created_at=None,
    )
    before_save = get_now()
    saved_implicit = repo.save(chat_implicit)
    after_save = get_now()
    assert saved_implicit.created_at is not None
    
    saved_implicit_naive = saved_implicit.created_at.replace(tzinfo=None) if saved_implicit.created_at.tzinfo else saved_implicit.created_at
    before_save_naive = before_save.replace(tzinfo=None)
    after_save_naive = after_save.replace(tzinfo=None)
    assert before_save_naive <= saved_implicit_naive <= after_save_naive

    # 3. Update existing Chat without updating created_at
    updated_chat = Chat(
        id=saved_implicit.id,
        status="active",
        octadesk_id="chat-implicit-ts",
        channel="instagram",
        contact_id=None,
        created_at=None,
    )
    updated = repo.save(updated_chat)
    updated_naive = updated.created_at.replace(tzinfo=None) if updated.created_at.tzinfo else updated.created_at
    assert updated_naive == saved_implicit_naive

    # 4. Update existing Chat with an explicit updated created_at
    new_explicit_dt = datetime(2026, 2, 2, 14, 0, 0, tzinfo=get_timezone())
    updated_chat_with_ts = Chat(
        id=saved_implicit.id,
        status="active",
        octadesk_id="chat-implicit-ts",
        channel="instagram",
        contact_id=None,
        created_at=new_explicit_dt,
    )
    updated_with_ts = repo.save(updated_chat_with_ts)
    updated_with_ts_naive = updated_with_ts.created_at.replace(tzinfo=None) if updated_with_ts.created_at.tzinfo else updated_with_ts.created_at
    assert updated_with_ts_naive == new_explicit_dt.replace(tzinfo=None)






# ---------------------------------------------------------------------------
# add-db-indexes — find_by_contact_id
# ---------------------------------------------------------------------------


def test_chat_repository_find_by_contact_id_returns_entity(db_session):
    """find_by_contact_id() retorna o Chat associado ao contact_id informado."""
    import uuid
    from app.src.adapters.database.models import ChatModel, ContactModel

    contact_id = uuid.uuid4()
    contact = ContactModel(id=contact_id, name="Contato Chat Índice")
    chat_model = ChatModel(
        octadesk_id="chat-idx-contact-001",
        channel="whatsapp",
        contact_id=contact_id,
    )
    db_session.add_all([contact, chat_model])
    db_session.commit()

    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    found = repo.find_by_contact_id(str(contact_id))
    assert found is not None
    assert found.octadesk_id == "chat-idx-contact-001"


def test_chat_repository_find_by_contact_id_not_found(db_session):
    """find_by_contact_id() retorna None quando contact_id não existe."""
    import uuid
    from app.src.adapters.database.repositories.chat_repository_adapter import (
        SQLAlchemyChatRepositoryAdapter,
    )

    repo = SQLAlchemyChatRepositoryAdapter(db_session)
    # UUID válido mas inexistente — o adapter converte e retorna None
    assert repo.find_by_contact_id(str(uuid.uuid4())) is None
    # ID com formato UUID inválido
    assert repo.find_by_contact_id("invalid-uuid") is None

