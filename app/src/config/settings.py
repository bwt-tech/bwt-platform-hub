import os

from dotenv import load_dotenv        
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()


def _build_database_url() -> str:
    """
    Monta a DATABASE_URL a partir de variáveis individuais (injetadas pelo ECS
    via SSM Secrets) quando a URL completa não está disponível.

    Ordem de prioridade:
    1. DATABASE_URL definida diretamente (local dev / override manual)
    2. DB_HOST + DB_PORT + DB_NAME + DB_USER + DB_PASSWORD (ECS / produção)
    3. Fallback local para desenvolvimento
    """
    full_url = os.getenv("DATABASE_URL")
    if full_url:
        return full_url

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if all([host, name, user, password]):
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    # Fallback para desenvolvimento local
    return "postgresql://postgres:postgrespassword@localhost:5432/bwt_platform"


class Settings(BaseSettings):
    app_name: str = "bwt-contrib-integrator"
    port: int = 8080
    log_level: str = "INFO"

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_endpoint_url: Optional[str] = os.getenv("AWS_URL")
    aws_secret_name: str = "secrets_bwt"
    s3_bucket_name: str = "process-summary-bwt"

    # Integration Credentials (will be resolved from Secrets Manager or ENV)
    octadesk_api_key: str | None = None
    octadesk_base_url: str | None = None
    octadesk_subdomain: str | None = None
    rdstation_token: str | None = None
    sentry_url: str | None = None
    rdstation_url: str = "https://crm.rdstation.com/api/v1"

    # BWT Platform Configuration
    bwt_url: str = ""
    bwt_email: str | None = None
    bwt_password: str | None = None

    # Database — montada dinamicamente a partir de variáveis individuais ou URL completa
    database_url: str = _build_database_url()

    model_config = {"env_prefix": "APP_"}

    def load_from_secrets_manager(self, secrets_adapter):
        """
        Loads integration credentials from AWS Secrets Manager.
        Falls back to environment variables if retrieval fails.
        """
        try:
            secrets = secrets_adapter.get_secret(self.aws_secret_name)
            self.octadesk_api_key = secrets.get(
                "OCTADESK_API_KEY", self.octadesk_api_key
            )
            self.octadesk_base_url = secrets.get(
                "OCTADESK_BASE_URL", self.octadesk_base_url
            )
            self.octadesk_subdomain = secrets.get(
                "OCTADESK_SUBDOMAIN", self.octadesk_subdomain
            )
            self.rdstation_token = secrets.get("RDSTATION_TOKEN", self.rdstation_token)
            self.sentry_url = secrets.get("SENTRY_URL", self.sentry_url)
            self.bwt_email = secrets.get("BWT_EMAIL", self.bwt_email)
            self.bwt_password = secrets.get("BWT_PASSWORD", self.bwt_password)
            self.bwt_url = secrets.get("BWT_URL", self.bwt_url)

        except Exception as e:
            from loguru import logger

            logger.warning(
                f"Could not load secrets from AWS: {e}. Using environment variables."
            )


settings = Settings()
