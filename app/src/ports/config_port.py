from abc import ABC, abstractmethod

from app.src.domain.entities.scheduler_config import SchedulerConfig


class ConfigPort(ABC):
    @abstractmethod
    def get_scheduler_config(self) -> SchedulerConfig:
        """
        Retrieves the scheduler configuration from the parameter store.

        Returns:
            A SchedulerConfig entity containing:
            - enabled: bool
            - cron: str
            - batch_size: int

        Raises:
            IntegrationError: If parameters cannot be retrieved.
        """
        pass

    @abstractmethod
    def get_reverse_scheduler_config(self) -> SchedulerConfig:
        """
        Retrieves the reverse scheduler configuration from the parameter store.

        Returns:
            A SchedulerConfig entity containing:
            - enabled: bool
            - cron: str
            - batch_size: int

        Raises:
            IntegrationError: If parameters cannot be retrieved.
        """
        pass

    @abstractmethod
    def get_parameter(self, name: str) -> str:
        """
        Retrieves a single parameter value by name from the parameter store.

        Args:
            name: The SSM parameter path/name.

        Returns:
            The parameter value as string.

        Raises:
            IntegrationError: If parameter cannot be retrieved.
        """
        pass

