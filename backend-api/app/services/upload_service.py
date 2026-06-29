import hashlib
import re
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".txt", ".rtf",
                      ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "text/plain",
    "application/rtf",
    "text/rtf",
    "application/octet-stream",
}


def safe_filename(filename: str) -> str:
    filename = filename.strip().replace(" ", "_")
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)
    return filename or "uploaded_file"


def build_storage_path(user_id: UUID, job_id: UUID, file_type: str, filename: str) -> str:
    clean_name = safe_filename(filename)
    return f"users/{user_id}/jobs/{job_id}/{file_type}/{clean_name}"


async def validate_file(file: UploadFile) -> bytes:
    original_filename = file.filename or ""
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: PDF, DOCX, PPTX, TXT, DOC, RTF",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    return content


def calculate_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
