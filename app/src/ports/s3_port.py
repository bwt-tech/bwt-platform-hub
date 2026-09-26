from abc import ABC, abstractmethod


class S3Port(ABC):
    @abstractmethod
    def upload_content(
        self, bucket_name: str, file_name: str, content: str
    ) -> None:  # pragma: no cover
        pass
