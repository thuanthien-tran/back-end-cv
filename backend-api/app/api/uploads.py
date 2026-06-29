from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import assert_owner_or_admin, get_current_user
from app.database.session import get_db
from app.models.analysis_job import AnalysisJob
from app.models.uploaded_file import UploadedFile
from app.models.user import User
from app.schemas.upload import UploadedFileResponse, UploadResponse
from app.services.upload_service import build_storage_path, calculate_checksum, validate_file
from app.storage.local import LocalStorageService

router = APIRouter(prefix="/uploads", tags=["Uploads"])
storage_service = LocalStorageService()


def to_file_response(file: UploadedFile) -> UploadedFileResponse:
    return UploadedFileResponse(
        id=str(file.id),
        user_id=str(file.user_id),
        job_id=str(file.job_id) if file.job_id else None,
        file_type=file.file_type,
        original_filename=file.original_filename,
        storage_type=file.storage_type,
        storage_path=file.storage_path,
        mime_type=file.mime_type,
        file_size=file.file_size,
        checksum=file.checksum,
        upload_status=file.upload_status,
        created_at=file.created_at,
        uploaded_at=file.uploaded_at,
        deleted_at=file.deleted_at,
    )


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_file(
    job_id: UUID = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file_type not in ["cv", "jd"]:
        raise HTTPException(status_code=400, detail="file_type must be cv or jd")

    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    assert_owner_or_admin(job.user_id, current_user)

    if job.status not in ["uploaded", "failed"]:
        raise HTTPException(status_code=409, detail="Cannot upload file for this job status")

    content = await validate_file(file)
    checksum = calculate_checksum(content)
    storage_path = build_storage_path(current_user.id, job.id, file_type, file.filename or "uploaded_file")
    saved_path = storage_service.save(storage_path, content)

    uploaded_file = UploadedFile(
        user_id=current_user.id,
        job_id=job.id,
        file_type=file_type,
        original_filename=file.filename or "uploaded_file",
        storage_type="local",
        storage_path=saved_path,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        checksum=checksum,
        upload_status="uploaded",
    )
    db.add(uploaded_file)
    db.flush()

    if file_type == "cv":
        job.cv_file_id = uploaded_file.id
    else:
        job.jd_file_id = uploaded_file.id
    job.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(uploaded_file)

    return UploadResponse(
        file_id=str(uploaded_file.id),
        job_id=str(job.id),
        file_type=uploaded_file.file_type,
        original_filename=uploaded_file.original_filename,
        upload_status=uploaded_file.upload_status,
        file_size=uploaded_file.file_size,
        checksum=uploaded_file.checksum,
    )


@router.get("/{file_id}", response_model=UploadedFileResponse)
def get_upload(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")
    assert_owner_or_admin(uploaded_file.user_id, current_user)
    return to_file_response(uploaded_file)


@router.delete("/{file_id}")
def delete_upload(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="File not found")
    assert_owner_or_admin(uploaded_file.user_id, current_user)

    uploaded_file.upload_status = "deleted"
    uploaded_file.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "File soft deleted"}
