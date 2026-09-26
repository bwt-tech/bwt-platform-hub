import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.scheduler_config import SchedulerConfig
from app.src.ports.config_port import ConfigPort


class AWSParameterStoreAdapter(ConfigPort):
    def __init__(self, region_name: str, endpoint_url: str | None = None):
        self.client = boto3.client(
            "ssm", region_name=region_name, endpoint_url=endpoint_url
        )
        self.paths = {
            "enabled": "/bwt/scheduler/enabled",
            "cron": "/bwt/scheduler/cron",
            "batch_size": "/bwt/scheduler/batch_size",
        }
        self.reverse_paths = {
            "enabled": "/bwt/reverse_scheduler/enabled",
            "cron": "/bwt/reverse_scheduler/cron",
            "batch_size": "/bwt/reverse_scheduler/batch_size",
        }

    def get_scheduler_config(self) -> SchedulerConfig:
        logger.info("Retrieving scheduler configuration from SSM Parameter Store")
        try:
            # Batch fetch parameters by path or names
            names = list(self.paths.values())
            response = self.client.get_parameters(Names=names, WithDecryption=True)

            # Map retrieved parameters back to our keys
            retrieved = {p["Name"]: p["Value"] for p in response.get("Parameters", [])}

            # Fallback logic for missing keys
            enabled = retrieved.get(self.paths["enabled"], "false").lower() == "true"
            cron = retrieved.get(self.paths["cron"], "*/5 * * * *")

            batch_size_str = retrieved.get(self.paths["batch_size"], "10")
            try:
                batch_size = int(batch_size_str)
            except ValueError:
                logger.warning(
                    f"Invalid batch_size in SSM: {batch_size_str}. Falling back to 10."
                )
                batch_size = 10

            return SchedulerConfig(enabled=enabled, cron=cron, batch_size=batch_size)

        except ClientError as e:
            logger.error(f"Failed to retrieve parameters from SSM: {e}")
            return SchedulerConfig(enabled=True, cron="*/5 * * * *", batch_size=10)

    def get_reverse_scheduler_config(self) -> SchedulerConfig:
        logger.info("Retrieving reverse scheduler configuration from SSM Parameter Store")
        try:
            names = list(self.reverse_paths.values())
            response = self.client.get_parameters(Names=names, WithDecryption=True)

            retrieved = {p["Name"]: p["Value"] for p in response.get("Parameters", [])}

            enabled = retrieved.get(self.reverse_paths["enabled"], "true").lower() == "true"
            cron = retrieved.get(self.reverse_paths["cron"], "*/5 * * * *")

            batch_size_str = retrieved.get(self.reverse_paths["batch_size"], "10")
            try:
                batch_size = int(batch_size_str)
            except ValueError:
                logger.warning(
                    f"Invalid reverse batch_size in SSM: {batch_size_str}. Falling back to 10."
                )
                batch_size = 10

            return SchedulerConfig(enabled=enabled, cron=cron, batch_size=batch_size)

        except ClientError as e:
            logger.error(f"Failed to retrieve reverse scheduler parameters from SSM: {e}")
            return SchedulerConfig(enabled=True, cron="*/5 * * * *", batch_size=10)

    def get_parameter(self, name: str) -> str:
        logger.info(f"Retrieving parameter '{name}' from SSM Parameter Store")
        try:
            response = self.client.get_parameter(Name=name, WithDecryption=True)
            return response["Parameter"]["Value"]
        except ClientError as e:
            logger.error(f"Failed to retrieve SSM parameter '{name}': {e}")
            raise IntegrationError(f"Failed to retrieve SSM parameter '{name}': {e}") from e

