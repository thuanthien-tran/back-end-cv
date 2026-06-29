from app.storage.base import StorageService


class MinIOStorageService(StorageService):
    """Placeholder để mô phỏng object storage sau này.

    MVP mặc định dùng LocalStorageService. Khi cần MinIO, implement class này theo cùng interface.
    """

    def save(self, path: str, content: bytes) -> str:
        raise NotImplementedError("MinIOStorageService is not implemented in MVP")

    def read(self, path: str) -> bytes:
        raise NotImplementedError("MinIOStorageService is not implemented in MVP")

    def delete(self, path: str) -> None:
        raise NotImplementedError("MinIOStorageService is not implemented in MVP")

    def exists(self, path: str) -> bool:
        raise NotImplementedError("MinIOStorageService is not implemented in MVP")
