from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import assert_owner_or_admin, get_current_user
from app.database.session import get_db
from app.models.analysis_job import AnalysisJob
from app.models.analysis_result import AnalysisResult
from app.models.uploaded_file import UploadedFile
from app.models.user import User
from app.queue.celery_queue import queue_service
from app.schemas.job import JobCreateResponse, JobResponse, ResultResponse
from app.services.job_event_service import create_job_event

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def to_job_response(job: AnalysisJob) -> JobResponse:
    return JobResponse(
        id=str(job.id),
        user_id=str(job.user_id),
        status=job.status,
        cv_file_id=str(job.cv_file_id) if job.cv_file_id else None,
        jd_file_id=str(job.jd_file_id) if job.jd_file_id else None,
        error_code=job.error_code,
        error_message=job.error_message,
        retry_count=job.retry_count or 0,
        created_at=job.created_at,
        queued_at=job.queued_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        failed_at=job.failed_at,
    )


@router.post("", response_model=JobCreateResponse, status_code=201)
def create_job(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = AnalysisJob(user_id=current_user.id, status="uploaded")
    db.add(job)
    db.flush()
    create_job_event(db, job.id, "job_created", None, "uploaded", "Job created")
    db.commit()
    db.refresh(job)
    return JobCreateResponse(job_id=str(job.id), status=job.status)


@router.get("")
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(AnalysisJob).filter(AnalysisJob.user_id == current_user.id)
    total = query.count()
    jobs = query.order_by(AnalysisJob.created_at.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": [to_job_response(job).model_dump() for job in jobs]}


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    assert_owner_or_admin(job.user_id, current_user)
    return to_job_response(job)


@router.post("/{job_id}/enqueue")
def enqueue_job(job_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    assert_owner_or_admin(job.user_id, current_user)

    if job.status == "completed":
        raise HTTPException(status_code=409, detail="Job already completed")
    if job.status in ["queued", "processing"]:
        raise HTTPException(status_code=409, detail=f"Job already {job.status}")
    if not job.cv_file_id or not job.jd_file_id:
        raise HTTPException(status_code=400, detail="CV and JD are required before enqueue")

    cv_file = db.query(UploadedFile).filter(UploadedFile.id == job.cv_file_id).first()
    jd_file = db.query(UploadedFile).filter(UploadedFile.id == job.jd_file_id).first()
    if not cv_file or not jd_file:
        raise HTTPException(status_code=404, detail="CV or JD file metadata not found")
    if cv_file.upload_status != "uploaded" or jd_file.upload_status != "uploaded":
        raise HTTPException(status_code=400, detail="CV and JD files must be uploaded")

    old_status = job.status
    job.status = "queued"
    job.queued_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
    job.error_code = None
    job.error_message = None
    create_job_event(db, job.id, "job_queued", old_status, "queued", "Job enqueued")
    db.commit()

    queue_service.enqueue_analysis_job(
        {
            "job_id": str(job.id),
            "user_id": str(current_user.id),
            "cv_file_id": str(cv_file.id),
            "jd_file_id": str(jd_file.id),
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "attempt": (job.retry_count or 0) + 1,
        }
    )
    return {"job_id": str(job.id), "status": job.status}


@router.get("/{job_id}/result", response_model=ResultResponse)
def get_job_result(job_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    assert_owner_or_admin(job.user_id, current_user)
    if job.status != "completed":
        raise HTTPException(status_code=409, detail=f"Job is not completed. Current status: {job.status}")

    result = db.query(AnalysisResult).filter(AnalysisResult.job_id == job.id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    raw = result.raw_matching_result or {}
    skill_score = float(result.skill_score) if result.skill_score is not None else 0.0
    experience_score = float(result.experience_score) if result.experience_score is not None else 60.0
    education_score = float(result.education_score) if result.education_score is not None else 60.0
    keyword_score = raw.get("keyword_score", skill_score)
    cv_quality_score = raw.get("cv_quality_score", 70.0)

    compatibility = raw.get("compatibility", {})
    if not compatibility:
        from app.matching.engine import get_compatibility_level
        compatibility = get_compatibility_level(float(result.matching_score))

    score_breakdown = raw.get("score_breakdown", {
        "skill_match": {"score": skill_score, "weight": 40, "description": "Mức độ khớp kỹ năng giữa CV và JD"},
        "experience_match": {"score": experience_score, "weight": 25, "description": "Mức độ phù hợp về kinh nghiệm làm việc"},
        "education_match": {"score": education_score, "weight": 15, "description": "Mức độ phù hợp về học vấn"},
        "keyword_match": {"score": keyword_score, "weight": 10, "description": "Mức độ khớp các từ khóa quan trọng trong JD"},
        "cv_quality": {"score": cv_quality_score, "weight": 10, "description": "Chất lượng trình bày và mức độ rõ ràng của CV"},
    })

    return ResultResponse(
        job_id=str(job.id),
        compatibility={
            "overall_score": float(result.matching_score),
            "level": compatibility.get("level", "N/A"),
            "recommendation": compatibility.get("recommendation", "N/A"),
            "message": compatibility.get("message", ""),
            "confidence": 0.82,
        },
        score_breakdown=score_breakdown,
        skills_analysis={
            "matched_skills": result.matched_skills or [],
            "missing_skills": result.missing_skills or [],
            "extra_skills": result.extra_skills or [],
            "skill_match_ratio": skill_score,
        },
        candidate_summary={
            "summary": result.summary,
            "strengths": result.strengths or [],
            "weaknesses": result.weaknesses or [],
            "risk_flags": raw.get("risk_flags", []),
        },
        recommendations={
            "for_recruiter": raw.get("recommendations", {}).get("for_recruiter", []) if raw else [],
            "for_candidate": result.improvement_suggestions or [],
        },
        interview_questions=result.interview_questions or [],
        alternative_roles=raw.get("alternative_roles", []) if raw else [],
        warnings=raw.get("warnings", []) if raw else [],
        metadata={
            "ai_provider": result.ai_provider,
            "ai_model": result.ai_model,
            "processing_time_seconds": float(result.processing_time_seconds) if result.processing_time_seconds is not None else None,
        },
    )


@router.delete("/{job_id}")
def cancel_job(job_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    assert_owner_or_admin(job.user_id, current_user)
    if job.status in ["completed", "processing"]:
        raise HTTPException(status_code=409, detail="Cannot cancel completed or processing job")
    old_status = job.status
    job.status = "cancelled"
    job.updated_at = datetime.now(timezone.utc)
    create_job_event(db, job.id, "job_cancelled", old_status, "cancelled", "Job cancelled")
    db.commit()
    return {"message": "Job cancelled"}
