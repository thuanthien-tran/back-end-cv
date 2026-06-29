import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.ai.factory import get_ai_service
from app.core.config import settings
from app.database.session import SessionLocal
from app.matching.engine import calculate_matching
from app.models.analysis_job import AnalysisJob
from app.models.analysis_result import AnalysisResult
from app.models.uploaded_file import UploadedFile
from app.services.job_event_service import create_job_event
from app.services.text_extractor import extract_text
from app.storage.local import LocalStorageService
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.process_analysis_job", bind=True, max_retries=3, default_retry_delay=30)
def process_analysis_job(self, message: dict):
    db = SessionLocal()
    start_time = time.time()
    job_id = UUID(message["job_id"])

    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            logger.warning("Job not found: %s", job_id)
            return

        if job.status == "completed":
            logger.info("Job already completed, skip: %s", job_id)
            return

        if job.status != "queued":
            logger.info("Job is not queued, skip: %s status=%s", job_id, job.status)
            return

        old_status = job.status
        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        create_job_event(db, job.id, "job_processing", old_status, "processing", "Worker started processing")
        db.commit()

        storage_service = LocalStorageService(settings.upload_dir)
        cv_file = db.query(UploadedFile).filter(UploadedFile.id == job.cv_file_id).first()
        jd_file = db.query(UploadedFile).filter(UploadedFile.id == job.jd_file_id).first()
        if not cv_file or not jd_file:
            raise ValueError("CV or JD file metadata not found")

        cv_content = storage_service.read(cv_file.storage_path)
        jd_content = storage_service.read(jd_file.storage_path)

        cv_text = extract_text(cv_content, cv_file.storage_path)
        jd_text = extract_text(jd_content, jd_file.storage_path)
        if not cv_text.strip() or not jd_text.strip():
            raise ValueError("Could not extract text from CV or JD")

        # Scanned PDF / low-text warning
        warnings = []
        if len(cv_text.strip()) < 100:
            warnings.append("CV text extraction may be incomplete (possible scanned/image file). Results may be less accurate.")
        if len(jd_text.strip()) < 100:
            warnings.append("JD text extraction may be incomplete (possible scanned/image file). Results may be less accurate.")

        matching_result = calculate_matching(cv_text, jd_text)
        matching_result["warnings"] = warnings

        ai_service = get_ai_service()
        try:
            ai_result = ai_service.generate_feedback(matching_result)
            ai_provider = settings.ai_provider
            ai_model = settings.ai_model if settings.ai_provider == "mock" else settings.ollama_model
        except Exception as ai_exc:
            logger.exception("AI service failed, fallback to mock: %s", ai_exc)
            from app.ai.mock_ai import MockAIService

            ai_result = MockAIService().generate_feedback(matching_result)
            ai_provider = "mock_fallback"
            ai_model = "mock-v1"

        processing_time = round(time.time() - start_time, 3)

        raw_result = dict(matching_result)
        raw_result["risk_flags"] = ai_result.get("risk_flags", [])
        raw_result["recommendations"] = ai_result.get("recommendations", {})
        raw_result["alternative_roles"] = ai_result.get("alternative_roles", [])

        result = AnalysisResult(
            job_id=job.id,
            matching_score=matching_result["matching_score"],
            skill_score=matching_result["skill_score"],
            experience_score=matching_result["experience_score"],
            education_score=matching_result["education_score"],
            matched_skills=matching_result["matched_skills"],
            missing_skills=matching_result["missing_skills"],
            extra_skills=matching_result["extra_skills"],
            summary=ai_result.get("summary"),
            strengths=ai_result.get("strengths", []),
            weaknesses=ai_result.get("weaknesses", []),
            improvement_suggestions=ai_result.get("improvement_suggestions", []),
            interview_questions=ai_result.get("interview_questions", []),
            raw_matching_result=raw_result,
            ai_provider=ai_provider,
            ai_model=ai_model,
            processing_time_seconds=processing_time,
        )
        db.add(result)

        old_status = job.status
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.updated_at = datetime.now(timezone.utc)
        create_job_event(db, job.id, "job_completed", old_status, "completed", "Analysis completed successfully")
        db.commit()
        logger.info("Job completed: %s", job_id)

    except IntegrityError as exc:
        db.rollback()
        logger.exception("Integrity error while processing job %s", job_id)
        raise self.retry(exc=exc)

    except Exception as exc:
        db.rollback()
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            old_status = job.status
            job.status = "failed"
            job.error_code = exc.__class__.__name__
            job.error_message = str(exc)[:1000]
            job.failed_at = datetime.now(timezone.utc)
            job.updated_at = datetime.now(timezone.utc)
            job.retry_count = (job.retry_count or 0) + 1
            create_job_event(
                db,
                job.id,
                "job_failed",
                old_status,
                "failed",
                "Worker failed to process job",
                {"error_code": job.error_code},
            )
            db.commit()
        logger.exception("Job failed: %s", job_id)

    finally:
        db.close()
