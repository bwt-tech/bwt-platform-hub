from loguru import logger

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.deal import Deal
from app.src.domain.entities.deal_stage import DealStage
from app.src.ports.rdstation_port import RDStationPort

MAX_NO_AWNSWER_ACCEPT = 5

class RecurringNoAnswerChecker:
    def __init__(self, rdstation: RDStationPort):
        self._rdstation = rdstation

    def is_recurring(self, name: str, phone: str, no_answer_stage: DealStage) -> bool:
        no_answer_stage_id = no_answer_stage.id
        logger.debug("Looking for NO ANSWER deals")
        try:
            no_answer_deal_wrapper = self._rdstation.get_deals(
                deal_stage_id=no_answer_stage_id
            )
            no_answer_deals = no_answer_deal_wrapper.get("deals", [])
        except IntegrationError as e:
            logger.error(f"Failed to retrieve NO ANSWER deals: {e}")
            return False

        no_answer_count = 0
        for no_answer_deal in no_answer_deals:
            try:
                if Deal.from_dict(no_answer_deal).phone == phone:
                    no_answer_count += 1
                    logger.debug(f"Recurring NO ANSWER contact: {name} - {phone}")
                    deal_id = no_answer_deal.get("id")
                    self._rdstation.put_deal(deal_id, no_answer_stage_id)
                    if no_answer_count == MAX_NO_AWNSWER_ACCEPT:
                        logger.debug(f"CONTACT WITH RECURRING NO ANSWER {phone}")
                        return True
            except ValueError:
                logger.debug(f"IGNORING DEAL {no_answer_deal['id']} to check NO ANSWER")
            except IntegrationError as e:
                logger.error(
                    f"Adapter error processing NO ANSWER deal {no_answer_deal.get('id')}: {e}"
                )

        return False
