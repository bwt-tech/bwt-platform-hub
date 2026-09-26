import json

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.src.core.exceptions import IntegrationError
from app.src.ports.secrets_port import SecretsPort


class AWSSecretsManagerAdapter(SecretsPort):
    def __init__(self, region_name: str, endpoint_url: str | None = None):
        self.client = boto3.client(
            "secretsmanager", region_name=region_name, endpoint_url=endpoint_url
        )

    def get_secret(self, secret_name: str) -> dict[str, str]:
        logger.info(f"Retrieving secret: {secret_name}")
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if "SecretString" in response:
                return json.loads(response["SecretString"])
            else:
                raise IntegrationError(
                    f"Secret {secret_name} does not contain SecretString"
                )
        except ClientError as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise IntegrationError(f"AWS Secrets Manager error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse secret {secret_name} as JSON: {e}")
            raise IntegrationError(f"Invalid JSON format in secret {secret_name}")
