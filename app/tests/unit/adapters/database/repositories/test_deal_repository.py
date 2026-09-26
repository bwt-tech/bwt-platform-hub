from app.src.adapters.database.repositories.deal_repository_adapter import (
    SQLAlchemyDealRepositoryAdapter,
)
from app.src.domain.entities.deal import Deal


def test_deal_repository_save_and_find(db_session):
    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    deal = Deal(
        deal_id="deal-ext-123",
        name="Opportunity 1",
        phone="5511999999999",
        email="test@example.com",
        deal_source_name="RD",
        deal_campaign_name="Campaign 1",
        id=None,
        rdstation_id="deal-ext-123",
        contact_id=None,
        deal_status="SC",
    )

    # Test save
    saved = repo.save(deal)
    assert saved.id is not None
    assert saved.deal_id == "deal-ext-123"
    assert saved.rdstation_id == "deal-ext-123"
    assert saved.deal_status == "SC"

    # Test find_by_id
    found = repo.find_by_id(saved.id)
    assert found is not None
    assert found.deal_id == "deal-ext-123"

    # Test find_by_rdstation_id
    found_rd = repo.find_by_rdstation_id("deal-ext-123")
    assert found_rd is not None
    assert found_rd.id == saved.id


def test_deal_repository_find_not_found(db_session):
    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    assert repo.find_by_id("non-existent-id") is None  # invalid UUID
    assert repo.find_by_rdstation_id("non-existent-rd") is None


def test_deal_repository_find_by_id_valid_uuid_not_found(db_session):
    """Covers line 71: valid UUID that doesn't exist returns None."""
    import uuid

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    assert repo.find_by_id(str(uuid.uuid4())) is None


def test_deal_repository_update_existing(db_session):
    """Covers lines 54-59: updating an existing deal record."""
    import uuid

    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    deal = Deal(
        deal_id="deal-upd-001",
        name="Update Deal",
        phone="5511988880001",
        email="upd@example.com",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        id=None,
        rdstation_id="deal-upd-001",
        contact_id=None,
        deal_status="SC",
    )
    saved = repo.save(deal)

    # Save again with the same id — triggers update branch (covers lines 54-59)
    # Pass a valid contact_id to cover line 57 (model.contact_id = contact_uuid)
    contact_uuid = str(uuid.uuid4())
    updated_deal = Deal(
        deal_id="deal-upd-001",
        name="Update Deal",
        phone="5511988880001",
        email="upd@example.com",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        id=saved.id,
        rdstation_id="deal-upd-001",
        contact_id=contact_uuid,
        deal_status="CF",
    )
    updated = repo.save(updated_deal)

    assert updated.deal_status == "CF"
    assert updated.rdstation_id == "deal-upd-001"


def test_deal_repository_timestamp_mapping(db_session):
    from datetime import datetime
    from app.src.adapters.database.models import DealModel

    now = datetime.now()
    model = DealModel(
        rdstation_id="deal-ts-repo-001",
        deal_status="SC",
        created_at=now,
        updated_at=now,
    )
    db_session.add(model)
    db_session.commit()

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    found = repo.find_by_id(str(model.id))
    assert found is not None
    assert found.created_at is not None
    assert found.updated_at is not None

    found_rd = repo.find_by_rdstation_id("deal-ts-repo-001")
    assert found_rd is not None
    assert found_rd.created_at is not None
    assert found_rd.updated_at is not None


def test_deal_repository_timestamp_mapping_none(db_session):
    import uuid
    from app.src.adapters.database.models import DealModel

    model = DealModel(
        id=uuid.uuid4(),
        rdstation_id="deal-no-ts-repo-001",
        deal_status="SC",
    )
    model.created_at = None
    model.updated_at = None

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    domain_deal = repo._to_domain(model)
    assert domain_deal.created_at is None
    assert domain_deal.updated_at is None


def test_deal_repository_with_contact_and_info(db_session):
    import uuid
    from app.src.adapters.database.models import ContactInfoModel, ContactModel, DealModel

    contact_id = uuid.uuid4()
    contact = ContactModel(
        id=contact_id,
        name="John Doe",
    )
    contact_info = ContactInfoModel(
        contact_id=contact_id,
        phone="5511999998888",
        email="contact@example.com",
    )
    contact.info = contact_info
    deal_model = DealModel(
        id=uuid.uuid4(),
        rdstation_id="deal-with-contact-001",
        deal_status="SC",
        contact=contact,
    )
    db_session.add_all([contact, contact_info, deal_model])
    db_session.commit()

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    found = repo.find_by_id(str(deal_model.id))
    assert found is not None
    assert found.name == "John Doe"
    assert found.phone == "5511999998888"
    assert found.email == "contact@example.com"


