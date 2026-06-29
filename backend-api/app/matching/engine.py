import re

SKILL_SYNONYMS = {
    "js": "javascript",
    "py": "python",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "fast api": "fastapi",
    "fast-api": "fastapi",
    "node.js": "nodejs",
    "node js": "nodejs",
}

KNOWN_SKILLS = {
    "python", "fastapi", "django", "flask", "sqlalchemy", "alembic",
    "postgresql", "mysql", "redis", "celery", "docker", "kubernetes",
    "aws", "s3", "sqs", "rds", "linux", "git", "ci/cd", "javascript",
    "typescript", "react", "nodejs", "html", "css", "rest api", "jwt",
    "nginx", "pytest", "pandas", "numpy", "machine learning", "nlp",
}


def normalize_skill(skill: str) -> str:
    value = skill.lower().strip()
    return SKILL_SYNONYMS.get(value, value)


def _contains_skill(text: str, skill: str) -> bool:
    escaped = re.escape(skill)
    if skill in {"ci/cd", "rest api", "machine learning"}:
        return skill in text
    pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
    return re.search(pattern, text) is not None


def extract_skills(text: str) -> set[str]:
    text_lower = text.lower()
    found: set[str] = set()
    for skill in KNOWN_SKILLS:
        if _contains_skill(text_lower, skill):
            found.add(normalize_skill(skill))
    for alias, canonical in SKILL_SYNONYMS.items():
        if _contains_skill(text_lower, alias):
            found.add(canonical)
    return found


def extract_years_experience(text: str) -> int | None:
    text_lower = text.lower()
    patterns = [
        r"(\d+)\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?experience",
        r"(?:experience|kinh nghiệm).*?(\d+)\+?\s*(?:years|year|năm)",
        r"(\d+)\+?\s*năm\s+kinh\s+nghiệm",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))
    return None


def get_compatibility_level(score: float) -> dict:
    if score >= 85:
        return {
            "level": "Excellent Fit",
            "recommendation": "Strongly Recommend",
            "message": "Ứng viên rất phù hợp với JD.",
        }
    if score >= 70:
        return {
            "level": "Strong Fit",
            "recommendation": "Recommend",
            "message": "Ứng viên phù hợp, có thể đưa vào vòng phỏng vấn.",
        }
    if score >= 55:
        return {
            "level": "Medium Fit",
            "recommendation": "Consider after improvements",
            "message": "Ứng viên có mức phù hợp trung bình, cần kiểm tra thêm.",
        }
    if score >= 40:
        return {
            "level": "Weak Fit",
            "recommendation": "Not priority",
            "message": "Ứng viên còn thiếu nhiều yêu cầu quan trọng.",
        }
    return {
        "level": "Not Recommended",
        "recommendation": "Reject",
        "message": "CV chưa phù hợp với JD hiện tại.",
    }


def calculate_keyword_score(cv_text: str, jd_text: str) -> float:
    jd_words = set(re.findall(r"[a-zA-Z]{3,}", jd_text.lower()))
    if not jd_words:
        return 0.0
    cv_words = set(re.findall(r"[a-zA-Z]{3,}", cv_text.lower()))
    stopwords = {"the", "and", "for", "with", "that", "this", "from", "have", "are", "was", "will", "can", "not", "you", "your", "our"}
    jd_keywords = jd_words - stopwords
    if not jd_keywords:
        return 0.0
    matched = cv_words & jd_keywords
    return round(len(matched) / len(jd_keywords) * 100, 2)


def calculate_cv_quality(cv_text: str) -> float:
    score = 50.0
    if len(cv_text) > 300:
        score += 10
    if len(cv_text) > 800:
        score += 5
    if re.search(r"\d+%|\d+\s*(users|requests|projects|clients)", cv_text.lower()):
        score += 15
    section_keywords = ["experience", "education", "skills", "projects", "kinh nghiệm", "học vấn", "kỹ năng"]
    sections_found = sum(1 for kw in section_keywords if kw in cv_text.lower())
    score += min(sections_found * 5, 20)
    return min(score, 100.0)


def calculate_matching(cv_text: str, jd_text: str) -> dict:
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = sorted(cv_skills & jd_skills)
    missing_skills = sorted(jd_skills - cv_skills)
    extra_skills = sorted(cv_skills - jd_skills)

    skill_score = round(len(matched_skills) / len(jd_skills) * 100, 2) if jd_skills else 0.0

    candidate_years = extract_years_experience(cv_text)
    required_years = extract_years_experience(jd_text)
    if candidate_years is not None and required_years:
        experience_score = round(min(candidate_years / required_years, 1) * 100, 2)
    else:
        experience_score = 60.0

    education_keywords = ["bachelor", "degree", "university", "computer science", "đại học", "cử nhân"]
    education_score = 100.0 if any(keyword in cv_text.lower() for keyword in education_keywords) else 60.0

    keyword_score = calculate_keyword_score(cv_text, jd_text)
    cv_quality_score = calculate_cv_quality(cv_text)

    overall_score = round(
        skill_score * 0.40
        + experience_score * 0.25
        + education_score * 0.15
        + keyword_score * 0.10
        + cv_quality_score * 0.10,
        2,
    )

    compatibility = get_compatibility_level(overall_score)

    return {
        "matching_score": overall_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "keyword_score": keyword_score,
        "cv_quality_score": cv_quality_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "candidate_years": candidate_years,
        "required_years": required_years,
        "compatibility": compatibility,
        "score_breakdown": {
            "skill_match": {
                "score": skill_score,
                "weight": 40,
                "description": "Mức độ khớp kỹ năng giữa CV và JD",
            },
            "experience_match": {
                "score": experience_score,
                "weight": 25,
                "description": "Mức độ phù hợp về kinh nghiệm làm việc",
            },
            "education_match": {
                "score": education_score,
                "weight": 15,
                "description": "Mức độ phù hợp về học vấn",
            },
            "keyword_match": {
                "score": keyword_score,
                "weight": 10,
                "description": "Mức độ khớp các từ khóa quan trọng trong JD",
            },
            "cv_quality": {
                "score": cv_quality_score,
                "weight": 10,
                "description": "Chất lượng trình bày và mức độ rõ ràng của CV",
            },
        },
    }
