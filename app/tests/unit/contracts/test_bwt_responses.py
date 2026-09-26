from app.src.contracts.bwt.responses import AccountsResponse


def test_accounts_response_normalize_dict():
    data = {"count": 1, "results": [{"id": 1, "name": "Account 1"}]}
    res = AccountsResponse.model_validate(data)
    assert res.count == 1
    assert res.results[0].id == 1
