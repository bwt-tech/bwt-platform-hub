import uuid
from app.src.core.datetime_utils import get_now

from app.src.adapters.database.models import ContactInfoModel, ContactModel
from app.src.domain.entities.contact import Contact
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from sqlalchemy.orm import Session


class SQLAlchemyContactRepositoryAdapter(ContactRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: ContactModel) -> Contact:
        phone = model.info.phone if model.info else None
        email = model.info.email if model.info else None
        deal_id = model.deals[0].rdstation_id if model.deals else None

        return Contact(
            id=str(model.id),
            name=model.name,
            phone=phone or "",
            email=email or "",
            deal_id=deal_id or "",
            octadesk_id=model.octadesk_id,
            rdstation_id=model.rdstation_id,
            bwt_account_id=model.bwt_account_id,
            bwt_contact_id=model.bwt_contact_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, contact: Contact) -> Contact:
        contact_id = uuid.UUID(contact.id) if contact.id else uuid.uuid4()

        # Check if model already exists
        model = self.session.query(ContactModel).filter_by(id=contact_id).first()
        if not model:
            if contact.rdstation_id:
                model = (
                    self.session.query(ContactModel)
                    .filter_by(rdstation_id=contact.rdstation_id)
                    .first()
                )
            if not model and contact.octadesk_id:
                model = (
                    self.session.query(ContactModel)
                    .filter_by(octadesk_id=contact.octadesk_id)
                    .first()
                )

        created_at = contact.created_at or get_now()

        if not model:
            model = ContactModel(
                id=contact_id,
                name=contact.name,
                octadesk_id=contact.octadesk_id,
                rdstation_id=contact.rdstation_id,
                created_at=created_at,
            )
            self.session.add(model)
        else:
            model.name = contact.name
            if contact.octadesk_id:
                model.octadesk_id = contact.octadesk_id
            if contact.rdstation_id:
                model.rdstation_id = contact.rdstation_id
            if contact.bwt_account_id is not None:
                model.bwt_account_id = contact.bwt_account_id
            if contact.bwt_contact_id is not None:
                model.bwt_contact_id = contact.bwt_contact_id
            if contact.created_at:
                model.created_at = contact.created_at

        # Save contact info
        if contact.email or contact.phone:
            info_model = (
                self.session.query(ContactInfoModel)
                .filter_by(contact_id=model.id)
                .first()
            )
            if not info_model:
                info_model = ContactInfoModel(
                    contact_id=model.id,
                    email=contact.email or None,
                    phone=contact.phone or None,
                )
                self.session.add(info_model)
            else:
                info_model.email = contact.email or None
                info_model.phone = contact.phone or None

        self.session.flush()
        self.session.commit()
        return self._to_domain(model)

    def find_by_id(self, contact_id: str) -> Contact | None:
        try:
            uid = uuid.UUID(contact_id)
        except (ValueError, TypeError):
            return None
        model = self.session.query(ContactModel).filter_by(id=uid).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_phone(self, phone: str) -> Contact | None:
        info_model = self.session.query(ContactInfoModel).filter_by(phone=phone).first()
        if not info_model or not info_model.contact:
            return None
        return self._to_domain(info_model.contact)

    def find_by_email(self, email: str) -> Contact | None:
        info_model = self.session.query(ContactInfoModel).filter_by(email=email).first()
        if not info_model or not info_model.contact:
            return None
        return self._to_domain(info_model.contact)

    def find_by_octadesk_id(self, octadesk_id: str) -> Contact | None:
        model = (
            self.session.query(ContactModel).filter_by(octadesk_id=octadesk_id).first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_bwt_contact_id(self, bwt_contact_id: int) -> Contact | None:
        model = (
            self.session.query(ContactModel)
            .filter_by(bwt_contact_id=bwt_contact_id)
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_bwt_account_id(self, bwt_account_id: int) -> Contact | None:
        model = (
            self.session.query(ContactModel)
            .filter_by(bwt_account_id=bwt_account_id)
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)
