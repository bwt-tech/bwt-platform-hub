import yaml
from loguru import logger

from app.src.domain.entities.agent_seller_configuration import AgentSellerConfiguration


class AgentSellerConfigLoader:
    """Carrega configurações de agentes e vendedores do agents2seller.yaml."""

    CONFIG_PATH = "app/src/config/agents2seller.yaml"

    def load(self) -> list[AgentSellerConfiguration]:
        try:
            with open(self.CONFIG_PATH) as config_file:
                data = yaml.safe_load(config_file)
                if not data:
                    return []
                return [AgentSellerConfiguration.from_dict(entry) for entry in data]
        except Exception as error:
            logger.error(f"Failed to load agents2seller.yaml: {error}")
            return []
