from typing import Any, Optional
import traceback

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.policies.deal_status_policy import WITH_SELLER
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.domain.services.pipeline_scope_resolver import PipelineScopeResolver
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.agent_seller_config_loader import AgentSellerConfigLoader
from app.src.services.factories.bwt_port_factory import BWTPortFactory
from app.src.services.octadesk_lookup import OctadeskLookup
from app.src.services.workflows.bwt_reverse_sync_service import BWTReverseSyncService
from app.src.services.workflows.rd_station_reverse_sync_service import (
    RDStationReverseSyncService,
)
from app.src.services.workflows.reverse_sync_workflow import ReverseSyncWorkflow


PROCESSED: set[str] = set()


class OrchestratorReverseService:
    """Orquestra a sincronização reversa Octadesk -> RD Station & BWT."""

    def __init__(
        self,
        octadesk_port: OctadeskPort,
        rdstation_port: RDStationPort,
        contact_repo: Optional[ContactRepositoryPort] = None,
        deal_repo: Optional[DealRepositoryPort] = None,
        chat_repo: Optional[ChatRepositoryPort] = None,
        bwt_factory: Optional[BWTPortFactory] = None,
        config_loader: Optional[AgentSellerConfigLoader] = None,
        scope_resolver: Optional[PipelineScopeResolver] = None,
        reverse_sync_workflow: Optional[ReverseSyncWorkflow] = None,
    ):
        self._octadesk = octadesk_port
        self._rdstation = rdstation_port
        self._bwt_factory = bwt_factory or BWTPortFactory()
        self._config_loader = config_loader or AgentSellerConfigLoader()
        self._scope_resolver = scope_resolver or PipelineScopeResolver()
        self._reverse_sync_workflow = reverse_sync_workflow or self._build_workflow(
            octadesk_port=octadesk_port,
            rdstation_port=rdstation_port,
            contact_repo=contact_repo,
            deal_repo=deal_repo,
            chat_repo=chat_repo,
        )
        self.batch_size: int = 0

    def start_process(self) -> None:
        logger.info("Starting REVERSE synchronization process (Octadesk -> RD Station & BWT)")
        try:
            pipelines: list[Pipeline] = self._rdstation.get_deal_pipelines()
        except IntegrationError as error:
            logger.error(f"Failed to get deal pipelines: {error}")
            return

        agent_configs = self._config_loader.load()

        for agent_config in agent_configs:
            logger.info(f"Processing pipeline agent: {agent_config}")
            if not agent_config.has_agent_id:
                continue

            chats = self._fetch_chats_for_agent(agent_config.agent_id)
            if chats is None:
                continue

            if self.batch_size > 0:
                logger.info(
                    f"Limiting reverse synchronization to first {self.batch_size} chats"
                )
                chats = chats

            count = 0
            logger.info(
                    f"Chats encontrados para o agent {agent_config.seller}: {len(chats)}"
                )
            for chat in chats:
                if self.batch_size > 0 and count >= self.batch_size:
                    break
                
                if chat["id"] in PROCESSED:
                    continue  # pragma: no cover
                self._process_chat(chat, agent_config, pipelines)
                PROCESSED.add(chat["id"])
                logger.info(
                    f"Processado chat {chat['id']}"
                )
                count += 1

    def _fetch_chats_for_agent(
        self, agent_id: str
    ) -> Optional[list[dict[str, Any]]]:
        try:
            chats = []
            page = 1
            retrieved_chats = self._octadesk.get_chats_in_progress(page=page, agent_id=agent_id)
            chats += retrieved_chats
            while len(retrieved_chats) > 0:
                page += 1
                retrieved_chats = self._octadesk.get_chats_in_progress(page=page, agent_id=agent_id)
                chats += retrieved_chats

            return chats
        except IntegrationError as error:
            logger.error(
                f"Failed to get chats in progress for agent {agent_id}: {error}"
            )
            return None

    def _process_chat(
        self,
        chat: dict[str, Any],
        agent_config,
        pipelines: list[Pipeline],
    ) -> None:
        context = self._scope_resolver.resolve(agent_config, chat, pipelines)
        if context is None:
            return

        with_seller_stage = context.pipeline.get_stage_by_nickname(WITH_SELLER)
        if with_seller_stage is None:
            logger.warning(
                f"Stage WITH_SELLER ('{WITH_SELLER}') not found in pipeline: "
                f"{context.pipeline.name}"
            )
            return

        bwt_port = self._bwt_factory.create(context.scope)
        try:
            self._reverse_sync_workflow.execute(
                chat=chat,
                seller=agent_config.seller,
                supervisor=agent_config.supervisor,
                with_seller_stage_id=with_seller_stage.id,
                bwt_port=bwt_port,
            )
        except IntegrationError as error:
            error_string = traceback.format_exc()

            logger.error(
                f"External API error processing chat {chat.get('id')}: {error}: {error_string}"
            )
        except SQLAlchemyError as error:
            error_string = traceback.format_exc()
            logger.error(
                f"Database error processing chat {chat.get('id')}: {error}: {error_string}"
            )
        except Exception as error:
            error_string = traceback.format_exc()

            logger.error(
                f"Unexpected error processing chat {chat.get('id')}: {error}: {error_string}"
            )

    @staticmethod
    def _build_workflow(
        octadesk_port: OctadeskPort,
        rdstation_port: RDStationPort,
        contact_repo: Optional[ContactRepositoryPort],
        deal_repo: Optional[DealRepositoryPort],
        chat_repo: Optional[ChatRepositoryPort],
    ) -> ReverseSyncWorkflow:
        octadesk_lookup = OctadeskLookup(octadesk_port, contact_repo)
        return ReverseSyncWorkflow(
            octadesk_lookup=octadesk_lookup,
            rd_sync=RDStationReverseSyncService(rdstation_port, deal_repo),
            bwt_sync=BWTReverseSyncService(),
            contact_repo=contact_repo,
            deal_repo=deal_repo,
            chat_repo=chat_repo,
        )
