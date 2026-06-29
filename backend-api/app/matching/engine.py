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
    "c#": "csharp",
    "c sharp": "csharp",
    ".net": "dotnet",
    "asp.net": "dotnet",
    "vue.js": "vuejs",
    "vue js": "vuejs",
    "angular.js": "angular",
    "react.js": "react",
    "react js": "react",
    "spring boot": "spring",
    "pl/sql": "plsql",
    "pl sql": "plsql",
    "t-sql": "tsql",
    "ms sql": "mssql",
    "sql server": "mssql",
    "mongo db": "mongodb",
    "no sql": "nosql",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "ci/cd": "ci/cd",
    "ci cd": "ci/cd",
    "rest api": "rest api",
    "restful api": "rest api",
    "restful": "rest api",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "elk stack": "elk",
    "elastic stack": "elk",
    "elasticsearch": "elk",
}

KNOWN_SKILLS = {
    # Programming languages
    "python", "java", "javascript", "typescript", "csharp", "c/c++",
    "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "lua", "dart", "elixir", "haskell",
    # Web frameworks
    "fastapi", "django", "flask", "spring", "dotnet", "react",
    "angular", "vuejs", "nodejs", "express", "nextjs", "nuxtjs",
    "laravel", "rails", "sinatra", "gin", "fiber",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "oracle", "mssql",
    "plsql", "tsql", "nosql", "mariadb", "couchdb",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
    "ansible", "jenkins", "gitlab", "github actions", "ci/cd",
    "linux", "nginx", "apache", "helm", "prometheus", "grafana",
    # Data & AI
    "machine learning", "deep learning", "nlp", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "spark",
    "hadoop", "airflow", "dbt", "tableau", "power bi",
    "random forest", "neural network", "computer vision",
    # Security
    "cybersecurity", "penetration testing", "siem", "wireshark",
    "wazuh", "nessus", "burp suite", "metasploit", "nmap",
    "owasp", "firewall", "ids", "ips", "soc", "threat detection",
    "log analysis", "vulnerability assessment", "incident response",
    "encryption", "ssl", "tls", "vpn", "network security",
    # Enterprise & Management
    "sap", "erp", "crm", "salesforce", "jira", "confluence",
    "sdlc", "agile", "scrum", "kanban", "waterfall",
    "project management", "itil", "devops",
    # General
    "git", "rest api", "graphql", "grpc", "microservices",
    "jwt", "oauth", "html", "css", "sass", "webpack",
    "sqlalchemy", "alembic", "celery", "rabbitmq", "kafka",
    "pytest", "junit", "selenium", "cypress",
    "s3", "sqs", "rds", "lambda", "ec2",
    "vmware", "virtualbox", "vagrant",
}

# Role levels for detecting seniority mismatch
ROLE_LEVELS = {
    "intern": {"intern", "internship", "thực tập", "fresher", "trainee", "junior"},
    "junior": {"junior", "associate", "entry level", "entry-level", "1-2 years"},
    "mid": {"mid", "middle", "intermediate", "3-5 years", "engineer", "developer"},
    "senior": {"senior", "lead", "principal", "staff", "architect", "7+ years", "5+ years"},
    "manager": {"manager", "director", "head", "chief", "vp", "vice president",
                "team lead", "tech lead", "quản lý", "trưởng phòng", "giám đốc"},
}

