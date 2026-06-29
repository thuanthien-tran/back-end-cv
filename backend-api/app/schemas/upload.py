from datetime import datetime
from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_id: str
    job_id: str
    file_type: str
    original_filename: str
    upload_status: str
    file_size: int
    checksum: str


class UploadedFileResponse(BaseModel):
    id: str
    user_id: str
    job_id: str | None
    file_type: str
    original_filename: str
    storage_type: str
    storage_path: str
    mime_type: str
    file_size: int
    checksum: str
    upload_status: str
    created_at: datetime | None
    uploaded_at: datetime | None
    deleted_at: datetime | None
