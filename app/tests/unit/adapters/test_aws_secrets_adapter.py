import pytest
from app.src.adapters.outbounds.aws_secrets_adapter import AWSSecretsManagerAdapter
from app.src.core.exceptions import IntegrationError


def test_get_secret_success(mock_aws_secrets, load_fixture):
    # Prepare
    secrets_data = load_fixture("aws", "secrets_bwt")
    adapter = AWSSecretsManagerAdapter(region_name="us-east-1")

    # Execute
    result = adapter.get_secret("bwt/platform/hub")

    # Assert
    assert result == secrets_data


def test_get_secret_not_found(mock_aws_secrets):
    # Prepare
    adapter = AWSSecretsManagerAdapter(region_name="us-east-1")

    # Execute & Assert
    with pytest.raises(IntegrationError) as exc:
        adapter.get_secret("invalid-secret")

    assert "AWS Secrets Manager error" in str(exc.value)


def test_get_secret_invalid_json(mock_aws_secrets):
    # Prepare
    # Create a secret with non-json content via the mocked client
    mock_aws_secrets.create_secret(Name="bad-json-secret", SecretString="not-a-json")

    adapter = AWSSecretsManagerAdapter(region_name="us-east-1")

    # Execute & Assert
    with pytest.raises(IntegrationError) as exc:
        adapter.get_secret("bad-json-secret")

    assert "Invalid JSON format" in str(exc.value)


def test_get_secret_missing_string(mock_aws_secrets):
    # Prepare
    # Binary secrets are not supported by our adapter currently,
    # but we test the missing SecretString case.
    mock_aws_secrets.create_secret(Name="no-string-secret", SecretBinary=b"some-bytes")

    adapter = AWSSecretsManagerAdapter(region_name="us-east-1")

    # Execute & Assert
    with pytest.raises(IntegrationError) as exc:
        adapter.get_secret("no-string-secret")

    assert "does not contain SecretString" in str(exc.value)