# Domain categories for detecting domain mismatch (universal - all industries)
DOMAIN_KEYWORDS = {
    # IT & Technology
    "cybersecurity": {"cybersecurity", "security", "siem", "threat", "vulnerability",
                      "penetration", "soc", "incident response", "malware", "forensic",
                      "firewall", "ids", "ips", "wireshark", "nmap", "burp suite",
                      "owasp", "encryption", "an ninh mạng", "bảo mật"},
    "web_development": {"react", "angular", "vue", "frontend", "backend", "fullstack",
                        "full-stack", "web development", "html", "css", "javascript",
                        "nodejs", "api", "rest", "graphql", "web developer"},
    "data_science": {"data science", "machine learning", "deep learning", "ai",
                     "artificial intelligence", "nlp", "computer vision", "tensorflow",
                     "pytorch", "data analysis", "statistics", "data scientist"},
    "devops": {"devops", "cloud", "aws", "azure", "gcp", "kubernetes", "docker",
               "terraform", "ci/cd", "infrastructure", "deployment", "sre",
               "cloud engineer", "site reliability"},
    "mobile": {"mobile", "ios", "android", "flutter", "react native", "swift",
               "kotlin", "mobile app", "ứng dụng di động", "mobile developer"},
    "enterprise_it": {"sap", "erp", "crm", "oracle", "plsql", "it manager",
                      "it director", "enterprise", "vendor", "stakeholder",
                      "business requirements", "help desk", "it projects",
                      "it infrastructure", "it operations"},
    "database": {"database", "dba", "sql", "oracle", "postgresql", "mysql",
                 "mongodb", "data modeling", "data warehouse", "etl", "data engineer"},
    # Business & Management
    "marketing": {"marketing", "digital marketing", "seo", "sem", "content marketing",
                  "social media", "brand", "campaign", "ads", "advertising",
                  "market research", "email marketing", "influencer", "pr",
                  "public relations", "google ads", "facebook ads", "analytics",
                  "tiếp thị", "quảng cáo", "truyền thông"},
    "sales": {"sales", "b2b", "b2c", "revenue", "pipeline", "crm", "negotiation",
              "account management", "business development", "lead generation",
              "quota", "territory", "closing", "prospecting", "client acquisition",
              "bán hàng", "kinh doanh", "doanh thu"},
    "human_resources": {"human resources", "hr", "recruitment", "hiring", "talent",
                        "onboarding", "employee relations", "compensation", "benefits",
                        "payroll", "performance management", "training", "development",
                        "labor law", "nhân sự", "tuyển dụng", "đào tạo"},
    "finance": {"finance", "accounting", "financial analysis", "budgeting", "forecasting",
                "audit", "tax", "investment", "banking", "portfolio", "risk management",
                "financial reporting", "compliance", "tài chính", "kế toán", "kiểm toán"},
    "operations": {"operations", "supply chain", "logistics", "procurement", "inventory",
                   "warehouse", "manufacturing", "production", "quality control",
                   "lean", "six sigma", "process improvement", "vận hành", "sản xuất"},
    "project_management": {"project management", "pmp", "scrum master", "agile",
                           "waterfall", "sprint", "backlog", "stakeholder management",
                           "risk management", "milestone", "deliverable", "gantt",
                           "quản lý dự án"},
    # Specialized Industries
    "healthcare": {"healthcare", "medical", "clinical", "patient", "hospital",
                   "nursing", "pharmacy", "diagnosis", "treatment", "physician",
                   "surgeon", "therapist", "health", "y tế", "bệnh viện", "bác sĩ"},
    "education": {"education", "teaching", "curriculum", "student", "classroom",
                  "pedagogy", "assessment", "learning", "instructor", "professor",
                  "academic", "school", "university", "giáo dục", "giảng dạy"},
    "legal": {"legal", "law", "attorney", "lawyer", "litigation", "contract",
              "compliance", "regulatory", "intellectual property", "corporate law",
              "dispute", "court", "luật", "pháp lý", "hợp đồng"},
    "design": {"design", "ui", "ux", "graphic design", "figma", "sketch", "adobe",
               "photoshop", "illustrator", "user experience", "user interface",
               "wireframe", "prototype", "thiết kế"},
    "construction": {"construction", "civil engineering", "structural", "autocad",
                     "building", "site supervision", "safety compliance", "contractor",
                     "architecture", "blueprint", "xây dựng", "kiến trúc"},
    "hospitality": {"hospitality", "hotel", "restaurant", "tourism", "travel",
                    "customer service", "front desk", "reservation", "event planning",
                    "food service", "khách sạn", "du lịch", "nhà hàng"},
    "real_estate": {"real estate", "property", "broker", "listing", "appraisal",
                    "mortgage", "lease", "tenant", "commercial property",
                    "bất động sản", "môi giới"},
}


def normalize_skill(skill: str) -> str:
    value = skill.lower().strip()
    return SKILL_SYNONYMS.get(value, value)


def _contains_skill(text: str, skill: str) -> bool:
    escaped = re.escape(skill)
    if skill in {"ci/cd", "rest api", "machine learning", "deep learning",
                 "c/c++", "log analysis", "threat detection", "incident response",
                 "vulnerability assessment", "penetration testing", "network security",
                 "project management", "github actions", "power bi", "random forest",
                 "neural network", "computer vision", "burp suite", "elk stack"}:
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


def detect_role_level(text: str) -> str:
    """Detect the seniority/role level from text."""
    text_lower = text.lower()
    scores = {}
    for level, keywords in ROLE_LEVELS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            scores[level] = count

    if not scores:
        return "unknown"
    return max(scores, key=scores.get)


def detect_domains(text: str) -> list[str]:
    """Detect which domains/fields are mentioned in text."""
    text_lower = text.lower()
    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count >= 2:
            domains.append(domain)
    return domains


