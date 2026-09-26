from abc import ABC, abstractmethod


class SecretsPort(ABC):
    @abstractmethod
    def get_secret(self, secret_name: str) -> dict[str, str]:
        """
        Retrieves a dictionary of secrets from the underlying secrets manager.

        Args:
            secret_name: The name or path of the secret to retrieve.

        Returns:
            A dictionary containing the secret key-value pairs.

        Raises:
            IntegrationError: If the secret cannot be retrieved or parsed.
        """
        pass
