import uuid
from app.src.core.datetime_utils import get_now

from app.src.adapters.database.models import DealModel
from app.src.domain.entities.deal import Deal
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from sqlalchemy.orm import Session


class SQLAlchemyDealRepositoryAdapter(DealRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: DealModel) -> Deal:
        contact_phone = ""
        contact_email = ""
        contact_name = "Unknown"
        if model.contact:
            contact_name = model.contact.name
            if model.contact.info:
                contact_phone = model.contact.info.phone or ""
                contact_email = model.contact.info.email or ""

        return Deal(
            deal_id=model.rdstation_id or "",
            name=contact_name,
            phone=contact_phone,
            email=contact_email,
            deal_source_name="RD",
            deal_campaign_name="Campaign",
            id=str(model.id),
            rdstation_id=model.rdstation_id,
            contact_id=str(model.contact_id) if model.contact_id else None,
            deal_status=model.deal_status,
            bwt_deal_id=model.bwt_deal_id,
            bwt_responsible_id=model.bwt_responsible_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, deal: Deal) -> Deal:
        deal_id = uuid.UUID(deal.id) if deal.id else uuid.uuid4()
        contact_uuid = uuid.UUID(deal.contact_id) if deal.contact_id else None

        model = self.session.query(DealModel).filter_by(id=deal_id).first()
        if not model and deal.rdstation_id:
            model = (
                self.session.query(DealModel)
                .filter_by(rdstation_id=deal.rdstation_id)
                .first()
            )

        created_at = deal.created_at or get_now()

        if not model:
            model = DealModel(
                id=deal_id,
                rdstation_id=deal.rdstation_id,
                contact_id=contact_uuid,
                deal_status=deal.deal_status or "SC",
                created_at=created_at,
            )
            self.session.add(model)
        else:
            if deal.rdstation_id:
                model.rdstation_id = deal.rdstation_id
            if contact_uuid:
                model.contact_id = contact_uuid
            if deal.deal_status:
                model.deal_status = deal.deal_status
            if deal.bwt_deal_id is not None:
                model.bwt_deal_id = deal.bwt_deal_id
            if deal.bwt_responsible_id is not None:
                model.bwt_responsible_id = deal.bwt_responsible_id
            if deal.created_at:
                model.created_at = deal.created_at
        self.session.commit()
        self.session.flush()
        return self._to_domain(model)

    def find_by_id(self, deal_id: str) -> Deal | None:
        try:
            uid = uuid.UUID(deal_id)
        except (ValueError, TypeError):
            return None
        model = self.session.query(DealModel).filter_by(id=uid).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_rdstation_id(self, rdstation_id: str) -> Deal | None:
        model = (
            self.session.query(DealModel).filter_by(rdstation_id=rdstation_id).first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_contact_id(self, contact_id: str) -> Deal | None:
        try:
            contact_uuid = uuid.UUID(contact_id)
        except (ValueError, TypeError):
            return None
        model = (
            self.session.query(DealModel).filter_by(contact_id=contact_uuid).first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_contact_id_and_rd_station_id(self, contact_id: str, rdstation_id: str) -> Deal | None:
        try:
            contact_uuid = uuid.UUID(contact_id)
        except (ValueError, TypeError):
            return None
        model = (
            self.session.query(DealModel).filter_by(contact_id=contact_uuid, rdstation_id=rdstation_id).first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_bwt_deal_id(self, bwt_deal_id: int) -> Deal | None:
        model = (
            self.session.query(DealModel).filter_by(bwt_deal_id=bwt_deal_id).first()
        )
        if not model:
            return None
        return self._to_domain(model)
