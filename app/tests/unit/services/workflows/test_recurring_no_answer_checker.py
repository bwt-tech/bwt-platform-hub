from unittest.mock import MagicMock
import pytest

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.deal_stage import DealStage
from app.src.services.workflows.recurring_no_answer_checker import (
    RecurringNoAnswerChecker,
)


def test_recurring_no_answer_checker_reaches_max_count():
    mock_rd = MagicMock()
    stage = DealStage(id="stage-no-answer", nickname="NR")
    matching_deal = {
        "id": "deal-1",
        "name": "Maria",
        "contacts": [{"phones": [{"phone": "11999998888"}]}],
        "deal_source": {"name": "Source"},
    }
    mock_rd.get_deals.return_value = {"deals": [matching_deal] * 5}

    checker = RecurringNoAnswerChecker(mock_rd)
    assert checker.is_recurring("Maria", "11999998888", stage) is True
    assert mock_rd.put_deal.call_count == 5


def test_recurring_no_answer_checker_integration_error_on_get_deals():
    mock_rd = MagicMock()
    stage = DealStage(id="stage-no-answer", nickname="NR")
    mock_rd.get_deals.side_effect = IntegrationError("API error")

    checker = RecurringNoAnswerChecker(mock_rd)
    assert checker.is_recurring("Maria", "11999998888", stage) is False


def test_recurring_no_answer_checker_handles_value_error_and_put_deal_integration_error():
    mock_rd = MagicMock()
    stage = DealStage(id="stage-no-answer", nickname="NR")
    invalid_deal = {"id": "invalid-deal"}  # Will raise ValueError in Deal.from_dict
    valid_deal = {
        "id": "valid-deal",
        "name": "Maria",
        "contacts": [{"phones": [{"phone": "11999998888"}]}],
        "deal_source": {"name": "Source"},
    }
    mock_rd.get_deals.return_value = {"deals": [invalid_deal, valid_deal]}
    mock_rd.put_deal.side_effect = IntegrationError("Put error")

    checker = RecurringNoAnswerChecker(mock_rd)
    assert checker.is_recurring("Maria", "11999998888", stage) is False
