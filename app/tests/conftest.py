import os
from unittest.mock import MagicMock, patch

# Set dummy AWS credentials immediately to prevent any real AWS credential lookup
# during test import/collection.
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Mock Sentry and AWS Secrets Manager during the import of app.main
sentry_patcher = patch("sentry_sdk.init")
sentry_patcher.start()

mock_adapter_instance = MagicMock()
mock_adapter_instance.get_secret.return_value = {}
adapter_patcher = patch(
    "app.src.adapters.outbounds.aws_secrets_adapter.AWSSecretsManagerAdapter",
    return_value=mock_adapter_instance,
)
adapter_patcher.start()

# Force import of app.main under the mocks so its module-level init_configs() is mocked
from app.main import app  # noqa: F401

# Stop the patchers to keep the real classes available for unit tests
adapter_patcher.stop()
sentry_patcher.stop()

import json
from pathlib import Path

import boto3
import pytest
import respx
from moto import mock_aws


@pytest.fixture(scope="session")
def fixtures_path():
    """Returns the absolute path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def load_fixture(fixtures_path):
    """Returns a helper function to load JSON fixtures."""

    def _load(service: str, name: str):
        file_path = fixtures_path / service / f"{name}.json"
        with open(file_path) as f:
            return json.load(f)

    return _load


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(autouse=True)
def block_all_http():
    """Globally block all unmocked HTTPX requests to ensure no real API calls."""
    with respx.mock(assert_all_called=False) as rs:
        yield rs


@pytest.fixture(autouse=True)
def mock_all_aws():
    """Globally apply moto mock to ensure no real AWS interaction."""
    with mock_aws():
        yield


def _skip_scheduler_init(self, *args, **kwargs):
    """Avoid AWS/DB initialization when schedulers are instantiated in app lifespan."""
    self._initialized = True


from app.src.adapters.inbound.background.scheduler import (  # noqa: E402
    SyncronizerScheduler,
    ReverseSyncronizerScheduler,
)

ORIGINAL_START = SyncronizerScheduler.start
ORIGINAL_REVERSE_START = ReverseSyncronizerScheduler.start


@pytest.fixture(autouse=True, scope="session")
def mock_scheduler_lifespan():
    """
    Globally patches the SyncronizerScheduler and ReverseSyncronizerScheduler
    to prevent background threads and AWS calls during any test (unit or functional).
    """
    from app.src.adapters.inbound.background.scheduler import (
        ReverseSyncronizerScheduler,
        SyncronizerScheduler,
    )

    with patch.object(
        SyncronizerScheduler, "__init__", _skip_scheduler_init
    ), patch.object(
        ReverseSyncronizerScheduler, "__init__", _skip_scheduler_init
    ), patch(
        "app.src.adapters.inbound.background.scheduler.SyncronizerScheduler.start"
    ) as mock_start, patch(
        "app.src.adapters.inbound.background.scheduler.ReverseSyncronizerScheduler.start"
    ) as mock_reverse_start:
        mock_start.return_value = None
        mock_reverse_start.return_value = None
        yield mock_start


@pytest.fixture
def mock_aws_secrets(load_fixture):
    """Fixture to mock AWS Secrets Manager using moto."""
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="us-east-1")
        secrets = load_fixture("aws", "secrets_bwt")
        client.create_secret(Name="bwt/platform/hub", SecretString=json.dumps(secrets))
        yield client


@pytest.fixture
def mock_aws_config(load_fixture):
    """Fixture to mock AWS SSM Parameter Store using moto."""
    with mock_aws():
        client = boto3.client("ssm", region_name="us-east-1")
        params = load_fixture("aws", "ssm_parameters")
        for key, value in params.items():
            client.put_parameter(Name=key, Value=value, Type="String")
        yield client


@pytest.fixture
def mock_rdstation_api(load_fixture):
    """Fixture to mock RD Station CRM API using respx."""
    with respx.mock(
        base_url="https://crm.rdstation.com/api/v1", assert_all_called=False
    ) as respx_mock:
        yield respx_mock


@pytest.fixture
def mock_octadesk_api(load_fixture):
    """Fixture to mock Octadesk API using respx."""
    base_url = "https://api.octadesk.example"
    with respx.mock(base_url=base_url, assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def mock_bwt_api():
    """Fixture to mock BWT Platform API using respx."""
    base_url = "https://api.homolog.brasileiroswinetours.com.br"
    with respx.mock(base_url=base_url, assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def db_session():
    """Fixture to provide an in-memory SQLite database session for tests."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.src.adapters.database.connection import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
