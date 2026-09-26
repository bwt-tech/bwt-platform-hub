import json

import boto3
import pytest
from app.src.adapters.outbounds.aws_s3_adapter import AWSS3Adapter
from app.src.core.exceptions import IntegrationError
from moto import mock_aws

BUCKET_NAME = "test-bucket"
REGION = "us-east-1"


@pytest.fixture
def mock_s3():
    """Fixture that provides a moto-mocked S3 environment with a pre-created bucket."""
    with mock_aws():
        client = boto3.client("s3", region_name=REGION)
        client.create_bucket(Bucket=BUCKET_NAME)
        yield client


def test_upload_content_success(mock_s3):
    """upload_content writes the payload to S3 and we can read it back."""
    adapter = AWSS3Adapter(region_name=REGION)
    content = json.dumps({"pipeline": "Test", "deals_processed": 5}, indent=2)

    adapter.upload_content(
        bucket_name=BUCKET_NAME,
        file_name="report_20260601.json",
        content=content,
    )

    # Verify the object was actually written
    obj = mock_s3.get_object(Bucket=BUCKET_NAME, Key="report_20260601.json")
    body = obj["Body"].read().decode("utf-8")
    assert json.loads(body) == {"pipeline": "Test", "deals_processed": 5}


def test_upload_content_invalid_bucket(mock_s3):
    """upload_content raises IntegrationError when the bucket does not exist."""
    adapter = AWSS3Adapter(region_name=REGION)

    with pytest.raises(IntegrationError) as exc:
        adapter.upload_content(
            bucket_name="nonexistent-bucket",
            file_name="report.json",
            content="{}",
        )

    assert "AWS S3 error" in str(exc.value)


def test_upload_content_overwrites_existing_key(mock_s3):
    """Uploading to the same key overwrites the previous content."""
    adapter = AWSS3Adapter(region_name=REGION)

    adapter.upload_content(BUCKET_NAME, "report.json", '{"version": 1}')
    adapter.upload_content(BUCKET_NAME, "report.json", '{"version": 2}')

    obj = mock_s3.get_object(Bucket=BUCKET_NAME, Key="report.json")
    body = obj["Body"].read().decode("utf-8")
    assert json.loads(body) == {"version": 2}