def test_deal_repository_created_at_persistence(db_session):
    from datetime import datetime
    from app.src.core.datetime_utils import get_timezone, get_now
    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    # 1. Save with explicit created_at
    explicit_dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=get_timezone())
    deal_explicit = Deal(
        id="",
        deal_id="deal-explicit-ts",
        name="Explicit Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-explicit-ts",
        contact_id=None,
        deal_status="SC",
        created_at=explicit_dt,
    )
    saved_explicit = repo.save(deal_explicit)
    saved_explicit_naive = saved_explicit.created_at.replace(tzinfo=None) if saved_explicit.created_at.tzinfo else saved_explicit.created_at
    assert saved_explicit_naive == explicit_dt.replace(tzinfo=None)

    # 2. Save without created_at (should fall back to current local/configured time)
    deal_implicit = Deal(
        id="",
        deal_id="deal-implicit-ts",
        name="Implicit Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-implicit-ts",
        contact_id=None,
        deal_status="SC",
        created_at=None,
    )
    before_save = get_now()
    saved_implicit = repo.save(deal_implicit)
    after_save = get_now()
    assert saved_implicit.created_at is not None
    
    saved_implicit_naive = saved_implicit.created_at.replace(tzinfo=None) if saved_implicit.created_at.tzinfo else saved_implicit.created_at
    before_save_naive = before_save.replace(tzinfo=None)
    after_save_naive = after_save.replace(tzinfo=None)
    assert before_save_naive <= saved_implicit_naive <= after_save_naive

    # 3. Update existing Deal without updating created_at
    updated_deal = Deal(
        id=saved_implicit.id,
        deal_id="deal-implicit-ts",
        name="Implicit Deal Updated",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-implicit-ts",
        contact_id=None,
        deal_status="CF",
        created_at=None,
    )
    updated = repo.save(updated_deal)
    updated_naive = updated.created_at.replace(tzinfo=None) if updated.created_at.tzinfo else updated.created_at
    assert updated_naive == saved_implicit_naive

    # 4. Update existing Deal with an explicit updated created_at
    new_explicit_dt = datetime(2026, 2, 2, 14, 0, 0, tzinfo=get_timezone())
    updated_deal_with_ts = Deal(
        id=saved_implicit.id,
        deal_id="deal-implicit-ts",
        name="Implicit Deal Updated",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-implicit-ts",
        contact_id=None,
        deal_status="CF",
        created_at=new_explicit_dt,
    )
    updated_with_ts = repo.save(updated_deal_with_ts)
    updated_with_ts_naive = updated_with_ts.created_at.replace(tzinfo=None) if updated_with_ts.created_at.tzinfo else updated_with_ts.created_at
    assert updated_with_ts_naive == new_explicit_dt.replace(tzinfo=None)








# ---------------------------------------------------------------------------
# T14 — BWT fields: save() and find_by_bwt_deal_id coverage
# ---------------------------------------------------------------------------


def test_deal_repository_save_persists_bwt_ids(db_session):
    """save() updates bwt_deal_id and bwt_responsible_id on an existing deal."""
    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    # First: create the deal without BWT IDs
    deal = Deal(
        id=None,
        deal_id="deal-bwt-001",
        name="BWT Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-001",
        contact_id=None,
        deal_status="SC",
    )
    saved = repo.save(deal)
    assert saved.bwt_deal_id is None
    assert saved.bwt_responsible_id is None

    # Second: update with BWT IDs — triggers the else (update) branch
    deal_with_bwt = Deal(
        id=saved.id,
        deal_id="deal-bwt-001",
        name="BWT Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-001",
        contact_id=None,
        deal_status="SC",
        bwt_deal_id=7007,
        bwt_responsible_id=8008,
    )
    updated = repo.save(deal_with_bwt)

    assert updated.bwt_deal_id == 7007
    assert updated.bwt_responsible_id == 8008


