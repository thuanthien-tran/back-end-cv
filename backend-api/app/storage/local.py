from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageService


class LocalStorageService(StorageService):
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.upload_dir)

    def _full_path(self, path: str) -> Path:
        normalized = Path(path)
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError("Invalid storage path")
        return self.base_dir / normalized

    def save(self, path: str, content: bytes) -> str:
        full_path = self._full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return path

    def read(self, path: str) -> bytes:
        return self._full_path(path).read_bytes()

    def delete(self, path: str) -> None:
        full_path = self._full_path(path)
        if full_path.exists():
            full_path.unlink()

    def exists(self, path: str) -> bool:
        return self._full_path(path).exists()
