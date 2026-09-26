from typing import Optional, List
from loguru import logger
from app.src.contracts.bwt.requests import DealStage
from app.src.contracts.bwt.responses import (
    AccountContactsResponse,
    AccountContactResponse,
    AccountResponse,
    CreateDealResponse,
    DealsQueryResponse,
    DealQueryResponse,
    CompanyUserResponse
)
from app.src.domain.entities.bwt_sync_result import BWTSyncResult
from app.src.ports.bwt_port import BWTPort

ACTIVE_BWT_DEAL_STAGES = frozenset(
    [
        DealStage.NEW_DEAL,
        DealStage.CONTACTED,
        DealStage.QUOTE,
        DealStage.QUOTE_SENT,
    ]
)


class BWTReverseSyncService:
    """Sincroniza conta, contato e negociação na plataforma BWT."""

    def sync(
        self,
        bwt_port: BWTPort,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
        seller: str,
        supervisor: str,
    ) -> BWTSyncResult:
        account, contact = self._resolve_or_create_account_and_contact(
            bwt_port, contact_name, contact_email, contact_phone
        )
        deal = self._resolve_or_create_active_deal(bwt_port, account, contact)
        responsible = self._advance_deal_and_assign_seller(bwt_port, deal, seller, supervisor)
        return BWTSyncResult(
            account_id=account.id,
            contact_id=contact.id,
            deal_id=deal.id,
            responsible_id=responsible.id if responsible else None,
        )

    def _resolve_or_create_account_and_contact(
        self,
        bwt_port: BWTPort,
        contact_name: str,
        contact_email: str,
        contact_phone: str,
    ) -> tuple[AccountResponse, AccountContactResponse]:
        account, contact = self._find_account_and_contact_by_phone(
            bwt_port, contact_name, contact_phone
        )
        if account is None:
            account = bwt_port.create_account(name=contact_name)
        if contact is None:
            contact = bwt_port.create_contact(
                account_id=account.id,
                name=contact_name,
                email=contact_email,
                phone=contact_phone,
            )
        return account, contact

    def _find_account_and_contact_by_phone(
        self,
        bwt_port: BWTPort,
        contact_name: str,
        contact_phone: str,
    ) -> tuple[AccountResponse | None, AccountContactResponse | None]:
        contacts_query_response: AccountContactsResponse = bwt_port.get_contacts_by_phone(contact_phone)
        if not contacts_query_response or contacts_query_response.count == 0 or not contacts_query_response.results:
            return None, None

        contact = contacts_query_response.results[0]
        account = contact.accounts[0] if len(contact.accounts) > 0 else None
        return account, contact

    def _resolve_or_create_active_deal(
        self,
        bwt_port: BWTPort,
        account: AccountResponse,
        contact: AccountContactResponse,
    ) -> CreateDealResponse:
        active_deal = self._find_active_deal(bwt_port, account.id)
        if active_deal is  None:
            active_deal = bwt_port.create_deal(
                contact_id=contact.id,
                account_id=account.id,
            )
        return bwt_port.get_deal(active_deal.id)

    def _find_active_deal(
        self, bwt_port: BWTPort, account_id: str | int
    ) -> CreateDealResponse | DealQueryResponse | None:
        for deals_page in self._fetch_all_deals(bwt_port, account_id):
            for deal in (deals_page.results or []):
                if deal.stage in ACTIVE_BWT_DEAL_STAGES:
                    return deal
        return None

    def _fetch_all_deals(
        self, bwt_port: BWTPort, account_id: str | int
    ) -> list[DealsQueryResponse]:
        pages: list[DealsQueryResponse] = []
        page = 1
        while True:
            deals_page = bwt_port.get_deals(account_id=account_id, page=page)
            if deals_page.count > 0:
                pages.append(deals_page)
            if deals_page.next is None:
                break
            page += 1
        return pages

    def _advance_deal_and_assign_seller(
        self, bwt_port: BWTPort, deal: CreateDealResponse | DealQueryResponse, seller: str, supervisor: str
    ) -> Optional[CompanyUserResponse]:
        if deal.stage is None:
            logger.warning(f"Deal {deal.id} has no stage — skipping status advance.")
            return None
        if deal.stage != DealStage.NEW_DEAL:
            return None
        responsible = self._assign_seller_if_unique(bwt_port=bwt_port, deal_id=deal.id, seller=seller, supervisor_name=supervisor)
        bwt_port.update_deal_status(deal_id=deal.id, stage=DealStage.CONTACTED)
        return responsible

    def _get_responsible(self,bwt_port: BWTPort, seller_name: str, supervisor_name:str) -> Optional[CompanyUserResponse]:
        sellers = bwt_port.get_company_users(search_term=seller_name).results
        
        filtered_sellers: List[CompanyUserResponse]  = list(filter(lambda s: s.is_active == True ,sellers))
        if len(filtered_sellers) == 1:
            return filtered_sellers[0]
        
        supervisors = bwt_port.get_company_users(search_term=supervisor_name).results
        filtered_supervisors: List[CompanyUserResponse] = list(filter(lambda s: s.is_active == True ,supervisors))
        if len(filtered_supervisors) == 1:
            return filtered_supervisors[0]
        return None

    def _assign_seller_if_unique(
        self, bwt_port: BWTPort, deal_id: str | int, seller: str, supervisor_name: str
    ) -> Optional[CompanyUserResponse]:
        responsible = self._get_responsible(bwt_port=bwt_port, seller_name=seller, supervisor_name=supervisor_name)
        if responsible:
            bwt_port.set_deal_responsible(
                deal_id=deal_id, responsible_id=responsible.id
            )
        return responsible
