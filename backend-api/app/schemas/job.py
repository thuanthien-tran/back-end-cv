from datetime import datetime
from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobResponse(BaseModel):
    id: str
    user_id: str
    status: str
    cv_file_id: str | None
    jd_file_id: str | None
    error_code: str | None
    error_message: str | None
    retry_count: int
    created_at: datetime | None
    queued_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None


class ScoreItem(BaseModel):
    score: float
    weight: int
    description: str


class CompatibilityInfo(BaseModel):
    overall_score: float
    level: str
    recommendation: str
    message: str
    confidence: float


class SkillsAnalysis(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    skill_match_ratio: float


class CandidateSummary(BaseModel):
    summary: str | None
    strengths: list[str]
    weaknesses: list[str]
    risk_flags: list[str]


class Recommendations(BaseModel):
    for_recruiter: list[str]
    for_candidate: list[str]


class ResultResponse(BaseModel):
    job_id: str
    compatibility: CompatibilityInfo
    score_breakdown: dict[str, ScoreItem]
    skills_analysis: SkillsAnalysis
    candidate_summary: CandidateSummary
    recommendations: Recommendations
    interview_questions: list[str]
    alternative_roles: list[str]
    warnings: list[str]
    metadata: dict
