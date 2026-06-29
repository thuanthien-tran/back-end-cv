from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def save(self, path: str, content: bytes) -> str:
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass
