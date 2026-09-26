import pytest

from app.src.adapters.outbounds.aws_config_adapter import AWSParameterStoreAdapter
from app.src.domain.entities.scheduler_config import SchedulerConfig


def test_get_scheduler_config_success(mock_aws_config, load_fixture):
    # Prepare - mock_aws_config already has the data from ssm_parameters.json
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    # Execute
    result = adapter.get_scheduler_config()

    # Assert - returns a typed SchedulerConfig entity
    assert isinstance(result, SchedulerConfig)
    assert result.enabled is True
    assert result.cron == "*/5 * * * *"
    assert result.batch_size == 50


def test_get_scheduler_config_fallback_on_missing_parameters(mock_aws_config):
    # Prepare - delete all parameters to simulate missing config
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")
    for param in [
        "/bwt/scheduler/enabled",
        "/bwt/scheduler/cron",
        "/bwt/scheduler/batch_size",
    ]:
        mock_aws_config.delete_parameter(Name=param)

    result = adapter.get_scheduler_config()

    # Assert - should return a typed SchedulerConfig with defaults
    assert isinstance(result, SchedulerConfig)
    assert result.enabled is False
    assert result.batch_size == 10


def test_get_scheduler_config_invalid_int_fallback(mock_aws_config):
    # Prepare
    mock_aws_config.put_parameter(
        Name="/bwt/scheduler/batch_size",
        Value="not-an-int",
        Type="String",
        Overwrite=True,
    )

    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    # Execute
    result = adapter.get_scheduler_config()

    # Assert
    assert isinstance(result, SchedulerConfig)
    assert result.batch_size == 10


def test_get_scheduler_config_client_error_returns_defaults(monkeypatch):
    """Covers the ClientError fallback path in get_scheduler_config."""
    from botocore.exceptions import ClientError

    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    def raise_client_error(*args, **kwargs):
        raise ClientError(
            {"Error": {"Code": "ParameterNotFound", "Message": "not found"}},
            "GetParameters",
        )

    monkeypatch.setattr(adapter.client, "get_parameters", raise_client_error)

    result = adapter.get_scheduler_config()

    assert isinstance(result, SchedulerConfig)
    assert result.enabled is True
    assert result.cron == "*/5 * * * *"
    assert result.batch_size == 10


# --- Reverse Scheduler Config Tests ---

@pytest.fixture
def mock_aws_config_reverse(mock_aws_config):
    """Extends mock_aws_config with reverse scheduler SSM parameters."""
    mock_aws_config.put_parameter(
        Name="/bwt/reverse_scheduler/enabled",
        Value="true",
        Type="String",
    )
    mock_aws_config.put_parameter(
        Name="/bwt/reverse_scheduler/cron",
        Value="0 */2 * * *",
        Type="String",
    )
    mock_aws_config.put_parameter(
        Name="/bwt/reverse_scheduler/batch_size",
        Value="25",
        Type="String",
    )
    return mock_aws_config


def test_get_reverse_scheduler_config_success(mock_aws_config_reverse):
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    result = adapter.get_reverse_scheduler_config()

    assert isinstance(result, SchedulerConfig)
    assert result.enabled is True
    assert result.cron == "0 */2 * * *"
    assert result.batch_size == 25


def test_get_reverse_scheduler_config_does_not_affect_direct_config(mock_aws_config_reverse):
    """Direct scheduler config must remain independent from reverse scheduler config."""
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    direct = adapter.get_scheduler_config()
    reverse = adapter.get_reverse_scheduler_config()

    assert direct.cron == "*/5 * * * *"
    assert direct.batch_size == 50
    assert reverse.cron == "0 */2 * * *"
    assert reverse.batch_size == 25


def test_get_reverse_scheduler_config_fallback_on_missing_parameters(mock_aws_config):
    """When reverse scheduler parameters are absent, defaults must be applied."""
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    result = adapter.get_reverse_scheduler_config()

    assert isinstance(result, SchedulerConfig)
    assert result.enabled is True
    assert result.cron == "*/5 * * * *"
    assert result.batch_size == 10


def test_get_reverse_scheduler_config_invalid_batch_size_fallback(mock_aws_config):
    mock_aws_config.put_parameter(
        Name="/bwt/reverse_scheduler/batch_size",
        Value="not-an-int",
        Type="String",
    )

    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    result = adapter.get_reverse_scheduler_config()

    assert isinstance(result, SchedulerConfig)
    assert result.batch_size == 10


def test_get_reverse_scheduler_config_client_error_returns_defaults(monkeypatch, mock_aws_config):
    """Covers the ClientError fallback path in get_reverse_scheduler_config."""
    from botocore.exceptions import ClientError

    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    original_get_parameters = adapter.client.get_parameters
    call_count = {"n": 0}

    def selective_raise(*args, **kwargs):
        names = kwargs.get("Names", args[0] if args else [])
        if any("reverse" in n for n in names):
            raise ClientError(
                {"Error": {"Code": "InternalServerError", "Message": "fail"}},
                "GetParameters",
            )
        return original_get_parameters(*args, **kwargs)

    monkeypatch.setattr(adapter.client, "get_parameters", selective_raise)

    result = adapter.get_reverse_scheduler_config()

    assert isinstance(result, SchedulerConfig)
    assert result.enabled is True
    assert result.cron == "*/5 * * * *"
    assert result.batch_size == 10


def test_get_parameter_success(mock_aws_config):
    mock_aws_config.put_parameter(
        Name="/bwt/octadesk/keys/mendoza",
        Value="secret_key_123",
        Type="SecureString",
    )
    adapter = AWSParameterStoreAdapter(region_name="us-east-1")
    val = adapter.get_parameter("/bwt/octadesk/keys/mendoza")
    assert val == "secret_key_123"


def test_get_parameter_error_raises_integration_error(monkeypatch, mock_aws_config):
    from botocore.exceptions import ClientError
    from app.src.core.exceptions import IntegrationError

    adapter = AWSParameterStoreAdapter(region_name="us-east-1")

    def raise_err(*args, **kwargs):
        raise ClientError(
            {"Error": {"Code": "ParameterNotFound", "Message": "not found"}},
            "GetParameter",
        )

    monkeypatch.setattr(adapter.client, "get_parameter", raise_err)

    with pytest.raises(IntegrationError, match="Failed to retrieve SSM parameter"):
        adapter.get_parameter("/bwt/octadesk/keys/nonexistent")