def calculate_role_compatibility(cv_level: str, jd_level: str) -> float:
    """Calculate compatibility between CV role level and JD role level."""
    level_order = ["intern", "junior", "mid", "senior", "manager"]

    if cv_level == "unknown" or jd_level == "unknown":
        return 60.0

    if cv_level not in level_order or jd_level not in level_order:
        return 60.0

    cv_idx = level_order.index(cv_level)
    jd_idx = level_order.index(jd_level)
    diff = abs(cv_idx - jd_idx)

    if diff == 0:
        return 100.0
    elif diff == 1:
        return 70.0
    elif diff == 2:
        return 40.0
    elif diff == 3:
        return 20.0
    else:
        return 5.0


def calculate_domain_compatibility(cv_domains: list[str], jd_domains: list[str]) -> float:
    """Calculate compatibility between CV domains and JD domains."""
    if not cv_domains or not jd_domains:
        return 50.0

    cv_set = set(cv_domains)
    jd_set = set(jd_domains)

    overlap = cv_set & jd_set
    if overlap:
        return round(len(overlap) / len(jd_set) * 100, 2)
    return 10.0


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
    stopwords = {"the", "and", "for", "with", "that", "this", "from", "have",
                 "are", "was", "will", "can", "not", "you", "your", "our",
                 "his", "her", "its", "they", "them", "their", "all", "any",
                 "each", "every", "both", "few", "more", "most", "other"}
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
    section_keywords = ["experience", "education", "skills", "projects",
                        "kinh nghiệm", "học vấn", "kỹ năng", "certificate",
                        "chứng chỉ", "dự án"]
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
        experience_score = 50.0  # unknown = neutral, not "medium fit"

    education_keywords = ["bachelor", "degree", "university", "computer science",
                          "đại học", "cử nhân", "master", "phd", "thạc sĩ", "tiến sĩ"]
    education_score = 100.0 if any(keyword in cv_text.lower() for keyword in education_keywords) else 50.0

    keyword_score = calculate_keyword_score(cv_text, jd_text)
    cv_quality_score = calculate_cv_quality(cv_text)

    # Role level analysis
    cv_role_level = detect_role_level(cv_text)
    jd_role_level = detect_role_level(jd_text)
    role_compatibility = calculate_role_compatibility(cv_role_level, jd_role_level)

    # Domain analysis
    cv_domains = detect_domains(cv_text)
    jd_domains = detect_domains(jd_text)
    domain_compatibility = calculate_domain_compatibility(cv_domains, jd_domains)

    # Weighted overall score (optimized weights)
    # Skill + Role + Domain = 70% (most decisive factors)
    # Experience + Education + Keyword + CV Quality = 30% (supporting factors)
    overall_score = round(
        skill_score * 0.35
        + role_compatibility * 0.20
        + domain_compatibility * 0.15
        + experience_score * 0.15
        + education_score * 0.05
        + keyword_score * 0.05
        + cv_quality_score * 0.05,
        2,
    )

    # Score cap rules: prevent inflated scores when critical mismatches exist
    if role_compatibility <= 20 and domain_compatibility <= 20:
        overall_score = min(overall_score, 35.0)
    elif role_compatibility <= 20 or domain_compatibility <= 20:
        overall_score = min(overall_score, 45.0)
    if skill_score <= 20 and domain_compatibility <= 30:
        overall_score = min(overall_score, 40.0)

    compatibility = get_compatibility_level(overall_score)

    return {
        "matching_score": overall_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "keyword_score": keyword_score,
        "cv_quality_score": cv_quality_score,
        "role_compatibility": role_compatibility,
        "domain_compatibility": domain_compatibility,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "candidate_years": candidate_years,
        "required_years": required_years,
        "cv_role_level": cv_role_level,
        "jd_role_level": jd_role_level,
        "cv_domains": cv_domains,
        "jd_domains": jd_domains,
        "compatibility": compatibility,
        "score_breakdown": {
            "skill_match": {
                "score": skill_score,
                "weight": 35,
                "description": "Mức độ khớp kỹ năng giữa CV và JD",
            },
            "role_match": {
                "score": role_compatibility,
                "weight": 20,
                "description": f"Mức độ phù hợp cấp bậc ({cv_role_level} vs {jd_role_level})",
            },
            "domain_match": {
                "score": domain_compatibility,
                "weight": 15,
                "description": "Mức độ phù hợp lĩnh vực chuyên môn",
            },
            "experience_match": {
                "score": experience_score,
                "weight": 15,
                "description": "Mức độ phù hợp về kinh nghiệm làm việc",
            },
            "education_match": {
                "score": education_score,
                "weight": 5,
                "description": "Mức độ phù hợp về học vấn",
            },
            "keyword_match": {
                "score": keyword_score,
                "weight": 5,
                "description": "Mức độ khớp các từ khóa quan trọng trong JD",
            },
            "cv_quality": {
                "score": cv_quality_score,
                "weight": 5,
                "description": "Chất lượng trình bày và mức độ rõ ràng của CV",
            },
        },
    }
