from app.src.domain.policies.deal_status_policy import DealStatusPolicy


def test_should_update_to_with_seller():
    assert DealStatusPolicy.should_update_to_with_seller("SC") is True
    assert DealStatusPolicy.should_update_to_with_seller("CF") is True
    assert DealStatusPolicy.should_update_to_with_seller("EPV") is False


def test_is_in_progress():
    assert DealStatusPolicy.is_in_progress("EPV") is True
    assert DealStatusPolicy.is_in_progress("PE") is True
    assert DealStatusPolicy.is_in_progress("SC") is False


def test_is_final():
    assert DealStatusPolicy.is_final("NR") is True
    assert DealStatusPolicy.is_final("EPV") is False


def test_is_active_in_rd():
    assert DealStatusPolicy.is_active_in_rd("EPV") is True
    assert DealStatusPolicy.is_active_in_rd("SC") is True
    assert DealStatusPolicy.is_active_in_rd("NR") is False
