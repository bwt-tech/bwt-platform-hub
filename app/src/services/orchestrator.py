import json

import yaml
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.deal import Deal
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.entities.pipeline import Pipeline
from app.src.domain.entities.template_configuration import TemplateConfiguration
from app.src.domain.process_summary_tracker import ProcessSummaryTracker
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.config_port import ConfigPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.services.octadesk_lookup import OctadeskLookup
from app.src.services.workflows.existing_contact_workflow import ExistingContactWorkflow
from app.src.services.workflows.new_contact_workflow import NewContactWorkflow
from app.src.services.workflows.recurring_no_answer_checker import (
    RecurringNoAnswerChecker,
)

NO_CONTACT = "SC"
NO_ANSWER = "NR"
CONTACTED = "CF"
PROCESSED = set()


class OrchestratorService:
    def __init__(
        self,
        octadesk_port: OctadeskPort,
        rdstation_port: RDStationPort,
        config_port: ConfigPort | None = None,
        contact_repo: ContactRepositoryPort | None = None,
        deal_repo: DealRepositoryPort | None = None,
        chat_repo: ChatRepositoryPort | None = None,
    ):
        self._octadesk: OctadeskPort = octadesk_port
        self._rdstation: RDStationPort = rdstation_port
        self._config_port: ConfigPort | None = config_port
        self._contact_repo = contact_repo
        self._deal_repo = deal_repo
        self._chat_repo = chat_repo
        self._lookup = OctadeskLookup(octadesk_port, contact_repo)
        self._recurring_checker = RecurringNoAnswerChecker(rdstation_port)
        self._new_contact_workflow = NewContactWorkflow(
            octadesk_port,
            rdstation_port,
            contact_repo=contact_repo,
            deal_repo=deal_repo,
            chat_repo=chat_repo,
        )
        self._existing_contact_workflow = ExistingContactWorkflow(
            octadesk_port,
            rdstation_port,
            self._lookup,
            contact_repo=contact_repo,
            deal_repo=deal_repo,
            chat_repo=chat_repo,
        )
        self.templates = self._load_templates()
        self.batch_size = 50

    def _load_templates(self) -> dict:
        try:
            with open("app/src/config/templates.yaml") as f:
                data = yaml.safe_load(f)
                return data.get("templates", {})
        except Exception as e:
            logger.error(f"Failed to load templates.yaml: {e}")
            return {}

    def _is_recurring_no_answer(
        self, name: str, phone: str, no_answer_stage: DealStage
    ) -> bool:
        return self._recurring_checker.is_recurring(name, phone, no_answer_stage)

    def _get_phone(self, deal: dict) -> str:
        return Deal.normalize_phone(deal["contacts"][0]["phones"][0]["phone"])

    def _has_chat(self, full_phone):
        return self._lookup.has_chat(full_phone)

    def start_process(self) -> None:
        self.templates = self._load_templates()
        logger.info("Starting DEAL and Contact synchronization process")
        try:
            pipelines: list[Pipeline] = self._rdstation.get_deal_pipelines()
        except IntegrationError as e:
            logger.error(f"Failed to get deal pipelines: {e}")
            return

        for pipeline in pipelines:
            pipeline_name = pipeline.name
            try:
                raw_config = self.templates.get(pipeline_name.strip())
                if not raw_config:
                    raise ValueError(
                        f"Could not resolve template configuration for pipeline: '{pipeline_name}'"
                    )
                configuration = TemplateConfiguration.from_dict(
                    pipeline_name, raw_config
                )
                key_attr = configuration.agent.key
                if self._config_port and key_attr and key_attr.startswith("/"):
                    api_key = self._config_port.get_parameter(key_attr)
                else:
                    api_key = key_attr
                self._octadesk.set_api_key(api_key)
            except ValueError as e:
                logger.warning(e)
                continue

            tracker = ProcessSummaryTracker(pipeline_name)
            logger.debug(f"Executing for {pipeline_name} pipeline")

            no_contact_stage = pipeline.get_stage_by_nickname(NO_CONTACT)
            no_answer_stage = pipeline.get_stage_by_nickname(NO_ANSWER)
            contacted_stage = pipeline.get_stage_by_nickname(CONTACTED)

            if no_contact_stage and no_answer_stage and contacted_stage:
                no_contact_stage_id = no_contact_stage.id
                contacted_stage_id = contacted_stage.id

                logger.debug("Looking for NO CONTACT deals")
                try:
                    no_contact_deal_wrapper = self._rdstation.get_deals(
                        deal_stage_id=no_contact_stage_id
                    )
                except IntegrationError as e:  # pragma: no cover
                    logger.error(
                        f"Failed to retrieve NO CONTACT deals: {e}"
                    )  # pragma: no cover
                    continue  # pragma: no cover

                deals = no_contact_deal_wrapper.get("deals", [])

                if self.batch_size > 0:
                    logger.info(
                        f"Limiting synchronization to first {self.batch_size} deals"
                    )
                    deals = deals[: self.batch_size]

                for deal_dict in deals:
                    try:
                        deal = Deal.from_dict(deal_dict)

                        if deal.phone in PROCESSED:
                            continue  # pragma: no cover

                        contact = deal.to_contact()
                        logger.debug(
                            f"Verifying lead '{contact.name}' '{contact.phone}' '{contact.email}'"
                        )

                        if self._recurring_checker.is_recurring(
                            contact.name, contact.phone, no_answer_stage
                        ):
                            logger.info(
                                f"Contact with recurring no answer '{contact.name}' "
                                f"'{contact.phone}' '{contact.email}'"
                            )
                            tracker.record_recurring_no_answer(contact)
                            continue

                        if not self._lookup.has_contact(deal.phone):
                            self._new_contact_workflow.execute(
                                deal,
                                contact,
                                configuration,
                                contacted_stage_id,
                                CONTACTED,
                                tracker,
                            )
                        else:
                            self._existing_contact_workflow.execute(
                                deal,
                                contact,
                                configuration,
                                contacted_stage_id,
                                CONTACTED,
                                tracker,
                            )
                        tracker.record_deal_processed()
                        PROCESSED.add(deal.phone)
                    except ValueError as e:
                        tracker.record_deal_failed({"deal_id": deal_dict.get("id")})
                        logger.warning(f"Skipping deal: {e}")
                    except IntegrationError as e:
                        logger.error(
                            f"External API error while processing deal {deal_dict.get('id')}. "
                            f"Skipping out. Error: {e}"
                        )
                    except SQLAlchemyError as e:
                        tracker.record_deal_failed({"deal_id": deal_dict.get("id")})
                        logger.error(
                            f"Database error while persisting deal {deal_dict.get('id')}. "
                            f"Error: {e}"
                        )
