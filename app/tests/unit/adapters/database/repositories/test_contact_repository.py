from app.src.adapters.database.repositories.contact_repository_adapter import (
    SQLAlchemyContactRepositoryAdapter,
)
from app.src.domain.entities.contact import Contact


def test_contact_repository_save_and_find(db_session):
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    contact = Contact(
        name="Alice",
        phone="5511988888888",
        email="alice@example.com",
        deal_id="deal-1",
        id=None,
        octadesk_id="octa-alice",
        rdstation_id="rd-alice",
    )

    # Test save
    saved = repo.save(contact)
    assert saved.id is not None
    assert saved.name == "Alice"
    assert saved.phone == "5511988888888"
    assert saved.email == "alice@example.com"
    assert saved.octadesk_id == "octa-alice"
    assert saved.rdstation_id == "rd-alice"

    # Test find_by_id
    found = repo.find_by_id(saved.id)
    assert found is not None
    assert found.name == "Alice"

    # Test find_by_phone
    found_phone = repo.find_by_phone("5511988888888")
    assert found_phone is not None
    assert found_phone.id == saved.id

    # Test find_by_email
    found_email = repo.find_by_email("alice@example.com")
    assert found_email is not None
    assert found_email.id == saved.id

    # Test find_by_octadesk_id
    found_octa = repo.find_by_octadesk_id("octa-alice")
    assert found_octa is not None
    assert found_octa.id == saved.id


def test_contact_repository_find_not_found(db_session):
    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    assert (
        repo.find_by_id("non-existent-id") is None
    )  # invalid UUID → caught at uuid.UUID()
    assert repo.find_by_phone("non-existent-phone") is None
    assert repo.find_by_email("non-existent-email") is None
    assert repo.find_by_octadesk_id("non-existent-octadesk") is None


def test_contact_repository_find_by_id_valid_uuid_not_found(db_session):
    """Covers line 87: valid UUID that doesn't exist returns None."""
    import uuid

    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    non_existent_uuid = str(uuid.uuid4())
    assert repo.find_by_id(non_existent_uuid) is None


def test_contact_repository_update_existing(db_session):
    """Covers lines 55-59 and 74-75: saving a contact that already exists updates it."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    # First save
    contact = Contact(
        name="Bob",
        phone="5511977777777",
        email="bob@example.com",
        deal_id="deal-bob",
        id=None,
        octadesk_id="octa-bob",
        rdstation_id="rd-bob",
    )
    saved = repo.save(contact)
    assert saved.name == "Bob"

    # Save again with the same id — triggers the update (else) branch
    updated_contact = Contact(
        name="Bob Updated",
        phone="5511977777777",  # same phone → updates info_model
        email="bob.new@example.com",  # updated email → covers info_model update
        deal_id="deal-bob",
        id=saved.id,
        octadesk_id="octa-bob-new",
        rdstation_id="rd-bob-new",
    )
    updated = repo.save(updated_contact)

    assert updated.name == "Bob Updated"
    assert updated.octadesk_id == "octa-bob-new"
    assert updated.rdstation_id == "rd-bob-new"


def test_contact_repository_timestamp_mapping(db_session):
    from datetime import datetime
    from app.src.adapters.database.models import ContactModel

    now = datetime.now()
    model = ContactModel(
        name="TS Contact",
        octadesk_id="octa-ts-repo-001",
        created_at=now,
        updated_at=now,
    )
    db_session.add(model)
    db_session.commit()

    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    found = repo.find_by_id(str(model.id))
    assert found is not None
    assert found.created_at is not None
    assert found.updated_at is not None

    found_octa = repo.find_by_octadesk_id("octa-ts-repo-001")
    assert found_octa is not None
    assert found_octa.created_at is not None
    assert found_octa.updated_at is not None


def test_contact_repository_timestamp_mapping_none(db_session):
    import uuid
    from app.src.adapters.database.models import ContactModel

    model = ContactModel(
        id=uuid.uuid4(),
        name="No TS Contact",
        octadesk_id="octa-no-ts-repo-001",
    )
    model.created_at = None
    model.updated_at = None

    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    domain_contact = repo._to_domain(model)
    assert domain_contact.created_at is None
    assert domain_contact.updated_at is None


def test_contact_repository_created_at_persistence(db_session):
    from datetime import datetime
    from app.src.core.datetime_utils import get_timezone, get_now
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    # 1. Save with explicit created_at
    explicit_dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=get_timezone())
    contact_explicit = Contact(
        id="",
        name="Explicit Contact",
        phone="",
        email="",
        deal_id="",
        octadesk_id="contact-explicit-ts",
        created_at=explicit_dt,
    )
    saved_explicit = repo.save(contact_explicit)
    saved_explicit_naive = saved_explicit.created_at.replace(tzinfo=None) if saved_explicit.created_at.tzinfo else saved_explicit.created_at
    assert saved_explicit_naive == explicit_dt.replace(tzinfo=None)

    # 2. Save without created_at (should fall back to current local/configured time)
    contact_implicit = Contact(
        id="",
        name="Implicit Contact",
        phone="",
        email="",
        deal_id="",
        octadesk_id="contact-implicit-ts",
        created_at=None,
    )
    before_save = get_now()
    saved_implicit = repo.save(contact_implicit)
    after_save = get_now()
    assert saved_implicit.created_at is not None
    
    saved_implicit_naive = saved_implicit.created_at.replace(tzinfo=None) if saved_implicit.created_at.tzinfo else saved_implicit.created_at
    before_save_naive = before_save.replace(tzinfo=None)
    after_save_naive = after_save.replace(tzinfo=None)
    assert before_save_naive <= saved_implicit_naive <= after_save_naive

    # 3. Update existing Contact without updating created_at
    updated_contact = Contact(
        id=saved_implicit.id,
        name="Implicit Contact Updated",
        phone="",
        email="",
        deal_id="",
        octadesk_id="contact-implicit-ts",
        created_at=None,
    )
    updated = repo.save(updated_contact)
    updated_naive = updated.created_at.replace(tzinfo=None) if updated.created_at.tzinfo else updated.created_at
    assert updated_naive == saved_implicit_naive

    # 4. Update existing Contact with an explicit updated created_at
    new_explicit_dt = datetime(2026, 2, 2, 14, 0, 0, tzinfo=get_timezone())
    updated_contact_with_ts = Contact(
        id=saved_implicit.id,
        name="Implicit Contact Updated",
        phone="",
        email="",
        deal_id="",
        octadesk_id="contact-implicit-ts",
        created_at=new_explicit_dt,
    )
    updated_with_ts = repo.save(updated_contact_with_ts)
    updated_with_ts_naive = updated_with_ts.created_at.replace(tzinfo=None) if updated_with_ts.created_at.tzinfo else updated_with_ts.created_at
    assert updated_with_ts_naive == new_explicit_dt.replace(tzinfo=None)






# ---------------------------------------------------------------------------
# T14 — BWT fields: save() and find_by_bwt_* coverage
# ---------------------------------------------------------------------------


def test_contact_repository_save_persists_bwt_ids(db_session):
    """save() updates bwt_account_id and bwt_contact_id on an existing contact."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    # First: create the contact without BWT IDs
    contact = Contact(
        id=None,
        name="BWT Contact",
        phone="5511900000001",
        email="bwt@example.com",
        deal_id="",
        octadesk_id="octa-bwt-001",
    )
    saved = repo.save(contact)
    assert saved.bwt_account_id is None
    assert saved.bwt_contact_id is None

    # Second: update with BWT IDs — triggers the else (update) branch
    contact_with_bwt = Contact(
        id=saved.id,
        name="BWT Contact",
        phone="5511900000001",
        email="bwt@example.com",
        deal_id="",
        octadesk_id="octa-bwt-001",
        bwt_account_id=1001,
        bwt_contact_id=2002,
    )
    updated = repo.save(contact_with_bwt)

    assert updated.bwt_account_id == 1001
    assert updated.bwt_contact_id == 2002