def test_deal_repository_save_persists_bwt_deal_id_without_responsible(db_session):
    """save() persists bwt_deal_id even when bwt_responsible_id is None."""
    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    deal = Deal(
        id=None,
        deal_id="deal-bwt-no-resp",
        name="BWT No Resp",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-no-resp",
        contact_id=None,
        deal_status="SC",
    )
    saved = repo.save(deal)

    deal_with_bwt = Deal(
        id=saved.id,
        deal_id="deal-bwt-no-resp",
        name="BWT No Resp",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-no-resp",
        contact_id=None,
        deal_status="SC",
        bwt_deal_id=9009,
        bwt_responsible_id=None,
    )
    updated = repo.save(deal_with_bwt)

    assert updated.bwt_deal_id == 9009
    assert updated.bwt_responsible_id is None


def test_deal_repository_find_by_bwt_deal_id_returns_entity(db_session):
    """find_by_bwt_deal_id() returns the matching Deal."""
    repo = SQLAlchemyDealRepositoryAdapter(db_session)

    deal = Deal(
        id=None,
        deal_id="deal-bwt-find-001",
        name="BWT Find Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-find-001",
        contact_id=None,
        deal_status="SC",
    )
    saved = repo.save(deal)

    deal_with_bwt = Deal(
        id=saved.id,
        deal_id="deal-bwt-find-001",
        name="BWT Find Deal",
        phone="",
        email="",
        deal_source_name="RD",
        deal_campaign_name="Camp",
        rdstation_id="deal-bwt-find-001",
        contact_id=None,
        deal_status="SC",
        bwt_deal_id=1234,
        bwt_responsible_id=5678,
    )
    repo.save(deal_with_bwt)

    found = repo.find_by_bwt_deal_id(1234)
    assert found is not None
    assert found.id == saved.id
    assert found.bwt_deal_id == 1234
    assert found.bwt_responsible_id == 5678


def test_deal_repository_find_by_bwt_deal_id_not_found(db_session):
    """find_by_bwt_deal_id() returns None when no match exists."""
    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    assert repo.find_by_bwt_deal_id(99999) is None


# ---------------------------------------------------------------------------
# add-db-indexes — find_by_contact_id e find_by_contact_id_and_rd_station_id
# ---------------------------------------------------------------------------


def test_deal_repository_find_by_contact_id_returns_entity(db_session):
    """find_by_contact_id() retorna o Deal associado ao contact_id informado."""
    import uuid
    from app.src.adapters.database.models import ContactModel, DealModel

    contact_id = uuid.uuid4()
    contact = ContactModel(id=contact_id, name="Contato Índice")
    deal_model = DealModel(
        rdstation_id="deal-idx-contact-001",
        deal_status="SC",
        contact_id=contact_id,
    )
    db_session.add_all([contact, deal_model])
    db_session.commit()

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    found = repo.find_by_contact_id(str(contact_id))
    assert found is not None
    assert found.rdstation_id == "deal-idx-contact-001"


def test_deal_repository_find_by_contact_id_not_found(db_session):
    """find_by_contact_id() retorna None quando contact_id não existe."""
    import uuid

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    assert repo.find_by_contact_id(str(uuid.uuid4())) is None


def test_deal_repository_find_by_contact_id_and_rdstation_id_returns_entity(db_session):
    """find_by_contact_id_and_rd_station_id() retorna o Deal correto."""
    import uuid
    from app.src.adapters.database.models import ContactModel, DealModel

    contact_id = uuid.uuid4()
    contact = ContactModel(id=contact_id, name="Contato Composto")
    deal_model = DealModel(
        rdstation_id="deal-idx-composite-001",
        deal_status="SC",
        contact_id=contact_id,
    )
    db_session.add_all([contact, deal_model])
    db_session.commit()

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    found = repo.find_by_contact_id_and_rd_station_id(str(contact_id), "deal-idx-composite-001")
    assert found is not None
    assert found.rdstation_id == "deal-idx-composite-001"


def test_deal_repository_find_by_contact_id_and_rdstation_id_not_found(db_session):
    """find_by_contact_id_and_rd_station_id() retorna None para combinação inexistente ou uuid inválido."""
    import uuid

    repo = SQLAlchemyDealRepositoryAdapter(db_session)
    assert repo.find_by_contact_id(str(uuid.uuid4())) is None
    assert repo.find_by_contact_id("invalid-uuid") is None
    assert repo.find_by_contact_id_and_rd_station_id(str(uuid.uuid4()), "nao-existe") is None
    assert repo.find_by_contact_id_and_rd_station_id("invalid-uuid", "nao-existe") is None