def test_contact_repository_find_by_bwt_contact_id_returns_entity(db_session):
    """find_by_bwt_contact_id() returns the matching Contact."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    # Create and persist a contact, then set BWT IDs via update
    contact = Contact(
        id=None,
        name="BWT Find Contact",
        phone="5511900000002",
        email="bwt-find@example.com",
        deal_id="",
        octadesk_id="octa-bwt-find-001",
    )
    saved = repo.save(contact)

    contact_with_bwt = Contact(
        id=saved.id,
        name="BWT Find Contact",
        phone="5511900000002",
        email="bwt-find@example.com",
        deal_id="",
        octadesk_id="octa-bwt-find-001",
        bwt_account_id=3003,
        bwt_contact_id=4004,
    )
    repo.save(contact_with_bwt)

    found = repo.find_by_bwt_contact_id(4004)
    assert found is not None
    assert found.id == saved.id
    assert found.bwt_contact_id == 4004


def test_contact_repository_find_by_bwt_contact_id_not_found(db_session):
    """find_by_bwt_contact_id() returns None when no match exists."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    assert repo.find_by_bwt_contact_id(99999) is None


def test_contact_repository_find_by_bwt_account_id_returns_entity(db_session):
    """find_by_bwt_account_id() returns the matching Contact."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)

    contact = Contact(
        id=None,
        name="BWT Account Contact",
        phone="5511900000003",
        email="bwt-acct@example.com",
        deal_id="",
        octadesk_id="octa-bwt-acct-001",
    )
    saved = repo.save(contact)

    contact_with_bwt = Contact(
        id=saved.id,
        name="BWT Account Contact",
        phone="5511900000003",
        email="bwt-acct@example.com",
        deal_id="",
        octadesk_id="octa-bwt-acct-001",
        bwt_account_id=5005,
        bwt_contact_id=6006,
    )
    repo.save(contact_with_bwt)

    found = repo.find_by_bwt_account_id(5005)
    assert found is not None
    assert found.id == saved.id
    assert found.bwt_account_id == 5005


def test_contact_repository_find_by_bwt_account_id_not_found(db_session):
    """find_by_bwt_account_id() returns None when no match exists."""
    repo = SQLAlchemyContactRepositoryAdapter(db_session)
    assert repo.find_by_bwt_account_id(99999) is None
